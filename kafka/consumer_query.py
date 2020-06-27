import sys
from kafka import KafkaConsumer
import redis
import json
from psycopg2 import connect, Error
from psycopg2.extras import execute_values
import time

BUFFER = 5
SEC_TOPIC = 't2_0626'


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Please enter Redis and PosrgreSQL password')

    redis_password = sys.argv[1]
    psql_password = sys.argv[2]

    # set up Kafka　consumer
    consumer = KafkaConsumer(
        SEC_TOPIC,
        bootstrap_servers=['10.0.0.7:9092'],
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')), 
        enable_auto_commit=True,
        )

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
            uid = message.value
            print(uid)
            user_data = r.get(uid)
            user_data = json.loads(user_data.decode('utf-8'))
            
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
            print(next_song)

            # prepare hashmap for redis
            user_data['music_end_time'] = user_data['ts'][-1] + round(float(next_song[4]) + BUFFER, 0)
            user_data['song_id'].append(next_song[0])
            user_data['title'].append(next_song[1])
            user_data['song_hotttnesss'].append(str(next_song[3]))
            user_data['artist_name'].append(next_song[2])
            user_data['tempo'].append(str(next_song[5]))
            user_data['duration'].append(str(next_song[4]))

            # # add or update to redis
            r.set(uid, json.dumps(user_data))

