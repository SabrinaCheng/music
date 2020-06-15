import sys
import os
import json
# import psycopg2
from psycopg2 import connect, Error
from psycopg2.extras import execute_values


# psql tables and cols
primary_key = 'metadata/song_id'
analysis_cols = ['track_id', 'bars_start', 'bars_confidence', 'beats_start', 'beats_confidence', \
                'sections_start', 'sections_confidence', 'tatums_start', 'tatums_confidence', \
                'key', 'key_confidence', 'mode', 'mode_confidence', \
                'segments_start', 'segments_confidence', 'segments_loudness_start', 'segments_loudness_max', 'segments_loudness_max_time', \
                'segments_pitches', 'segments_timbre', 'time_signature', 'time_signature_confidence', \
                'analysis_sample_rate', 'audio_md5', 'danceability', 'duration',  'energy', \
                'loudness', 'tempo', 'start_of_fade_out', 'end_of_fade_in']

metadata_cols = ['song_id', 'title', 'song_hotttnesss', 'release', 'release_7digitalid', 'track_7digitalid', \
                'artist_id', 'artist_7digitalid', 'artist_playmeid', 'artist_mbid', 'artist_name', \
                'artist_terms', 'artist_terms_freq', 'artist_terms_weight', 'artist_familiarity', \
                'artist_hotttnesss', 'artist_location', 'artist_longitude', 'artist_latitude', \
                'similar_artists']

musicbrainz_cols = ['artist_mbtags', 'artist_mbtags_count', 'year'] #'genre'


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Please indicate input directory path and Postgresql password')

    input_path = sys.argv[1]
    password = sys.argv[2]

    # walk through input dir and get all file names
    files = []
    for (dir_path, dir_names, file_names) in os.walk(input_path):
        for file_name in file_names:
            if file_name.endswith('.json'):
                files.append(os.sep.join([dir_path, file_name]))
    # print(files)

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
    
        # prepare date to insert to psql
        for f in files:
            with open(f) as json_file:
                songs = json.load(json_file)
                analysis_data = []
                metadata_data = []
                musicbrainz_data = []

                for h5_name, row in songs.items():
                    analysis_data.append(tuple([row[primary_key]] + [row['analysis/' + acol] if row['analysis/' + acol] else None for acol in analysis_cols]))
                    metadata_data.append(tuple([row['metadata/' + mcol] if row['metadata/' + mcol] else None for mcol in metadata_cols]))
                    musicbrainz_data.append(tuple([row[primary_key]] + [row['musicbrainz/' + bcol] if row['musicbrainz/' + bcol] else None for bcol in musicbrainz_cols]))
        
                # insert data to psql 
                try:
                    # insert to analysis
                    execute_values(cur,
                            'INSERT INTO analysis (song_id, track_id, bars_start, bars_confidence, beats_start, beats_confidence, sections_start, sections_confidence, tatums_start, tatums_confidence, key, key_confidence, mode, mode_confidence, segments_start, segments_confidence, segments_loudness_start, segments_loudness_max, segments_loudness_max_time, segments_pitches, segments_timbre, time_signature, time_signature_confidence, analysis_sample_rate, audio_md5, danceability, duration, energy, loudness, tempo, start_of_fade_out, end_of_fade_in) VALUES %s', analysis_data)

                    # insert to metadata
                    execute_values(cur,
                            'INSERT INTO metadata (song_id, title, song_hotttnesss, release, release_7digitalid, track_7digitalid, artist_id, artist_7digitalid, artist_playmeid, artist_mbid, artist_name, artist_terms, artist_terms_freq, artist_terms_weight, artist_familiarity, artist_hotttnesss, artist_location, artist_longitude, artist_latitude, similar_artists) VALUES %s', metadata_data)

                    # insert to musicbrainz
                    execute_values(cur,
                            'INSERT INTO musicbrainz (song_id, artist_mbtags, artist_mbtags_count, year) VALUES %s', musicbrainz_data)

                    #cur.execute( sql_string )
                    conn.commit()
                    print ('\nFinished INSERT INTO execution from {}'.format(f))

                except (Exception, Error) as error:
                    print("\nexecute_sql() error:", error)
                    conn.rollback()

    # close the cursor and connection
    cur.close()
    conn.close()