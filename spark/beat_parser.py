import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import arrays_zip, explode, col
from datetime import datetime

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Please enter output file')
    
    output_file = sys.argv[1]

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

    # get beat subset and flat data 
    beatDF = (fitDF
            .withColumn("tmp", arrays_zip("timestamp", "heart_rate"))
            .withColumn("tmp", explode("tmp"))
            .select("id", "userId", col("tmp.timestamp"), col("tmp.heart_rate")))
    beatDF.describe().show()

    n_user = beatDF.select("userId").distinct().count()
    n_workout = beatDF.select("id").distinct().count()

    print('===============================================================')
    print('Workout data has {} unique users and {} workouts.'.format(n_user, n_workout))
    print('===============================================================')

    # write to json
    beatDF.coalesce(1).write.format('json').save(output_file)

    # stop spark session
    spark.stop()