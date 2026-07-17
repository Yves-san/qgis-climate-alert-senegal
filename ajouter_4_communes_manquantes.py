import time
import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry

cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

communes_manquantes = [
    {"id": "KL004", "name": "Birkelane", "lat": 14.1500, "lon": -15.7500, "region": "Kaolack"},
    {"id": "KL005", "name": "Guinguineo", "lat": 14.2667, "lon": -15.9500, "region": "Kaolack"},
    {"id": "KL006", "name": "Koungheul", "lat": 13.9833, "lon": -14.8000, "region": "Kaolack"},
    {"id": "KL007", "name": "Malem Hodar", "lat": 14.0883, "lon": -15.2944, "region": "Kaolack"},
]

for i, commune in enumerate(communes_manquantes):
    print(f"[{i+1}/{len(communes_manquantes)}] {commune['name']}...", end=" ")
    params = {
        "latitude": commune["lat"],
        "longitude": commune["lon"],
        "start_date": "2025-01-01",
        "end_date": "2050-12-31",
        "models": ["MRI_AGCM3_2_S"],
        "daily": ["precipitation_sum"],
    }
    responses = openmeteo.weather_api("https://climate-api.open-meteo.com/v1/climate", params=params)
    response = responses[0]
    daily = response.Daily()

    dates = pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left",
    )
    df = pd.DataFrame({"date": dates})
    df["precipitation_sum"] = daily.Variables(0).ValuesAsNumpy()
    df.insert(0, "commune_id", commune["id"])
    df.insert(1, "commune_name", commune["name"])
    df.insert(2, "region", commune["region"])

    df.to_csv("precipitations_46_communes.csv", mode="a", header=False, index=False)
    print(f"OK ({len(df)} jours)")

    if i < len(communes_manquantes) - 1:
        time.sleep(6)

print("Termine.")
