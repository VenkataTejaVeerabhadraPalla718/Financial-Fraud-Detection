from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import psycopg2
import os
import time

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
# FASTAPI
# ==========================================

app = FastAPI(
    title="Synthetic Fraud Detection API"
)

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
# REQUEST SCHEMA
# ==========================================

class SyntheticTransaction(BaseModel):

    type: str

    amount: float

    oldbalanceOrg: float
    newbalanceOrig: float

    oldbalanceDest: float
    newbalanceDest: float


# ==========================================
# HOME
# ==========================================

@app.get("/")
def home():

    return {
        "message":
        "Synthetic Fraud Detection API Running"
    }


# ==========================================
# PREDICT
# ==========================================

@app.post("/predict")
def predict(
    transaction: SyntheticTransaction
):

    try:

        start_time = time.time()

        df = pd.DataFrame(
            [transaction.model_dump()]
        )

        # ----------------------------------
        # APPLY ENCODERS
        # ----------------------------------

        for col, encoder in encoders.items():

            if col in df.columns:

                try:

                    df[col] = encoder.transform(
                        df[col].astype(str)
                    )

                except Exception:

                    df[col] = 0

        # ----------------------------------
        # FEATURE ORDER
        # ----------------------------------

        feature_order = [

            "type",
            "amount",
            "oldbalanceOrg",
            "newbalanceOrig",
            "oldbalanceDest",
            "newbalanceDest"

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
        # API LOGGING
        # ----------------------------------

        response_time = round(
            time.time() - start_time,
            4
        )

        try:

            print(
                "Trying to insert API log..."
            )

            cursor.execute(
                """
                INSERT INTO api_logs
                (
                    endpoint,
                    response_time,
                    status_code
                )
                VALUES
                (%s,%s,%s)
                """,
                (
                    "/synthetic_predict",
                    response_time,
                    200
                )
            )

            conn.commit()

            print(
                "API Log Inserted Successfully"
            )

        except Exception as log_error:

            conn.rollback()

            print(
                f"API LOG ERROR: {log_error}"
            )

        # ----------------------------------
        # RESPONSE
        # ----------------------------------

        return {

            "prediction":
            prediction,

            "fraud_probability":
            round(
                probability,
                4
            )

        }

    except Exception as e:

        print(
            f"PREDICTION ERROR: {e}"
        )

        return {

            "error":
            str(e)

        }