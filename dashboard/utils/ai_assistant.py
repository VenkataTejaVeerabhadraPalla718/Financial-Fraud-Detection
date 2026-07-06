def explain_transaction(row):

    reasons = []

    if row["fraud_probability"] >= 0.80:
        reasons.append(
            "Very High Fraud Probability"
        )

    if row["prediction"] == 1:
        reasons.append(
            "Model Classified Transaction as Fraud"
        )

    if row["fraud_probability"] >= 0.95:
        reasons.append(
            "Extremely High Confidence"
        )

    return reasons