import pandas as pd
import joblib

from sklearn.ensemble import IsolationForest

print("=" * 60)
print("FINANCIAL FRAUD UNSUPERVISED TRAINING")
print("=" * 60)

# Load Dataset

df = pd.read_csv(
    "data/financial_fraud_detection_dataset.csv"
)

print("Dataset Loaded")
print("Shape:", df.shape)

# Load Encoders

encoders = joblib.load(
    "models/financial_encoders.pkl"
)

# Encode Categorical Columns

for col, encoder in encoders.items():

    df[col] = encoder.transform(
        df[col].astype(str)
    )

# Features

X = df.drop(
    columns=[
        "Fraudulent",
        "Transaction_ID",
        "Customer_ID",
        "Transaction_Date"
    ]
)

print("Feature Shape:", X.shape)

print("Training Isolation Forest...")

iso = IsolationForest(
    n_estimators=100,
    contamination=0.02,
    random_state=42,
    n_jobs=-1
)

iso.fit(X)

joblib.dump(
    iso,
    "models/financial_isolation_forest.pkl"
)

print("\nModel Saved Successfully")

print(
    "models/financial_isolation_forest.pkl"
)

print("=" * 60)
print("UNSUPERVISED TRAINING COMPLETED")
print("=" * 60)