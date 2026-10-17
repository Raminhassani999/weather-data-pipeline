import httpx

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

response = httpx.get(
    url,
    params=params,
    timeout=30.0,
)

response.raise_for_status()

data = response.json()

hourly = data["hourly"]

print("WEATHER API REQUEST SUCCESSFUL")
print(f"Timezone: {data['timezone']}")
print(f"Latitude: {data['latitude']}")
print(f"Longitude: {data['longitude']}")
print(f"Forecast records: {len(hourly['time'])}")

print("\nWEATHER UNITS")
print(data["hourly_units"])

print("\nFIRST THREE HOURLY RECORDS")

for i in range(min(3, len(hourly["time"]))):
    record = {
        column: values[i]
        for column, values in hourly.items()
    }

    print(record)
