from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import psycopg2
import time
import uuid
from financial_fraud.ensemble.ensemble_predict import (
    ensemble_predict
)

from financial_fraud.database.save_ensemble_prediction import (
    save_ensemble_prediction
)

conn = psycopg2.connect(
    host="localhost",
    database="fraud_db",
    user="postgres",
    password="Bhadra@7879"
)

cursor = conn.cursor()
app = FastAPI(
    title="Financial Fraud Detection API"
)
import os

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


class Transaction(BaseModel):

    Transaction_Amount: float
    Merchant_Category: str
    Payment_Method: str
    Device_Type: str
    Location: str
    Is_International: int
    Previous_Transactions: int
    Average_Spend: float
    Account_Age_Days: int
    Suspicious_Keyword: str


@app.get("/")
def home():

    return {
        "message":
        "Financial Fraud Detection API Running"
    }


@app.post("/predict")

def predict(transaction: Transaction):

    try:
        start_time = time.time()
        df = pd.DataFrame(
            [transaction.dict()]
        )

        for col, encoder in encoders.items():

            if col in df.columns:

                try:

                    df[col] = encoder.transform(
                        df[col].astype(str)
                    )

                except:

                    df[col] = 0

        ensemble_result = ensemble_predict(df)
        
        transaction_id = str(uuid.uuid4())[:8]
        
        prediction = ensemble_result["Final Prediction"]

        confidence = ensemble_result["Confidence"]
        
        save_ensemble_prediction(

            transaction_id,

            ensemble_result["Logistic Regression"],

            ensemble_result["Random Forest"],

            ensemble_result["XGBoost"],

            prediction,

            confidence

        )

        probability = model.predict_proba(df)[0][1]
        
        response_time = round(
            time.time() - start_time,
            4
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
                response_time,
                200
            )
        )

        conn.commit()

        print("API LOG INSERTED")

        return {

            "Logistic Regression":
                "Fraud"
                if ensemble_result["Logistic Regression"] == 1
                else "Legitimate",

            "Random Forest":
                "Fraud"
                if ensemble_result["Random Forest"] == 1
                else "Legitimate",

            "XGBoost":
                "Fraud"
                if ensemble_result["XGBoost"] == 1
                else "Legitimate",

            "Fraud Votes":
                ensemble_result["Fraud Votes"],

            "Legitimate Votes":
                ensemble_result["Legitimate Votes"],

            "Final Prediction":
                "Fraud"
                if prediction == 1
                else "Legitimate",

            "Confidence":
                f"{confidence}%"

        }

    except Exception as e:

        return {
            "error":
            str(e)
        }