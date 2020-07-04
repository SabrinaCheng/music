import sys
import os
import json
from psycopg2 import connect, Error
# from psycopg2.extras import execute_values
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Please indicate Postgresql password')

    password = sys.argv[1]

    # connect to psql
    try:
        conn = connect(dbname = 'songs',
                        user = 'pyadmin',
                        host = 'localhost',
                        password = password,
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

        avg_hrs = list(range(90, 190, 10))
        t1, t2, t3, t4 = [], [], [], []
        for avg_hr in avg_hrs:

            # case 1, normalization
            tempo_min, tempo_max = 0.9 * avg_hr, 1.1 * avg_hr
            case1_start_time = time.time()
            query1 = "SELECT song_id, title, artist_name, song_hotness, duration, tempo \
                            FROM needed \
                            WHERE tempo BETWEEN {} AND {} \
                            ORDER BY RANDOM() LIMIT 1;".format(tempo_min, tempo_max)

            cur.execute(query1)
            # print('case 1 time used: ', time.time() - case1_start_time)
            t1.append(time.time() - case1_start_time)
            # next_song = cur.fetchone()
            # print(next_song)

            # case 2, subquery of analysis
            case2_start_time = time.time()
            query2 = "SELECT m.song_id, m.title, m.artist_name, m.song_hotttnesss, a.duration, a.tempo \
                            FROM metadata m RIGHT JOIN (SELECT song_id, tempo, duration \
                                                        FROM analysis \
                                                        WHERE tempo BETWEEN {} AND {} \
                                                        ORDER BY RANDOM() LIMIT 1000) a \
                                            ON m.song_id = a.song_id \
                            ORDER BY m.song_hotttnesss DESC LIMIT 1;".format(tempo_min, tempo_max)

            cur.execute(query2)
            # print('case 2 time used: ', time.time() - case2_start_time)
            t2.append(time.time() - case2_start_time)
            # next_song = cur.fetchone()
            # print(next_song)

            # case 3, subquery of metadata
            case3_start_time = time.time()
            query3 = "SELECT m.song_id, m.title, m.artist_name, m.song_hotttnesss, a.duration, a.tempo \
                            FROM analysis a RIGHT JOIN (SELECT song_id, title, artist_name, song_hotttnesss \
                                                        FROM metadata \
                                                        ORDER BY song_hotttnesss DESC LIMIT 1000) m \
                                            ON a.song_id = m.song_id \
                            WHERE a.tempo BETWEEN {} AND {} \
                            ORDER BY RANDOM() LIMIT 1;".format(tempo_min, tempo_max)

            cur.execute(query3)
            # print('case 3 time used: ', time.time() - case3_start_time)
            t3.append(time.time() - case3_start_time)
            # next_song = cur.fetchone()
            # print(next_song)

            # case 4, direct join
            case4_start_time = time.time()
            query4 = "SELECT m.song_id, m.title, m.artist_name, m.song_hotttnesss, a.duration, a.tempo \
                            FROM analysis a JOIN metadata m \
                                ON a.song_id = m.song_id \
                            WHERE a.tempo BETWEEN {} AND {} \
                            ORDER BY RANDOM() LIMIT 1;".format(tempo_min, tempo_max)

            cur.execute(query4)
            # print('case 4 time used: ', time.time() - case4_start_time)
            t4.append(time.time() - case4_start_time)
            # next_song = cur.fetchone()
            # print(next_song)

    print(t1)
    print(t2)
    print(t3)
    print(t4)

                
    # close the cursor and connection
    cur.close()
    conn.close()