import os
import time
import httpx
import pandas as pd
import psycopg
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.open-meteo.com/v1/forecast"

LOCATION = "Messina"
LATITUDE = 38.1938
LONGITUDE = 15.5540

PARAMS = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
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


def extract_weather(max_attempts=5):
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            response = httpx.get(
                API_URL,
                params=PARAMS,
                timeout=30.0,
            )
            response.raise_for_status()

            data = response.json()

            print(
                f"Extracted {len(data['hourly']['time'])} "
                "forecast records."
            )

            return data

        except httpx.HTTPStatusError as exc:
            # Retry rate limits and temporary server errors
            if exc.response.status_code not in {
                429, 500, 502, 503, 504
            }:
                raise

            last_error = exc

        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            last_error = exc

        if attempt < max_attempts:
            delay = 2 ** attempt

            print(
                f"Request failed on attempt {attempt}/{max_attempts}. "
                f"Retrying in {delay} seconds..."
            )

            time.sleep(delay)

    raise RuntimeError(
        f"Open-Meteo request failed after {max_attempts} attempts."
    ) from last_error


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

    df["forecast_time"] = pd.to_datetime(
        df["forecast_time"],
        errors="raise",
    )

    df["location"] = LOCATION
    df["latitude"] = data["latitude"]
    df["longitude"] = data["longitude"]
    df["timezone"] = data["timezone"]

    columns = [
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

    df = df[columns]

    rows = []

    for row in df.itertuples(index=False, name=None):
        clean_row = []

        for value in row:
            if pd.isna(value):
                clean_row.append(None)
            elif isinstance(value, pd.Timestamp):
                clean_row.append(value.to_pydatetime())
            elif hasattr(value, "item"):
                clean_row.append(value.item())
            else:
                clean_row.append(value)

        rows.append(tuple(clean_row))

    print(f"Transformed {len(rows)} records using Pandas.")

    return rows


def load_weather(rows):
    """Load weather records into PostgreSQL."""

    required_settings = [
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ]

    missing_settings = [
        key for key in required_settings
        if not os.getenv(key)
    ]

    if missing_settings:
        raise ValueError(
            f"Missing database settings: {', '.join(missing_settings)}"
        )

    if not rows:
        raise ValueError("No weather records available to load.")

    with psycopg.connect(
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
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
                VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                ON CONFLICT (location, forecast_time)
                DO UPDATE SET
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    timezone = EXCLUDED.timezone,
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
    """Run the complete ETL pipeline."""

    data = extract_weather()
    rows = transform_weather(data)
    load_weather(rows)

    print("WEATHER ETL PIPELINE COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()
