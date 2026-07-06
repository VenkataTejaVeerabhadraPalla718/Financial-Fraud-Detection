from financial_fraud.database.db_config import (
    conn,
    cursor
)

def save_ensemble_prediction(

    transaction_id,

    lr,

    rf,

    xgb,

    final,

    confidence

):

    cursor.execute(
        """
        INSERT INTO ensemble_predictions
        (
            transaction_id,
            logistic_prediction,
            random_forest_prediction,
            xgboost_prediction,
            final_prediction,
            confidence
        )

        VALUES
        (%s,%s,%s,%s,%s,%s)
        """,
        (
            transaction_id,
            lr,
            rf,
            xgb,
            final,
            confidence
        )
    )

    conn.commit()