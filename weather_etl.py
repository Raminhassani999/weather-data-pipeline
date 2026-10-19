import os
import httpx
import pandas as pd
import psycopg
from dotenv import load_dotenv


load_dotenv()


url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 38.1938,
    "longitude": 15.5540,
    "hourly": (
        "temperature_2m,"
        "relative_humidity_2m,"
        "apparent_temperature,"
        "precipitation,"
        "weather_code,"
        "wind_speed_10m"
    ),
    "forecast_hours": 24,
    "timezone": "Europe/Rome",
}

location = "Messina"


def extract_weather():
    response = httpx.get(url, params=params, timeout=30.0)
    response.raise_for_status()

    data = response.json()

    print("Weather data extracted successfully.")
    return data



def transform_weather(data):
    
    df = pd.DataFrame(data["hourly"])

    df = df.rename(columns={
        "time": "forecast_time",
        "temperature_2m": "temperature_c",
        "relative_humidity_2m": "humidity_percent",
        "apparent_temperature": "apparent_temperature_c",
        "precipitation": "precipitation_mm",
        "wind_speed_10m": "wind_speed_kmh",
    })

    df["forecast_time"] = pd.to_datetime(df["forecast_time"])

    df["location"] = location
    df["latitude"] = data["latitude"]
    df["longitude"] = data["longitude"]
    df["timezone"] = data["timezone"]

    df = df[
        [
            "location",
            "forecast_time",
            "latitude",
            "longitude",
            "timezone",
            "temperature_c",
            "humidity_percent",
            "apparent_temperature_c",
            "precipitation_mm",
            "weather_code",
            "wind_speed_kmh",
        ]
    ]


    df = df.astype(object).where(pd.notna(df), None)

    rows = []

    for row in df.itertuples(index=False, name=None):
        clean_row = []

        for value in row:
            if pd.isna(value):
                value = None
            elif isinstance(value, pd.Timestamp):
                value = value.to_pydatetime()
            elif hasattr(value, "item"):
                value = value.item()

            clean_row.append(value)

        rows.append(tuple(clean_row))

    print(f"Transformed {len(rows)} records using Pandas.")
    return rows

def load_weather(rows):
    with psycopg.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5433")),
    ) as conn:

        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO weather_forecast (
                    location,
                    forecast_time,
                    latitude,
                    longitude,
                    timezone,
                    temperature_c,
                    humidity_percent,
                    apparent_temperature_c,
                    precipitation_mm,
                    weather_code,
                    wind_speed_kmh
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

                ON CONFLICT (location, forecast_time)
                DO UPDATE SET
                    temperature_c = EXCLUDED.temperature_c,
                    humidity_percent = EXCLUDED.humidity_percent,
                    apparent_temperature_c = EXCLUDED.apparent_temperature_c,
                    precipitation_mm = EXCLUDED.precipitation_mm,
                    weather_code = EXCLUDED.weather_code,
                    wind_speed_kmh = EXCLUDED.wind_speed_kmh,
                    fetched_at = CURRENT_TIMESTAMP;
                """,
                rows,
            )

    print(f"Loaded {len(rows)} records into PostgreSQL.")

def main():
    data = extract_weather()
    rows = transform_weather(data)
    load_weather(rows)

    print("ETL PIPELINE COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()
