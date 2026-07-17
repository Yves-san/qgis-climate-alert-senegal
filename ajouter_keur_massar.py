import time
import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry

cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

commune = {"id": "DK006", "name": "Keur Massar", "lat": 14.7864, "lon": -17.3119, "region": "Dakar"}

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
print(f"Keur Massar ajoute : {len(df)} jours")
