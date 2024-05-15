import pandas as pd
import json
from dotenv import load_dotenv
import os
from kafka import KafkaProducer
import time

load_dotenv(dotenv_path='.kafka.env')
BOOTSTRAP_SERVER = os.getenv('BOOTSTRAP_SERVER')
TOPIC = os.getenv('TOPIC')
TIMING = float(os.getenv('TIMING'))

df = pd.read_csv('VN_Index_Historical_Data.csv')
producer = KafkaProducer(bootstrap_servers=[BOOTSTRAP_SERVER])

list_price = ["Price", "Open", "High", "Low"]
for i in list_price:
    df[i] = pd.to_numeric(df[i].apply(lambda x: x.replace(",", "")))

col = []
for i in range(0, 7):
    col.append(df.columns[i])
# col contains ['Date', 'Price', 'Open', 'High', 'Low', 'Vol.', 'Change %']

def send(tmp):
    s = {}
    for i in range(0, 7):
        s[col[i]] = tmp[i]
    print("Message: ", s)
    producer.send(TOPIC, value = json.dumps(s).encode('utf-8'))

for i in range(df.shape[0]-1, -1, -1):
    tmp = list(df.loc[i])
    send(tmp)
    time.sleep(TIMING)