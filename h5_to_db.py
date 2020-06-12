import sys
from pyspark.sql import SparkSession
import boto3
import tables
import collections
import time

if __name__ == "__main__":

    # initial spark session
    spark = SparkSession\
        .builder\
        .appName("h5_to_postgresql")\
        .getOrCreate()
    print(spark)
    print('=============================', end='\n')

    # print all file names in s3 bucket
    #s3 = boto3.resource('s3')
    #my_bucket = s3.Bucket('pymillionsong')
    #for object_summary in my_bucket.objects.filter(Prefix="data/"):
    #    print(object_summary.key)


    def get_song(file_name):
        '''read h5 and store data in dict'''
        start_t = time.time()
        h5 = tables.open_file(file_name, mode='r')
        data = collections.defaultdict()
        path = h5.root
        for leaf in path._f_walknodes('Leaf'):
            if 'Table' in str(leaf):
                group, table = str(leaf)[1:].split('(')[0].split('/')
                for name in eval('h5.root.' + group + '.' + table + '.colnames'):
                    data[name] = eval('h5.root.' + group + '.' + table + '.cols.' + name + '[0]')
            else:
                group, arr = str(leaf)[1:].split('(', 1)[0].split('/')
                data[arr] = list(eval('h5.root.' + group + '.' + arr + '[:]'))
        h5.close()
        print('Time used: ', time.time() - start_t)
        return data

   # before read all files, try just one h5 and pass the h5 to get_song()
    # case 1: local file -> ok
    #local_file = 'TRAAAAK128F9318786.h5'
    #song_data = get_song(local_file)
    #print(song_data.keys())

    # case 2: h5 in s3 -> fail
    #bucket = 'pymillionsong'
    #key = 'data/A/A/A/TRAAAAK128F9318786.h5'
    #s3 = boto3.resource('s3')
    #obj = s3.Object(bucket, key)
    #obj.get()['Body'].read()
    #print(obj)
    #song_data = get_song(obj)

    # case 3 -> fail
    s3 = boto3.client('s3')
    h5_file = s3.get_object(Bucket='pymillionsong', Key='data/A/A/A/TRAAAAK128F9318786.h5')['Body'].read().decode('ascii')
    print(h5_file)
    song_data = get_song(h5_file)


    spark.stop()