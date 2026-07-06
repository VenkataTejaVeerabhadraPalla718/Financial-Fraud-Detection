from credit_card_fraud.alerts.email_alert import send_alert
from kafka import KafkaConsumer
import pandas as pd
import json
import joblib
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="fraud_db",
    user="postgres",
    password="Bhadra@7879"
)

cursor = conn.cursor()
from credit_card_fraud.database.save_credit_prediction import save_credit_prediction

model = joblib.load(
    "credit_card_fraud/models/credit_card_model.pkl"
)

consumer = KafkaConsumer(
    "credit_card_topic",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="latest",
    value_deserializer=lambda x:
    json.loads(x.decode("utf-8"))
)

print("=" * 60)
print("CREDIT CARD FRAUD DETECTION STARTED")
print("=" * 60)

for message in consumer:

    try:

        data = message.value

        df = pd.DataFrame([data])

        if "Class" in df.columns:
            df = df.drop(columns=["Class"])

        prediction = int(
            model.predict(df)[0]
        )

        probability = float(
            model.predict_proba(df)[0][1]
        )

        print(
            f"Prediction={prediction}, Probability={probability:.4f}"
        )
        
        save_credit_prediction(
            prediction,
            probability
        )

        if prediction == 1:
            
            cursor.execute(
            """
            INSERT INTO alert_history
            (
                fraud_type,
                transaction_id,
                fraud_probability,
                alert_message
            )
            VALUES
            (%s,%s,%s,%s)
            """,
            (
                "Credit Card Fraud",
                "CREDIT_CARD_TXN",
                probability,
                "High Risk Credit Card Transaction"
            )
            )

            conn.commit()
        
            print(
                f"🚨 CREDIT CARD FRAUD ({probability:.2%})"
            )

            send_alert(
                transaction_id="CREDIT_CARD_TXN",
                amount=float(data["Amount"]),
                fraud_probability=round(
                    probability * 100,
                    2
                )
            )

        else:

            print(
                f"✅ Legitimate ({probability:.2%})"
            )

        cursor.execute(
            """
            INSERT INTO kafka_logs
            (
            topic_name,
            message_count
            )
            VALUES
            (%s,%s)
            """,
            (
            "credit_card_topic",
            1
            )
        )
        conn.commit()
        print("Kafka Log Inserted")

    except Exception as e:

        print(
            f"ERROR : {e}"
        )
    