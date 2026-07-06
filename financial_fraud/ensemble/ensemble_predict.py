import os
import joblib
import numpy as np

# ---------------------------------------
# LOAD MODELS
# ---------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(__file__)
)

lr_model = joblib.load(
    os.path.join(
        BASE_DIR,
        "models",
        "financial_lr.pkl"
    )
)

rf_model = joblib.load(
    os.path.join(
        BASE_DIR,
        "models",
        "financial_rf.pkl"
    )
)

xgb_model = joblib.load(
    os.path.join(
        BASE_DIR,
        "models",
        "financial_xgb.pkl"
    )
)


# ---------------------------------------
# ENSEMBLE PREDICTION
# ---------------------------------------

def ensemble_predict(X):

    lr_pred = int(
        lr_model.predict(X)[0]
    )

    rf_pred = int(
        rf_model.predict(X)[0]
    )

    xgb_pred = int(
        xgb_model.predict(X)[0]
    )

    votes = [
        lr_pred,
        rf_pred,
        xgb_pred
    ]

    fraud_votes = votes.count(1)

    legitimate_votes = votes.count(0)

    final_prediction = 1 if fraud_votes >= 2 else 0

    confidence = max(
        fraud_votes,
        legitimate_votes
    ) / len(votes)

    return {

        "Logistic Regression": lr_pred,

        "Random Forest": rf_pred,

        "XGBoost": xgb_pred,

        "Final Prediction": final_prediction,

        "Fraud Votes": fraud_votes,

        "Legitimate Votes": legitimate_votes,

        "Confidence": round(
            confidence * 100,
            2
        )

    }