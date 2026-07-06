import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="fraud_db",
    user="postgres",
    password="Bhadra@7879"
)

cursor = conn.cursor()

print("PostgreSQL Connected Successfully")