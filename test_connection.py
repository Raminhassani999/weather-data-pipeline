import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


db_name = os.getenv("POSTGRES_DB")
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
db_host = os.getenv("POSTGRES_HOST", "localhost")
db_port = int(os.getenv("POSTGRES_PORT", "5432"))


if not all([db_name, db_user, db_password]):
    raise ValueError(
        "Missing database configuration. Check your .env file."
    )

with psycopg.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port,
) as conn:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT current_database(), current_user, version();"
        )
        result = cur.fetchone()

        print("POSTGRESQL CONNECTION SUCCESSFUL")
        print(f"Database: {result[0]}")
        print(f"User: {result[1]}")
        print(f"Version: {result[2].split(',')[0]}")
