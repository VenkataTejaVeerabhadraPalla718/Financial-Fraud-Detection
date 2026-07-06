import psycopg2
import pandas as pd

DB_CONFIG = {
    "host": "localhost",
    "database": "fraud_db",
    "user": "postgres",
    "password": "Bhadra@7879"
}

def get_connection():

    return psycopg2.connect(
        host=DB_CONFIG["host"],
        database=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )


def load_table(table_name):

    conn = get_connection()

    query = f"SELECT * FROM {table_name}"

    df = pd.read_sql(query, conn)

    conn.close()

    return df

def load_alerts():
    return load_table("alert_history")

def load_metrics():
    return load_table("model_metrics")

def load_kafka_logs():
    return load_table("kafka_logs")

def load_api_logs():
    return load_table("api_logs")

def load_risk_scores():

    financial = load_table(
        "fraud_predictions"
    )

    credit = load_table(
        "credit_card_predictions"
    )

    synthetic = load_table(
        "synthetic_predictions"
    )

    return (
        financial,
        credit,
        synthetic
    )
def kafka_summary():

    df = load_table("kafka_logs")

    if df.empty:

        return {
            "messages": 0,
            "topics": 0,
            "last_time": None
        }

    return {

        "messages": len(df),

        "topics": df["topic_name"].nunique(),

        "last_time": df.iloc[-1]["created_at"]

    }
def get_counts():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM fraud_predictions"
    )
    financial_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM credit_card_predictions"
    )
    credit_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM synthetic_predictions"
    )
    synthetic_count = cursor.fetchone()[0]

    conn.close()

    return (
        financial_count,
        credit_count,
        synthetic_count
    )
def load_user_activity():

    return load_table(
        "user_activity_logs"
    )
def load_forecast():

    return load_table(
        "fraud_forecast"
    )