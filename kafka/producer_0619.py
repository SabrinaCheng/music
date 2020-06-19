# from smart_open import smart_open
from smart_open import open
# import boto3
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
        producer.send('test', value=msg)
    except KafkaError as e:
        print(e)


input_json_path = 's3://fitrec/proper/endomondoHR_proper_ready.json/part-00000-11b9df76-54cc-403e-b60f-7644e6f546a4-c000.json'

first_line = True
init_ts = int(time.time())
print(init_ts)
s = sched.scheduler(time.time, time.sleep)
i = 0
for line in open(input_json_path, 'rb'):
    row = json.loads(line.decode('utf8'))
    if first_line:
        original_init_ts = row['timestamp']
        first_line = False
    print(row)
    new_ts = row['timestamp'] - original_init_ts + init_ts
    delta_ts = row['timestamp'] - original_init_ts
    # print(row['timestamp'], str(datetime.fromtimestamp(row['timestamp'])))
    # print(new_ts, str(datetime.fromtimestamp(new_ts)))
    row['timestamp'] = new_ts
    s.enter(delta_ts, 0, send_message, kwargs={'msg': row})
    s.run()
    i += 1
    if i == 10:
        break

# data = []
# first_line = True
# init_ts = time.time()
# i = 0
# with open(input_json_path) as f:
#     for l in f:
#         line = eval(l)
#         if first_line:
#             original_init_ts = line['timestamp']
#             first_line = False
#         timestamp = line['timestamp'] - init_ts
#         # message = {'userId': userId, 'timestamp': str(datetime.fromtimestamp(t)), 'heart_rate': h}
#         s.enter(timestamp, 1, send_message, kwargs={'a': 'line'})
#         s.run()

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