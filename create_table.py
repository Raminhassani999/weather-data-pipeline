import os
from pathlib import Path
import psycopg
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

with psycopg.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5433")),
) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS weather_forecast (
                location TEXT NOT NULL,
                forecast_time TIMESTAMP NOT NULL,
                latitude DOUBLE PRECISION NOT NULL,
                longitude DOUBLE PRECISION NOT NULL,
                timezone TEXT NOT NULL,
                temperature_c DOUBLE PRECISION,
                humidity_percent SMALLINT,
                apparent_temperature_c DOUBLE PRECISION,
                precipitation_mm DOUBLE PRECISION,
                weather_code INTEGER,
                wind_speed_kmh DOUBLE PRECISION,
                fetched_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

                PRIMARY KEY (location, forecast_time)
            );
        """)

print("Weather table created or already exists.")