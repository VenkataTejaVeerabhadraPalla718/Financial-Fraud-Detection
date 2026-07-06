import os
import json
import joblib
import pandas as pd

from kafka import KafkaConsumer

from financial_fraud.alerts.email_alert import send_alert
from financial_fraud.database.db_config import conn, cursor
from financial_fraud.database.save_prediction import save_prediction

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
        "financial_fraud_model.pkl"
    )
)

encoders = joblib.load(
    os.path.join(
        BASE_DIR,
        "models",
        "financial_encoders.pkl"
    )
)

# ==========================================
# KAFKA CONSUMER
# ==========================================

consumer = KafkaConsumer(
    "fraud_transactions",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="latest",
    value_deserializer=lambda x: json.loads(
        x.decode("utf-8")
    )
)

print("=" * 60)
print("REAL-TIME FRAUD DETECTION STARTED")
print("=" * 60)

# ==========================================
# PROCESS TRANSACTIONS
# ==========================================

for message in consumer:

    try:

        data = message.value

        transaction_id = data["Transaction_ID"]

        df = pd.DataFrame([data])

        # ----------------------------------
        # REMOVE UNUSED COLUMNS
        # ----------------------------------

        drop_cols = [
            "Transaction_ID",
            "Customer_ID",
            "Transaction_Date",
            "Fraudulent"
        ]

        for col in drop_cols:

            if col in df.columns:

                df.drop(
                    columns=[col],
                    inplace=True
                )

        # ----------------------------------
        # ENCODE CATEGORICAL FEATURES
        # ----------------------------------

        for col, encoder in encoders.items():

            if col in df.columns:

                try:

                    df[col] = encoder.transform(
                        df[col].astype(str)
                    )

                except Exception:

                    # unseen category
                    df[col] = 0

        # ----------------------------------
        # FEATURE ORDER
        # ----------------------------------

        feature_order = [

            "Transaction_Amount",
            "Merchant_Category",
            "Payment_Method",
            "Device_Type",
            "Location",
            "Is_International",
            "Previous_Transactions",
            "Average_Spend",
            "Account_Age_Days",
            "Suspicious_Keyword"

        ]

        df = df[feature_order]

        # ----------------------------------
        # PREDICTION
        # ----------------------------------

        prediction = int(
            model.predict(df)[0]
        )

        probability = float(
            model.predict_proba(df)[0][1]
        )

        # ----------------------------------
        # SAVE PREDICTION
        # ----------------------------------

        save_prediction(
            transaction_id,
            prediction,
            probability
        )

        print(
            f"Processed Transaction : {transaction_id}"
        )

        # ----------------------------------
        # FRAUD ALERT HISTORY
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
                    "Financial Fraud",
                    transaction_id,
                    probability,
                    "High Risk Transaction"
                )
            )

            conn.commit()

            print(
                f"🚨 FRAUD DETECTED ({probability:.2%})"
            )

            try:

                send_alert(
                    transaction_id=transaction_id,
                    amount=float(
                        data["Transaction_Amount"]
                    ),
                    fraud_probability=round(
                        probability * 100,
                        2
                    )
                )

            except Exception as email_error:

                print(
                    f"Email Error : {email_error}"
                )

        else:

            print(
                f"✅ Legitimate Transaction ({probability:.2%})"
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
                "fraud_transactions",
                1
            )
        )

        conn.commit()

        print(
            f"Kafka Log Inserted : {transaction_id}"
        )

    except Exception as e:

        print(
            f"ERROR : {e}"
        )