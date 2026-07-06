import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="fraud_db",  # use your actual DB name
    user="postgres",
    password="Bhadra@7879"
)

cursor = conn.cursor()

def save_synthetic_prediction(
    prediction,
    fraud_probability
):

    cursor.execute(
        """
        INSERT INTO synthetic_predictions
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