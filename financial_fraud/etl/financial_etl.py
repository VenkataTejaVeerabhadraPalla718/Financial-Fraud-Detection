import pandas as pd
import joblib

from sqlalchemy import create_engine
from sklearn.preprocessing import LabelEncoder

print("="*60)
print("FINANCIAL FRAUD ETL")
print("="*60)

df = pd.read_csv(
    "data/financial_fraud_detection_dataset.csv"
)

print("Dataset Loaded")
print(df.shape)

df.drop_duplicates(inplace=True)

df.fillna("Unknown", inplace=True)

categorical_cols = [
    "Merchant_Category",
    "Payment_Method",
    "Device_Type",
    "Location",
    "Suspicious_Keyword"
]

encoders = {}

for col in categorical_cols:

    encoder = LabelEncoder()

    df[col] = encoder.fit_transform(
        df[col].astype(str)
    )

    encoders[col] = encoder

joblib.dump(
    encoders,
    "models/financial_encoders.pkl"
)

engine = create_engine(
    "postgresql://postgres:Bhadra%407879@localhost:5432/fraud_db"
)

df.to_sql(
    "financial_transactions",
    engine,
    if_exists="replace",
    index=False,
    chunksize=1000,
    method="multi"
)

print("ETL COMPLETED")