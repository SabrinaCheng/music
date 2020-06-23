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

### Propressing
To deal with the MemoryError when loading and transforming Fitrec raw data from AWS S3 to EC2, the project uses Spark to remove unnecessary data, and unpack timestamp and heart_rate from wide to long format. Although after the spark preprocessing, the size of file increases from ~ 4GB to ~9GB, the unpacked data makes it easier to create Kafka messages.
![Alt text](img/spark_processing.png?raw=true "Title")


### Recommendation algorithm



![Alt text](img/kafka_multiple_topics.png?raw=true "Title")

