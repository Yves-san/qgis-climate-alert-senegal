import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

cache_session = requests_cache.CachedSession('.cache', expire_after=86400)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

url = "https://climate-api.open-meteo.com/v1/climate"
params = {
    "latitude": 14.5,
    "longitude": -14.25,
    "start_date": "2025-01-01",
    "end_date": "2050-12-31",
    "models": ["CMCC_CM2_VHR4", "FGOALS_f3_H", "HiRAM_SIT_HR", "MRI_AGCM3_2_S", "EC_Earth3P_HR", "MPI_ESM1_2_XR", "NICAM16_8S"],
    "daily": ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min"],
}
model_names = ["CMCC_CM2_VHR4", "FGOALS_f3_H", "HiRAM_SIT_HR", "MRI_AGCM3_2_S", "EC_Earth3P_HR", "MPI_ESM1_2_XR", "NICAM16_8S"]
responses = openmeteo.weather_api(url, params=params)
for i, response in enumerate(responses):
    model = model_names[i]
    print(f"Modele : {model}")
    daily = response.Daily()
    df = pd.DataFrame({
        "date": pd.date_range(start=pd.to_datetime(daily.Time(), unit="s", utc=True), end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True), freq=pd.Timedelta(seconds=daily.Interval()), inclusive="left"),
        "temperature_2m_mean": daily.Variables(0).ValuesAsNumpy(),
        "temperature_2m_max": daily.Variables(1).ValuesAsNumpy(),
        "temperature_2m_min": daily.Variables(2).ValuesAsNumpy(),
    })
    df.to_csv(f"temperature_{model}.csv", index=False)
    print(f"Sauvegarde OK -> temperature_{model}.csv")
