import pandas as pd
import joblib

from sqlalchemy import create_engine
from sklearn.preprocessing import LabelEncoder

print("=" * 50)
print("Financial Fraud Detection ETL Started")
print("=" * 50)

# Load Dataset

df = pd.read_csv("data/paysim.csv")

print("Dataset Loaded")
print("Rows:", len(df))
print("Columns:", len(df.columns))

# Remove duplicates

df.drop_duplicates(inplace=True)

# Missing values

df.fillna(0, inplace=True)

print("Cleaning Completed")

# Encode transaction type

encoder = LabelEncoder()

df["type"] = encoder.fit_transform(df["type"])

# Save encoder

joblib.dump(
    encoder,
    "models/type_encoder.pkl"
)

print("Encoder Saved")

# PostgreSQL connection

engine = create_engine(
    "postgresql://postgres:Bhadra%407879@localhost:5432/fraud_db"
)

# Load into PostgreSQL

df.to_sql(
    "transactions",
    engine,
    if_exists="replace",
    index=False
)

print("Data Loaded To PostgreSQL")

print("=" * 50)
print("ETL Completed Successfully")
print("=" * 50)