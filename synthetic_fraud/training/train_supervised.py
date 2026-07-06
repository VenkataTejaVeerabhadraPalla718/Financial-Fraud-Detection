import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

print("="*60)
print("SYNTHETIC FRAUD TRAINING")
print("="*60)

df = pd.read_csv(
    "synthetic_fraud/data/paysim.csv"
)

df = df.sample(
    100000,
    random_state=42
)

encoders = {}

for col in ["type"]:

    encoder = LabelEncoder()

    df[col] = encoder.fit_transform(
        df[col].astype(str)
    )

    encoders[col] = encoder

X = df[[
    "type",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest"
]]

y = df["isFraud"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced"
)

model.fit(
    X_train,
    y_train
)

pred = model.predict(X_test)

print(
    classification_report(
        y_test,
        pred
    )
)

joblib.dump(
    model,
    "synthetic_fraud/models/synthetic_model.pkl"
)

joblib.dump(
    encoders,
    "synthetic_fraud/models/synthetic_encoders.pkl"
)

print(
    "Synthetic Model Saved"
)