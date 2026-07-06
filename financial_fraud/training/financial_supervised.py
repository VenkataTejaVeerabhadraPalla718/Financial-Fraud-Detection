import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)
import os
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

print("="*60)
print("FINANCIAL FRAUD SUPERVISED TRAINING")
print("="*60)

BASE_DIR = os.path.dirname(
    os.path.dirname(__file__)
)

df = pd.read_csv(
    os.path.join(
        BASE_DIR,
        "data",
        "financial_fraud_detection_dataset.csv"
    )
)

encoders = joblib.load(
    os.path.join(
        BASE_DIR,
        "models",
        "financial_encoders.pkl"
    )
)

for col, encoder in encoders.items():
    df[col] = encoder.transform(
        df[col].astype(str)
    )

X = df.drop(
    columns=[
        "Fraudulent",
        "Transaction_ID",
        "Customer_ID",
        "Transaction_Date"
    ]
)
scaler = StandardScaler()

X = scaler.fit_transform(X)

y = df["Fraudulent"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

models = {
    "Logistic Regression":
    LogisticRegression(
    max_iter=5000,
    class_weight="balanced",
    solver="lbfgs"
    ),

    "Random Forest":
    RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        random_state=42
    ),

    "XGBoost":
    XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric="logloss"
    )
}

best_model = None
best_score = 0

for name, model in models.items():

    print(f"\nTraining {name}")

    model.fit(
        X_train,
        y_train
    )

    pred = model.predict(X_test)

    acc = accuracy_score(
        y_test,
        pred
    )

    print("Accuracy:", acc)

    print(
        "Precision:",
        precision_score(y_test, pred)
    )

    print(
        "Recall:",
        recall_score(y_test, pred)
    )

    print(
        "F1:",
        f1_score(y_test, pred)
    )

    if acc > best_score:
        best_score = acc
        best_model = model

# Save Individual Models

joblib.dump(
    models["Logistic Regression"],
    os.path.join(
        BASE_DIR,
        "models",
        "financial_lr.pkl"
    )
)

joblib.dump(
    models["Random Forest"],
    os.path.join(
        BASE_DIR,
        "models",
        "financial_rf.pkl"
    )
)

joblib.dump(
    models["XGBoost"],
    os.path.join(
        BASE_DIR,
        "models",
        "financial_xgb.pkl"
    )
)

joblib.dump(
    best_model,
    os.path.join(
        BASE_DIR,
        "models",
        "financial_fraud_model.pkl"
    )
)

print("=" * 60)
print("ALL MODELS SAVED SUCCESSFULLY")
print("=" * 60)