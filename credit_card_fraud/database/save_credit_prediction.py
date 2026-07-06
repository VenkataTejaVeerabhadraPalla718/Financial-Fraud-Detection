import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="fraud_db",   # replace with your actual database name if different
    user="postgres",
    password="Bhadra@7879"
)

cursor = conn.cursor()

def save_credit_prediction(
    prediction,
    fraud_probability
):
    cursor.execute(
        """
        INSERT INTO credit_card_predictions
        (
            prediction,
            fraud_probability
        )
        VALUES
        (%s,%s)
        """,
        (
            prediction,
            fraud_probability
        )
    )

    conn.commit()