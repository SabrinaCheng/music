import boto3
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
from datetime import datetime
import sched, time

bootstrap_servers = '10.0.0.7:9092'
min_time = 1143392301 #2006-03-26 11:58:21
max_time = 1554629756 #2019-04-07 05:35:56

producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                         value_serializer=lambda x: 
                         json.dumps(x).encode('utf-8')
                        )


def send_message(msg):
    try: 
        producer.send('test', value=msg.encode('utf-8'))
    except KafkaError as e:
        print(e)


# input_json_path = '../../music_l_data/endomondoHR_proper.json'
input_json_path = 's3://fitrec/endomondoHR_proper_ready.json/part-00000-11b9df76-54cc-403e-b60f-7644e6f546a4-c000.json'

# data = []
first_line = True
init_time = time.time()
i = 0
with open(input_json_path) as f:
    for l in f:
        line = eval(l)
        if first_line:
            original_init_ts = line['timestamp']
            first_line = False
        timestamp = line['timestamp'] - init_ts
        message = {'userId': userId, 'timestamp': str(datetime.fromtimestamp(t)), 'heart_rate': h}
        s.enter(timestamp, 1, send_message, kwargs={'a': 'message'})
        s.run()

        # print(line.keys())
        # userId = line['userId']
        # timestamps = line['timestamp']
        # heart_rates = line['heart_rate']
#         for t, h in zip(timestamps, heart_rates):
#             message = {'userId': userId, 'timestamp': str(datetime.fromtimestamp(t)), 'heart_rate': h} #, 'gender': gender, 'sport': sport
            # try: 
            #     producer.send('test', value=message.encode('utf-8'))
            # except KafkaError as e:
            #     print(e)
        # i += 1
        # if i == 3:
        #     break

# s = sched.scheduler(time.time, time.sleep)
# def print_time(a='default'):
#      print("From print_time", datetime.fromtimestamp(time.time()), a)

# def print_some_times():
#      print(time.time())
#      s.enter(10, 1, print_time)
#      s.enter(5, 2, print_time, argument=('positional',))
#      s.enter(5, 1, print_time, kwargs={'a': 'keyword'})
#      s.run()
#      print(time.time())

# print_some_times()

# print(min_time, datetime.fromtimestamp(min_time)) #1143392301 2006-03-26 11:58:21
# print(max_time, datetime.fromtimestamp(max_time)) #1554629756 2019-04-07 05:35:56

producer.flush()