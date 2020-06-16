from kafka import KafkaProducer
from kafka.errors import KafkaError
from json import dumps

bootstrap_servers = '10.0.0.7:9092'

producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                        value_serializer=lambda x: 
                         dumps(x).encode('utf-8')
                        )

print('ss')

for e in range(10):
    data = {'number' : e}
    producer.send('test', value=data)

# for i in range(3):
#     data = {'num': i}
#     try: 
#         producer.send('test', value=data.encode('utf-8'))
#     except KafkaError as e:
#         print(e)

print('sss')

producer.flush()