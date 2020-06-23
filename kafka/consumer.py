import sys
from kafka import KafkaConsumer
import redis
import json
import logging

# tracking interval: 60 sec
TRACKING_INTERVAL = 60
# heart rate normal range: 30 - 220 beats per minute (bpm)
MAX_HEART_RATE = 220
MIN_HEART_RATE = 30

def add_record(dict_data, ts, wid, uid, hr):
    dict_data['id'] = wid
    dict_data['hr'] = [hr]
    dict_data['ts'] = [ts]
    dict_data['avg_hr'] = [hr]
    return dict_data

def update_record(dict_data, ts, wid, uid, hr):
    while ts - dict_data['ts'][0] > TRACKING_INTERVAL:
        dict_data['ts'].pop(0)
        dict_data['hr'].pop(0)
        dict_data['avg_hr'].pop(0)
    dict_data['ts'].append(ts)
    dict_data['hr'].append(hr)
    dict_data['avg_hr'].append(round(sum(dict_data['hr']) / (len(dict_data['hr'])), 2))
    return dict_data

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Please enter Redis password and Kafka topic')

    password = sys.argv[1]
    topic = sys.argv[2]

    # connect to Kafka
    consumer = KafkaConsumer(
        topic,
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
        print(ts, wid, uid, hr)
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
        print('======', uid, json.dumps(user_data))
        r.set(uid, json.dumps(user_data))


