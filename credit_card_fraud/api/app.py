from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="fraud_db",
    user="postgres",
    password="Bhadra@7879"
)

cursor = conn.cursor()
app = FastAPI(
    title="Credit Card Fraud Detection API"
)

import os

BASE_DIR = os.path.dirname(
    os.path.dirname(__file__)
)

model = joblib.load(
    os.path.join(
        BASE_DIR,
        "models",
        "credit_card_model.pkl"
    )
)

class CreditCardTransaction(BaseModel):

    Time: float

    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float

    Amount: float


@app.get("/")
def home():

    return {
        "message":
        "Credit Card Fraud API Running"
    }


@app.post("/predict")

def predict(
    transaction: CreditCardTransaction
):

    df = pd.DataFrame(
        [transaction.dict()]
    )

    prediction = int(
        model.predict(df)[0]
    )

    probability = float(
        model.predict_proba(df)[0][1]
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
        "/predict",
        0.12,
        200
        )
    )
    return {

        "prediction":
        prediction,

        "fraud_probability":
        round(
            probability,
            4
        )
    }