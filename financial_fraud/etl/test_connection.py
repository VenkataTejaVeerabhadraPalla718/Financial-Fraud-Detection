from sqlalchemy import create_engine

try:
    engine = create_engine(
        "postgresql://postgres:Bhadra%407879@localhost:5432/fraud_db"
    )

    conn = engine.connect()

    print("PostgreSQL Connected Successfully")

    conn.close()

except Exception as e:
    print("Connection Error")
    print(e)