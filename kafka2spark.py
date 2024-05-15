from pyspark.sql import SparkSession
from pyspark.sql import Row
from dotenv import load_dotenv
from pyspark.sql.functions import from_json
import os 
from pyspark.sql.types import StructType, StringType, DoubleType, FloatType, IntegerType, StructField

load_dotenv(dotenv_path='.kafka.env')
BOOTSTRAP_SERVER = os.getenv('BOOTSTRAP_SERVER')
TOPIC = os.getenv('TOPIC')
TIMING = float(os.getenv('TIMING'))

def write_to_postgresql(df,epoch_id):
    df.write \
    .format('jdbc') \
    .options(url='jdbc:postgresql://db:5432/postgres',
            driver='org.postgresql.Driver',
            dbtable='final_pipeline',
            user='postgres',
            password='postgres',
            ) \
    .mode('append') \
    .save()

schema = StructType([
    StructField("Date", StringType(), True),
    StructField("Price", FloatType(), True)
    ])

# Create a SparkSession
spark = SparkSession.builder.appName("SparkSQL")\
.config("spark.executor.extraClassPath", './postgresql-42.7.3.jar')\
.config('spark.jars','./postgresql-42.7.3.jar').getOrCreate()\

# turn off INFO logging
spark.sparkContext.setLogLevel("ERROR")

# spark read kafka stream from pseudo-stream topic
raw_stream_df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", BOOTSTRAP_SERVER) \
    .option("subscribe", TOPIC) \
    .option("startingOffsets", "latest") \
    .load()

# Print the schema of the raw_stream_df
raw_stream_df.printSchema()

cleaned_stream_df = raw_stream_df.select(
    from_json(
        col=raw_stream_df.value.cast("string"),
        schema=schema,
    ).alias("parsed_value")
).select("parsed_value.*")

"""
query = cleaned_stream_df.writeStream\
         .outputMode("append")\
         .format("console")\
         .start()"""

# write stream to postgres container, in batch 5 seconds
"""
query = cleaned_stream_df.writeStream \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://postgres:5432/postgres") \
        .option("driver", "org.postgresql.Driver") \
        .option("dbtable", "test") \
        .option("user", "postgres") \
        .option("password", "postgres") \
        .foreachBatch(write_to_postgresql) \
        .trigger(processingTime="5 seconds") \
        .start()
"""
query = cleaned_stream_df.writeStream.foreachBatch(write_to_postgresql).trigger(processingTime="2 seconds").start()
# Run forever until terminated
query.awaitTermination()

# Cleanly shut down the session
spark.stop()
