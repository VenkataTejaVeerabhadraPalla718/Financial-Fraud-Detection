import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "fraud_db",
    "user": "postgres",
    "password": "Bhadra@7879"
}


def log_activity(username, activity, page):

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO user_activity_logs
        (
            username,
            activity,
            page_name
        )
        VALUES
        (%s,%s,%s)
        """,
        (
            username,
            activity,
            page
        )
    )

    conn.commit()

    cursor.close()
    conn.close()