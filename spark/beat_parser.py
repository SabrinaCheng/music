"""parse row fitrec data to kafka procuder message with format: timestamp, id, userId, heart_rate"""


import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import arrays_zip, explode, col
from datetime import datetime

if __name__ == "__main__":
    output_file = 's3a://fitrec/proper/endomondoHR_proper_ready.json'

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
            .withColumn("tmp", arrays_zip("timestamp", "heart_rate"))
            .withColumn("tmp", explode("tmp"))
            .select(col("tmp.timestamp"), "id", "userId", col("tmp.heart_rate"))
            .sort(col("timestamp")))
    beatDF.select("*").show(truncate=True)
    beatDF.describe().show()

    n_user = beatDF.select("userId").distinct().count()
    n_workout = beatDF.select("id").distinct().count()

    print('===============================================================')
    print('Workout data has {} unique users and {} workouts.'.format(n_user, n_workout))
    print('===============================================================')

    # write to json
    beatDF.write.json(output_file)

    # stop spark session
    spark.stop()