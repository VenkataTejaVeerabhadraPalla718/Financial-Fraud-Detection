import pandas as pd
import joblib

from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import IsolationForest

print("=" * 60)
print("UNSUPERVISED FRAUD DETECTION")
print("=" * 60)

# Load Dataset

df = pd.read_csv("data/paysim.csv")

print("Dataset Loaded")
print("Original Shape:", df.shape)

# Sample Data for Faster Training

sample_size = 300000

if len(df) > sample_size:
    df = df.sample(
        n=sample_size,
        random_state=42
    )

print("Training Shape:", df.shape)

# Encode Transaction Type

encoder = LabelEncoder()

df["type"] = encoder.fit_transform(df["type"])

# Features

X = df.drop(
    columns=[
        "nameOrig",
        "nameDest",
        "isFraud"
    ]
)

print("Training Isolation Forest...")

iso = IsolationForest(
    n_estimators=100,
    contamination=0.002,
    random_state=42,
    n_jobs=-1
)

iso.fit(X)

# Save Model

joblib.dump(
    iso,
    "models/isolation_forest.pkl"
)

print("Model Saved")

print("Saved File:")
print("models/isolation_forest.pkl")

print("=" * 60)
print("UNSUPERVISED TRAINING COMPLETED")
print("=" * 60)