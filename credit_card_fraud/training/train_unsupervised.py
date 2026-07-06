import pandas as pd
import joblib

from sklearn.ensemble import IsolationForest

print("=" * 60)
print("CREDIT CARD FRAUD UNSUPERVISED TRAINING")
print("=" * 60)

df = pd.read_csv(
    "credit_card_fraud/data/creditcard.csv"
)

X = df.drop(
    columns=["Class"]
)

model = IsolationForest(
    contamination=0.002,
    random_state=42
)

print("\nTraining Isolation Forest...\n")

model.fit(X)

joblib.dump(
    model,
    "credit_card_fraud/models/credit_card_isolation.pkl"
)

print(
    "\nIsolation Forest Saved Successfully"
)