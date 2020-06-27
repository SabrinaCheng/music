# import sys
from smart_open import open
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
from datetime import datetime
import sched, time

TOPIC = 't1_0626'

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
    # read fitrec json file
    input_json_path = 's3://fitrec/proper/endomondoHR_proper_ready.json/part-00001-11b9df76-54cc-403e-b60f-7644e6f546a4-c000.json'
    # simulate stream
    first_line = True
    init_ts = int(time.time())
    s = sched.scheduler(time.time, time.sleep)
    for line in open(input_json_path, 'rb'):
        row = json.loads(line.decode('utf8'))
        if first_line:
            original_init_ts = row['timestamp']
            first_line = False
        new_ts = row['timestamp'] - original_init_ts + init_ts
        delta_ts = row['timestamp'] - original_init_ts
        row['timestamp'] = new_ts
        print(row)
        s.enter(delta_ts, 0, send_message, kwargs={'msg': row})
    s.run()


    producer.flush()