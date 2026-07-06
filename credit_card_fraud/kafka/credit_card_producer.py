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
    "credit_card_fraud/data/creditcard.csv"
)

print("=" * 60)
print("CREDIT CARD STREAMING STARTED")
print("=" * 60)

for _, row in df.head(10000).iterrows():

    data = row.to_dict()

    data.pop("Class", None)

    producer.send(
        "credit_card_topic",
        data
    )

    print(
        f"Sent Transaction"
    )

    time.sleep(0.001)

producer.flush()

print("STREAMING COMPLETED")