import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score

print("=" * 60)
print("CREDIT CARD FRAUD SUPERVISED TRAINING")
print("=" * 60)

df = pd.read_csv(
    "credit_card_fraud/data/creditcard.csv"
)

X = df.drop(
    columns=["Class"]
)

y = df["Class"]

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

print("\nTraining Random Forest...\n")

model.fit(
    X_train,
    y_train
)

predictions = model.predict(
    X_test
)

print(
    "Accuracy:",
    accuracy_score(
        y_test,
        predictions
    )
)

print(
    "Precision:",
    precision_score(
        y_test,
        predictions
    )
)

print(
    "Recall:",
    recall_score(
        y_test,
        predictions
    )
)

print(
    "F1 Score:",
    f1_score(
        y_test,
        predictions
    )
)

print("\nClassification Report\n")

print(
    classification_report(
        y_test,
        predictions
    )
)

joblib.dump(
    model,
    "credit_card_fraud/models/credit_card_model.pkl"
)

print("\nModel Saved Successfully")