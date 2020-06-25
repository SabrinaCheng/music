import sys
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import redis
import json

# tracking interval: 60 sec
TRACKING_INTERVAL = 60
# heart rate normal range: 30 - 220 beats per minute (bpm)
MAX_HEART_RATE = 220
MIN_HEART_RATE = 30
# RECOMMENDATION WINDOW
WINDOW = 3

def add_record(dict_data, ts, wid, uid, hr):
    dict_data['id'] = wid
    dict_data['hr'] = [hr]
    dict_data['ts'] = [ts]
    dict_data['avg_hr'] = [hr]
    dict_data['music_end_time'] = ts
    dict_data['song_id'] = []
    dict_data['title'] = []
    dict_data['song_hotttnesss'] = []
    dict_data['artist_name'] = []
    dict_data['tempo'] = []
    dict_data['duration'] = []
    return dict_data

def update_record(dict_data, ts, wid, uid, hr):
    while len(dict_data['ts']) > 0 and ts - dict_data['ts'][0] > TRACKING_INTERVAL:
        dict_data['ts'].pop(0)
        dict_data['hr'].pop(0)
        dict_data['avg_hr'].pop(0)
    dict_data['ts'].append(ts)
    dict_data['hr'].append(hr)
    dict_data['avg_hr'].append(round(sum(dict_data['hr']) / (len(dict_data['hr'])), 2))
    return dict_data

def send_message(topic, msg):
    """send message to topic"""
    try: 
        producer.send(topic, value=msg)
    except KafkaError as e:
        print(e)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Please enter Redis password')

    password = sys.argv[1]

    # set up Kafka producer
    bootstrap_servers = '10.0.0.7:9092'
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                            value_serializer=lambda x: 
                            json.dumps(x).encode('utf-8')
                            )

    # set up Kafka　consumer
    consumer = KafkaConsumer(
        'raw_hr',
        bootstrap_servers=['10.0.0.7:9092'],
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')), 
        enable_auto_commit=True,
        )

    # connect to Redis
    r = redis.Redis(
        host='ec2-34-219-119-131.us-west-2.compute.amazonaws.com',
        port=6379, 
        password=password)

    # process message from Kafka
    for message in consumer:
        message = message.value
        ts, wid, uid, hr = message.values()
        # check heart rate within normal range
        if MIN_HEART_RATE <= hr <= MAX_HEART_RATE:
            
            # check user exists or not
            user_data = r.get(uid)
            print(uid, user_data)
            
            # existing user
            if user_data:
                user_data = json.loads(user_data)
                # new workout for both existing and new users
                if user_data['id'] != wid:
                    add_record(user_data, ts, wid, uid, hr)
                # same workout, new hr
                else:
                    update_record(user_data, ts, wid, uid, hr)

            else: # user doesn't exist
                # add new user
                user_data = {}
                add_record(user_data, ts, wid, uid, hr)

        # add or update to redis
        # key is uid, value consists of workoutid(wid), timestamp list(ts), heartrate list(hr), avghr, musicendtime
        # song_id, title(metadata), song_hotttnesss(metadata), artist_name(metadata), tempo(analysis), duration(analysis)
        r.set(uid, json.dumps(user_data))

        # send message to query_song topic if the user needs next song
        if user_data['music_end_time'] <= ts:
            send_message('query_song', uid)
        
    producer.flush()
