from kafka import KafkaConsumer
import pandas as pd
import json
import joblib
import psycopg2
import os

from synthetic_fraud.database.save_synthetic_prediction import (
    save_synthetic_prediction
)

# ==========================================
# DATABASE CONNECTION
# ==========================================

conn = psycopg2.connect(
    host="localhost",
    database="fraud_db",
    user="postgres",
    password="Bhadra@7879"
)

cursor = conn.cursor()

# ==========================================
# LOAD MODEL & ENCODERS
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(__file__)
)

model = joblib.load(
    os.path.join(
        BASE_DIR,
        "models",
        "synthetic_model.pkl"
    )
)

encoders = joblib.load(
    os.path.join(
        BASE_DIR,
        "models",
        "synthetic_encoders.pkl"
    )
)

# ==========================================
# KAFKA CONSUMER
# ==========================================

consumer = KafkaConsumer(
    "synthetic_fraud_topic",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="latest",
    value_deserializer=lambda x:
    json.loads(
        x.decode("utf-8")
    )
)

print("=" * 60)
print("SYNTHETIC FRAUD DETECTION STARTED")
print("=" * 60)

# ==========================================
# PROCESS STREAM
# ==========================================

for message in consumer:

    try:

        data = message.value

        df = pd.DataFrame([data])

        # ----------------------------------
        # ENCODE TYPE COLUMN
        # ----------------------------------

        if "type" in df.columns:

            try:

                df["type"] = encoders[
                    "type"
                ].transform(
                    df["type"].astype(str)
                )

            except Exception:

                df["type"] = 0

        # ----------------------------------
        # FEATURE ORDER
        # ----------------------------------

        X = df[
            [
                "type",
                "amount",
                "oldbalanceOrg",
                "newbalanceOrig",
                "oldbalanceDest",
                "newbalanceDest"
            ]
        ]

        # ----------------------------------
        # PREDICTION
        # ----------------------------------

        prediction = int(
            model.predict(X)[0]
        )

        probability = float(
            model.predict_proba(X)[0][1]
        )

        # ----------------------------------
        # SAVE PREDICTION
        # ----------------------------------

        save_synthetic_prediction(
            prediction,
            probability
        )

        print(
            f"Prediction={prediction} "
            f"Probability={probability:.4f}"
        )

        # ----------------------------------
        # ALERT HISTORY
        # ----------------------------------

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
                    "Synthetic Fraud",
                    "SYNTHETIC_TXN",
                    probability,
                    "High Risk Synthetic Fraud"
                )
            )

            conn.commit()

            print(
                f"🚨 SYNTHETIC FRAUD "
                f"({probability:.2%})"
            )

        else:

            print(
                f"✅ Legitimate "
                f"({probability:.2%})"
            )

        # ----------------------------------
        # KAFKA LOGS
        # ----------------------------------

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
                "synthetic_fraud_topic",
                1
            )
        )

        conn.commit()

        print(
            "Kafka Log Inserted"
        )

    except Exception as e:

        print(
            f"ERROR : {e}"
        )