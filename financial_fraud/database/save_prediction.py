from financial_fraud.database.db_config import conn, cursor

def save_prediction(
    transaction_id,
    prediction,
    fraud_probability
):

    cursor.execute(
        """
        INSERT INTO fraud_predictions
        (
            transaction_id,
            prediction,
            fraud_probability
        )
        VALUES
        (%s,%s,%s)

        ON CONFLICT (transaction_id)
        DO NOTHING
        """,
        (
            transaction_id,
            prediction,
            fraud_probability
        )
    )

    conn.commit()