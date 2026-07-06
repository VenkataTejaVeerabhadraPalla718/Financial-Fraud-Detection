from kafka import KafkaProducer
import pandas as pd
import json
import time

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda x:
    json.dumps(x).encode("utf-8")
)

df = pd.read_csv(
    "synthetic_fraud/data/paysim.csv"
)

print("=" * 60)
print("SYNTHETIC FRAUD STREAMING STARTED")
print("=" * 60)

for _, row in df.head(1000).iterrows():

    data = row.to_dict()

    data.pop("isFraud", None)

    producer.send(
        "synthetic_fraud_topic",
        data
    )

    print("Sent Transaction")

    time.sleep(0.001)

producer.flush()

print("STREAMING COMPLETED")