import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "fraud_db",
    "user": "postgres",
    "password": "Bhadra@7879"
}


def authenticate_user(
    username,
    password
):

    conn = psycopg2.connect(
        **DB_CONFIG
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username=%s
        AND password=%s
        """,
        (
            username,
            password
        )
    )

    user = cursor.fetchone()

    conn.close()

    return user


def register_user(
    username,
    email,
    password
):

    conn = psycopg2.connect(
        **DB_CONFIG
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users
        (
            username,
            email,
            password,
            role
        )
        VALUES
        (
            %s,
            %s,
            %s,
            'User'
        )
        """,
        (
            username,
            email,
            password
        )
    )

    conn.commit()

    conn.close()