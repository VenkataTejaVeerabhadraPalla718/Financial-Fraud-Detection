import pandas as pd
import joblib

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder

df = pd.read_csv(
    "synthetic_fraud/data/paysim.csv"
)

df = df.sample(
    100000,
    random_state=42
)

encoder = LabelEncoder()

df["type"] = encoder.fit_transform(
    df["type"]
)

X = df[[
    "type",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest"
]]

model = IsolationForest(
    contamination=0.002,
    random_state=42
)

model.fit(X)

joblib.dump(
    model,
    "synthetic_fraud/models/synthetic_isolation.pkl"
)

print(
    "Isolation Forest Saved"
)