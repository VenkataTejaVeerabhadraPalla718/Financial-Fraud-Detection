import psycopg2
import pandas as pd


DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "database": "fraud_db",
    "user": "postgres",
    "password": "Bhadra@7879"
}


def get_connection():
    return psycopg2.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        database=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        connect_timeout=10
    )


def load_table(table_name):
    allowed_tables = {
        "alert_history",
        "api_logs",
        "credit_card_predictions",
        "ensemble_predictions",
        "financial_transactions",
        "fraud_forecast",
        "fraud_predictions",
        "kafka_logs",
        "model_metrics",
        "reports",
        "synthetic_predictions",
        "transactions",
        "user_activity",
        "user_activity_logs",
        "users"
    }

    if table_name not in allowed_tables:
        raise ValueError(f"Invalid table name: {table_name}")

    conn = None

    try:
        conn = get_connection()

        query = f"SELECT * FROM {table_name}"

        return pd.read_sql(query, conn)

    finally:
        if conn is not None:
            conn.close()


def load_alerts():
    return load_table("alert_history")


def load_metrics():
    return load_table("model_metrics")


def load_kafka_logs():
    return load_table("kafka_logs")


def load_api_logs():
    return load_table("api_logs")


def load_risk_scores():
    financial = load_table("fraud_predictions")
    credit = load_table("credit_card_predictions")
    synthetic = load_table("synthetic_predictions")

    return financial, credit, synthetic


def kafka_summary():
    df = load_table("kafka_logs")

    if df.empty:
        return {
            "messages": 0,
            "topics": 0,
            "last_time": None
        }

    topic_column = "topic_name"

    if "topic_name" not in df.columns:
        if "topic" in df.columns:
            topic_column = "topic"
        else:
            topic_column = None

    created_at_column = "created_at"

    if created_at_column not in df.columns:
        created_at_column = None

    return {
        "messages": len(df),
        "topics": df[topic_column].nunique() if topic_column else 0,
        "last_time": (
            df.iloc[-1][created_at_column]
            if created_at_column
            else None
        )
    }


def get_counts():
    conn = None

    try:
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

        cursor.close()

        return (
            financial_count,
            credit_count,
            synthetic_count
        )

    finally:
        if conn is not None:
            conn.close()


def load_user_activity():
    return load_table("user_activity_logs")


def load_forecast():
    return load_table("fraud_forecast")