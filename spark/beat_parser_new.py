import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import size, udf, array, lit, expr, rand, arrays_zip, explode, col
from datetime import datetime

"""parse row fitrec data to kafka procuder message 
with format: timestamp, id, userId, heart_rate"""

# time window: 30 days
TIME_WINDOW = 60 * 24 * 30

if __name__ == "__main__":
    output_file = 's3a://fitrec/proper/endomondoHR_proper_thirtydays'

    # init spark session
    spark = SparkSession\
        .builder\
        .appName("test")\
        .getOrCreate()
    print(spark)

    # read input json
    input_json_path = 's3a://fitrec/proper/endomondoHR_proper.json'
    fitDF = spark.read.json(input_json_path)
    # fitDF.printSchema()
 

    # get beat subset and flatten data 
    beatDF = (fitDF
            .withColumn("o_ts", array([lit(fitDF["timestamp"].getItem(0))] * 500))
            .withColumn("rand", array([lit(rand() * TIME_WINDOW).cast("int")] * 500))
            .withColumn("new_time", 
                        expr("transform(arrays_zip(timestamp, o_ts, rand), x -> x.timestamp - x.o_ts + x.rand)"))
            .withColumn("tmp", arrays_zip("new_time", "heart_rate"))
            .withColumn("tmp", explode("tmp"))
            .select(col("tmp.new_time"), "id", "userId", col("tmp.heart_rate"))
            .filter(col('new_time') >= 0)
            .sort(col("new_time")))
    beatDF.select("*").show(truncate=True)
    beatDF.describe().show()

    n_user = beatDF.select("userId").distinct().count()
    n_workout = beatDF.select("id").distinct().count()

    print('===============================================================')
    print('Workout data has {} unique users and {} workouts.'.format(n_user, n_workout))
    print('===============================================================')

    # write to json
    beatDF.write.json(output_file)
    # beatDF.coalesce(3).write.format('json').save(output_file)

    # stop spark session
    spark.stop()