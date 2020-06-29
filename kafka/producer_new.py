# import sys
import boto3
from smart_open import open
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
from datetime import datetime
import sched, time

TOPIC = 't_0628'

"""simulate streaming and send to kafka topic"""

def send_message(msg):
    """send message to topic"""
    try: 
        producer.send(TOPIC, value=msg)
    except KafkaError as e:
        print(e)

if __name__ == "__main__":

    # set up kafka producer
    bootstrap_servers = '10.0.0.7:9092'
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                            value_serializer=lambda x: 
                            json.dumps(x).encode('utf-8')
                            )


    # simulate stream
    init_ts = int(time.time())
    s = sched.scheduler(time.time, time.sleep)

    # walk through dir and get all fitrec json files
    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket('fitrec')
    for object_summary in my_bucket.objects.filter(Prefix="proper/endomondoHR_proper_tenminutes.json/"):
        if object_summary.key.endswith('.json'):
            print(object_summary.key)
            input_json_path = 's3://fitrec/' + object_summary.key
            for line in open(input_json_path, 'rb'):
                row = json.loads(line.decode('utf8'))
                delta_ts = row['new_time']
                row['new_time'] += init_ts
                print(row)
                s.enter(delta_ts, 0, send_message, kwargs={'msg': row})
    s.run()


    producer.flush()