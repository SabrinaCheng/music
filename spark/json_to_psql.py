from pyspark.sql import SparkSession

spark = SparkSession\
    .builder\
    .appName("test")\
    .getOrCreate()
# print(spark)

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

lines = spark.read.text(h5_file.rdd.map(lambda r: r[0])
# counts = lines.flatMap(lambda x: x.split(' ')) \
#               .map(lambda x: (x, 1)) \
#               .reduceByKey(add)
# output = counts.collect()
# for (word, count) in output:
#     print("%s: %i" % (word, count))
# peopleDF = spark.read.json("examples/src/main/resources/people.json")

# DataFrames can be saved as Parquet files, maintaining the schema information.
# peopleDF.write.parquet("people.parquet")

# Read in the Parquet file created above.
# Parquet files are self-describing so the schema is preserved.
# The result of loading a parquet file is also a DataFrame.
# parquetFile = spark.read.parquet("people.parquet")

# Parquet files can also be used to create a temporary view and then used in SQL statements.
# parquetFile.createOrReplaceTempView("parquetFile")
# teenagers = spark.sql("SELECT name FROM parquetFile WHERE age >= 13 AND age <= 19")
# teenagers.show()
                        
                        
spark.stop()