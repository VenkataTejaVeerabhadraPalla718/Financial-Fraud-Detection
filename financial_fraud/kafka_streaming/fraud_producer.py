from kafka import KafkaProducer
import pandas as pd
import json
import time
import os

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda x:
    json.dumps(x).encode("utf-8")
)

BASE_DIR = os.path.dirname(
    os.path.dirname(__file__)
)

df = pd.read_csv(
    os.path.join(
        BASE_DIR,
        "data",
        "financial_fraud_detection_dataset.csv"
    )
)

print("=" * 60)
print("STREAMING STARTED")
print("=" * 60)

for _, row in df.iterrows():

    transaction = row.to_dict()

    producer.send(
        "fraud_transactions",
        transaction
    )

    print(
        f"Sent: {transaction['Transaction_ID']}"
    )

    time.sleep(0.001)

producer.flush()

print("=" * 60)
print("STREAMING COMPLETED")
print("=" * 60)