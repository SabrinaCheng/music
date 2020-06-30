import sys
from kafka import KafkaConsumer, TopicPartition
from kafka.errors import KafkaError
import redis
import json
from psycopg2 import connect, Error
from psycopg2.extras import execute_values
import time

# tracking interval: 60 sec
TRACKING_INTERVAL = 60
# heart rate normal range: 30 - 220 beats per minute (bpm)
MAX_HEART_RATE = 220
MIN_HEART_RATE = 30
# RECOMMENDATION BUFFER
BUFFER = 5 

TOPIC = 'test_n3'


def create_record(dict_data, ts, wid, uid, hr):
    dict_data['uid'] = uid
    dict_data['wid'] = wid
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


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Please enter Redis password, PostgreSQL password, and Kafka topic partition')

    redis_password = sys.argv[1]
    psql_password = sys.argv[2]
    # partition = sys.argv[3]

    # set up Kafka　consumer
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=['10.0.0.7:9092'],
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')), 
        enable_auto_commit=True,
        group_id='1'
        )
    # topic_partition = TopicPartition(TOPIC, partition)
    # consumer.assign([topic_partition])

    # connect to Redis
    r = redis.Redis(
        host='ec2-34-219-119-131.us-west-2.compute.amazonaws.com',
        port=6379, 
        password=redis_password)

    # connect to psql
    try:
        conn = connect(dbname = 'songs',
                        user = 'pyadmin',
                        host = '10.0.0.6',
                        password = psql_password,
                        port = 5431,
                        connect_timeout = 5
                        )

        cur = conn.cursor()
        print ("\nCreated cursor object:", cur)

    except (Exception, Error) as err:
        print ("\npsycopg2 connect error:", err)
        conn = None
        cur = None
    
    # only attempt to execute SQL if cursor is valid
    if cur != None:
        # process message from Kafka
        for message in consumer:
            print('p', message.partition)
            message = message.value
            ts, wid, uid, hr = message.values()
            # check heart rate within normal range
            if MIN_HEART_RATE <= hr <= MAX_HEART_RATE:
                
                # check user exists or not
                user_data = r.get(wid)
                print(wid, user_data)
                
                # existing workout
                if user_data:
                    user_data = json.loads(user_data)
                    update_record(user_data, ts, wid, uid, hr)
                else: # workout doesn't exist
                    # add new record
                    user_data = {}
                    create_record(user_data, ts, wid, uid, hr)

            # add or update to redis
            # key is wid, value consists of uid, workoutid(wid), timestamp list(ts), heartrate list(hr), avghr, musicendtime
            # song_id, title(metadata), song_hotttnesss(metadata), artist_name(metadata), tempo(analysis), duration(analysis)
            r.set(wid, json.dumps(user_data))

            # send message to query_song topic if the user needs next song
            if user_data['music_end_time'] <= ts:
                
                # determin upper and lower bound of tempo
                tempo_min, tempo_max = 0.95 * user_data['avg_hr'][-1], 1.05 * user_data['avg_hr'][-1]
                
                start_t = time.time()
                
                # opitimized query
                query = "SELECT m.song_id, m.title, m.artist_name, m.song_hotttnesss, a.duration, a.tempo \
                        FROM metadata m RIGHT JOIN (SELECT song_id, tempo, duration \
                                                    FROM analysis \
                                                    WHERE tempo BETWEEN {} AND {} \
                                                    ORDER BY RANDOM() LIMIT 1000) a \
                                        ON m.song_id = a.song_id \
                        WHERE m.song_hotttnesss BETWEEN 0.75 AND 1 \
                        ORDER BY m.song_hotttnesss DESC LIMIT 1;".format(tempo_min, tempo_max)

                cur.execute(query)
                print('Time used: ', time.time() - start_t)
                next_song = cur.fetchone()

                # prepare hashmap for redis
                user_data['music_end_time'] = user_data['ts'][-1] + round(float(next_song[4]) + BUFFER, 0)
                user_data['song_id'].append(next_song[0])
                user_data['title'].append(next_song[1])
                user_data['song_hotttnesss'].append(str(next_song[3]))
                user_data['artist_name'].append(next_song[2])
                user_data['tempo'].append(str(next_song[5]))
                user_data['duration'].append(str(next_song[4]))

                # add or update to redis
                r.set(wid, json.dumps(user_data))
                
