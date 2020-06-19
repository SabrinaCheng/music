import sys
from kafka import KafkaConsumer
# from json import loads
import redis

password = sys.argv[1]

r = redis.Redis(
    host='ec2-34-219-119-131.us-west-2.compute.amazonaws.com',
    port=6379 , 
    password=password)

print(r.get('test'))

# consumer = KafkaConsumer(
#     'test',
#      bootstrap_servers=['10.0.0.7:9092'],
#      auto_offset_reset='earliest',
#      enable_auto_commit=True,
#     #  group_id='my-group',
#     #  value_deserializer=lambda x: loads(x.decode('utf-8'))
#      )

# for message in consumer:
#     message = message.value
#     print(message)