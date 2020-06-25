# Beat & Tempo

## Introduction
How to create a playlist for better workout?
"Listening to music during exercise can improve results, both in terms of being a motivator (people exercise longer and more vigorously to music) and as a distraction from negatives like fatigue." "Music tempo with high motivational qualities roughly corresponds to the average person's heart rate during a routine workout." Taking the advantagies of new opportunities that wearable devices enable heart rate monitoring, this project recommends workout music based on heart rate.

## Demo

## Data
* FitRec Dataset (https://sites.google.com/eng.ucsd.edu/fitrec-project/home)
  ~ 4GB, 253,020 workouts / 1,104 users.
  Heart rate, timestamp

* Million Song Dataset (https://aws.amazon.com/datasets/million-song-dataset/)
  ~ 230GB, last updated: 2015.
  Tempo


## Architecture

![Alt text](img/tech_stack.png?raw=true "Title")

## Engineering challenges

### Injection
With 1,000,000 h5 files in Million Song Dataset as data source, directly injecting all h5 files is impractical. Considering there is only one read and no write operation, this project combines a batch of h5 files to json (instead of Apache Parquet) and then feed to PostgreSQL.

### Preprocessing
To deal with the MemoryError when loading and transforming Fitrec raw data from AWS S3 to EC2, the project uses Spark to remove unnecessary data, and unpack timestamp and heart_rate from wide to long format. Although after the spark preprocessing, the size of file increases from ~ 4GB to ~9GB, the unpacked data makes it easier to create Kafka messages.
![Alt text](img/spark_processing.png?raw=true "Title")


### Recommendation algorithm
This project has to calculate the moving average of heart rate, check whether the users need next song, and query songs based on the average heart rate, so two Kafka topics are created. The first topic calculates the average, and the second topic finds the songs to recommend to users. Because of high volumn of operations and mixed data types(int and list), Redis hashmap is used to store the resulting heart rate and songs.


![Alt text](img/kafka_multiple_topics.png?raw=true "Title")

