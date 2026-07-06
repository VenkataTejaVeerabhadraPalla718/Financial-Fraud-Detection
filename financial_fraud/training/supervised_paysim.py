import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from xgboost import XGBClassifier

print("="*60)
print("SUPERVISED FRAUD DETECTION TRAINING")
print("="*60)

# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

df = pd.read_csv("data/paysim.csv")

print("Dataset Loaded Successfully")
print("Shape:", df.shape)

# --------------------------------------------------
# SAMPLE DATA
# --------------------------------------------------

sample_size = 500000

if len(df) > sample_size:
    df = df.sample(
        n=sample_size,
        random_state=42
    )

print("Training Shape:", df.shape)

# --------------------------------------------------
# ENCODE TYPE COLUMN
# --------------------------------------------------

encoder = LabelEncoder()

df["type"] = encoder.fit_transform(df["type"])

joblib.dump(
    encoder,
    "models/type_encoder.pkl"
)

# --------------------------------------------------
# FEATURES
# --------------------------------------------------

X = df.drop(
    columns=[
        "nameOrig",
        "nameDest",
        "isFraud"
    ]
)

y = df["isFraud"]

# --------------------------------------------------
# TRAIN TEST SPLIT
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTrain Shape:", X_train.shape)
print("Test Shape:", X_test.shape)

# ==================================================
# LOGISTIC REGRESSION
# ==================================================

print("\nTraining Logistic Regression...")

lr = LogisticRegression(
    class_weight="balanced",
    max_iter=1000
)

lr.fit(X_train, y_train)

lr_pred = lr.predict(X_test)

print("\nLOGISTIC REGRESSION RESULTS")

print(
    "Accuracy:",
    accuracy_score(y_test, lr_pred)
)

print(
    "Precision:",
    precision_score(y_test, lr_pred)
)

print(
    "Recall:",
    recall_score(y_test, lr_pred)
)

print(
    "F1 Score:",
    f1_score(y_test, lr_pred)
)

# ==================================================
# RANDOM FOREST
# ==================================================

print("\nTraining Random Forest...")

rf = RandomForestClassifier(
    n_estimators=100,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

rf.fit(X_train, y_train)

rf_pred = rf.predict(X_test)

print("\nRANDOM FOREST RESULTS")

print(
    "Accuracy:",
    accuracy_score(y_test, rf_pred)
)

print(
    "Precision:",
    precision_score(y_test, rf_pred)
)

print(
    "Recall:",
    recall_score(y_test, rf_pred)
)

print(
    "F1 Score:",
    f1_score(y_test, rf_pred)
)

# ==================================================
# XGBOOST
# ==================================================

print("\nTraining XGBoost...")

xgb = XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    eval_metric="logloss"
)

xgb.fit(
    X_train,
    y_train
)

xgb_pred = xgb.predict(X_test)

print("\nXGBOOST RESULTS")

print(
    "Accuracy:",
    accuracy_score(y_test, xgb_pred)
)

print(
    "Precision:",
    precision_score(y_test, xgb_pred)
)

print(
    "Recall:",
    recall_score(y_test, xgb_pred)
)

print(
    "F1 Score:",
    f1_score(y_test, xgb_pred)
)

# ==================================================
# SAVE BEST MODEL
# ==================================================

joblib.dump(
    rf,
    "models/fraud_model.pkl"
)

print("\nBest Model Saved")

print("\nSaved File:")
print("models/fraud_model.pkl")

print("="*60)
print("TRAINING COMPLETED")
print("="*60)