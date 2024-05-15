from pyspark.sql import SparkSession
from pyspark.sql import Row
from dotenv import load_dotenv
from pyspark.sql.functions import from_json
import os


load_dotenv(dotenv_path='.kafka.env')
BOOTSTRAP_SERVER = os.getenv('BOOTSTRAP_SERVER')
TOPIC = os.getenv('TOPIC')
TIMING = float(os.getenv('TIMING'))

spark = SparkSession.builder.appName("SparkSQL")\
.config('spark.jars','./postgresql-42.7.3.jar').getOrCreate()

# load csv file
df = spark.read.csv("VN Index Historical Data.csv", header=True, inferSchema=True)
cleaned_df = df.select("Date")
cleaned_df.show()
# write to postgresql
cleaned_df.write \
    .format('jdbc') \
    .options(url='jdbc:postgresql://localhost:5432/postgres',
            driver='org.postgresql.Driver',
            dbtable='test',
            user='postgres',
            password='postgres',
            ) \
        .save()
spark.stop()


