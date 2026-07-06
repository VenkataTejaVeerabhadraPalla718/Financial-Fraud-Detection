import pandas as pd
import psycopg2
from datetime import timedelta

DB_CONFIG = {
    "host": "localhost",
    "database": "fraud_db",
    "user": "postgres",
    "password": "Bhadra@7879"
}


def generate_forecast():

    conn = psycopg2.connect(**DB_CONFIG)

    df = pd.read_sql(
        """
        SELECT *
        FROM fraud_predictions
        ORDER BY created_at
        """,
        conn
    )

    if df.empty:

        conn.close()

        return pd.DataFrame()

    df["created_at"] = pd.to_datetime(
        df["created_at"]
    )

    daily = (
        df.groupby(
            df["created_at"].dt.date
        )
        .agg(
            total_transactions=("prediction", "count"),
            fraud_transactions=("prediction", "sum")
        )
        .reset_index()
    )

    daily.columns = [

        "date",

        "transactions",

        "fraud"

    ]

    avg_transactions = int(
        daily["transactions"].tail(7).mean()
    )

    avg_fraud = int(
        daily["fraud"].tail(7).mean()
    )

    forecasts = []

    last_date = pd.to_datetime(
        daily["date"].max()
    )

    for i in range(1, 31):

        forecasts.append(

            {

                "forecast_date":

                last_date + timedelta(days=i),

                "predicted_transactions":

                avg_transactions,

                "predicted_fraud":

                avg_fraud,

                "confidence":

                95.0

            }

        )

    forecast_df = pd.DataFrame(
        forecasts
    )

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM fraud_forecast"
    )

    conn.commit()

    for _, row in forecast_df.iterrows():

        cursor.execute(
            """
            INSERT INTO fraud_forecast
            (
                forecast_date,
                predicted_transactions,
                predicted_fraud,
                confidence
            )

            VALUES
            (%s,%s,%s,%s)
            """,

            (

                row["forecast_date"],

                int(row["predicted_transactions"]),

                int(row["predicted_fraud"]),

                float(row["confidence"])

            )

        )

    conn.commit()

    conn.close()

    return forecast_df