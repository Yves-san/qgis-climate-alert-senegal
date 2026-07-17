"""
Recupere les precipitations projetees (2025-2050) pour les 46 communes du
Senegal via l'Open-Meteo Climate API, avec un seul modele (MRI_AGCM3_2_S).
"""

import time
from pathlib import Path

import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry

MODELE = "MRI_AGCM3_2_S"
VARIABLES = ["precipitation_sum"]
DATE_DEBUT = "2025-01-01"
DATE_FIN = "2050-12-31"
PAUSE_ENTRE_APPELS = 2
FICHIER_SORTIE = Path("precipitations_46_communes.csv")

SENEGAL_COMMUNES = {
    "Dakar": [
        {"id": "DK001", "name": "Dakar", "lat": 14.6928, "lon": -17.0407},
        {"id": "DK002", "name": "Pikine", "lat": 14.7667, "lon": -17.1500},
        {"id": "DK003", "name": "Guediawaye", "lat": 14.7550, "lon": -17.2850},
        {"id": "DK004", "name": "Rufisque", "lat": 14.7167, "lon": -17.2667},
        {"id": "DK005", "name": "Bargny", "lat": 14.6942, "lon": -17.2311},
    ],
    "Thies": [
        {"id": "TH001", "name": "Thies", "lat": 14.7861, "lon": -16.9203},
        {"id": "TH002", "name": "Mbour", "lat": 14.3917, "lon": -16.7250},
        {"id": "TH003", "name": "Tivaouane", "lat": 14.9500, "lon": -16.8333},
        {"id": "TH004", "name": "Meckhe", "lat": 14.8833, "lon": -16.4167},
        {"id": "TH005", "name": "Khombole", "lat": 14.7500, "lon": -16.7000},
    ],
    "Saint-Louis": [
        {"id": "SL001", "name": "Saint-Louis", "lat": 16.0167, "lon": -16.4833},
        {"id": "SL002", "name": "Podor", "lat": 16.6500, "lon": -15.2000},
        {"id": "SL003", "name": "Dagana", "lat": 16.4000, "lon": -15.7667},
        {"id": "SL004", "name": "Richard-Toll", "lat": 16.4628, "lon": -15.7022},
    ],
    "Kaolack": [
        {"id": "KL001", "name": "Kaolack", "lat": 13.9667, "lon": -16.0167},
        {"id": "KL002", "name": "Kaffrine", "lat": 14.1056, "lon": -15.5506},
        {"id": "KL003", "name": "Nioro du Rip", "lat": 13.7500, "lon": -15.7833},
    ],
    "Ziguinchor": [
        {"id": "ZG001", "name": "Ziguinchor", "lat": 12.5589, "lon": -16.2719},
        {"id": "ZG002", "name": "Bignona", "lat": 12.8101, "lon": -16.2244},
        {"id": "ZG003", "name": "Oussouye", "lat": 12.4844, "lon": -16.5464},
    ],
    "Tambacounda": [
        {"id": "TC001", "name": "Tambacounda", "lat": 13.7719, "lon": -13.7731},
        {"id": "TC002", "name": "Bakel", "lat": 14.9000, "lon": -12.4667},
        {"id": "TC003", "name": "Goudiry", "lat": 14.1833, "lon": -12.7333},
        {"id": "TC004", "name": "Koumpentoum", "lat": 13.9833, "lon": -14.5500},
    ],
    "Louga": [
        {"id": "LG001", "name": "Louga", "lat": 15.6167, "lon": -16.2333},
        {"id": "LG002", "name": "Linguere", "lat": 15.3833, "lon": -15.1167},
        {"id": "LG003", "name": "Kebemer", "lat": 15.3617, "lon": -16.4489},
    ],
    "Matam": [
        {"id": "MT001", "name": "Matam", "lat": 15.6558, "lon": -13.2550},
        {"id": "MT002", "name": "Kanel", "lat": 15.4844, "lon": -13.1747},
        {"id": "MT003", "name": "Ranerou", "lat": 15.2972, "lon": -13.9625},
    ],
    "Kolda": [
        {"id": "KD001", "name": "Kolda", "lat": 12.8978, "lon": -14.9408},
        {"id": "KD002", "name": "Velingara", "lat": 13.1500, "lon": -14.1167},
        {"id": "KD003", "name": "Medina Yoro Foulah", "lat": 13.0500, "lon": -14.5000},
    ],
    "Sedhiou": [
        {"id": "SD001", "name": "Sedhiou", "lat": 12.7072, "lon": -15.5572},
        {"id": "SD002", "name": "Goudomp", "lat": 12.5783, "lon": -15.8672},
        {"id": "SD003", "name": "Bounkiling", "lat": 13.0500, "lon": -15.6833},
    ],
    "Kedougou": [
        {"id": "KG001", "name": "Kedougou", "lat": 12.5553, "lon": -12.1747},
        {"id": "KG002", "name": "Saraya", "lat": 12.8333, "lon": -11.7500},
        {"id": "KG003", "name": "Salekata", "lat": 12.6833, "lon": -12.7667},
    ],
    "Fatick": [
        {"id": "FK001", "name": "Fatick", "lat": 14.3392, "lon": -16.4122},
        {"id": "FK002", "name": "Gossas", "lat": 14.5197, "lon": -16.0564},
        {"id": "FK003", "name": "Foundiougne", "lat": 14.1333, "lon": -16.4667},
        {"id": "FK004", "name": "Sokone", "lat": 13.8833, "lon": -16.3667},
    ],
    "Diourbel": [
        {"id": "DB001", "name": "Diourbel", "lat": 14.6553, "lon": -16.2300},
        {"id": "DB002", "name": "Bambey", "lat": 14.7000, "lon": -16.4500},
        {"id": "DB003", "name": "Mbacke", "lat": 14.7947, "lon": -15.9103},
    ],
}


def toutes_les_communes():
    result = []
    for region, communes in SENEGAL_COMMUNES.items():
        for c in communes:
            d = dict(c)
            d["region"] = region
            result.append(d)
    return result


def charger_deja_faites():
    if not FICHIER_SORTIE.exists():
        return set()
    df = pd.read_csv(FICHIER_SORTIE)
    return set(df["commune_id"].unique())


def recuperer_precipitations(openmeteo_client, commune):
    params = {
        "latitude": commune["lat"],
        "longitude": commune["lon"],
        "start_date": DATE_DEBUT,
        "end_date": DATE_FIN,
        "models": [MODELE],
        "daily": VARIABLES,
    }
    responses = openmeteo_client.weather_api(
        "https://climate-api.open-meteo.com/v1/climate", params=params
    )
    response = responses[0]
    daily = response.Daily()

    dates = pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left",
    )

    df = pd.DataFrame({"date": dates})
    for i, var in enumerate(VARIABLES):
        df[var] = daily.Variables(i).ValuesAsNumpy()

    df.insert(0, "commune_id", commune["id"])
    df.insert(1, "commune_name", commune["name"])
    df.insert(2, "region", commune["region"])
    return df


def main():
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    communes = toutes_les_communes()
    deja_faites = charger_deja_faites()
    if deja_faites:
        print(f"{len(deja_faites)} commune(s) deja presente(s), ignorees.")

    restantes = [c for c in communes if c["id"] not in deja_faites]
    print(f"{len(restantes)} commune(s) a traiter sur {len(communes)}.")

    ecrire_entete = not FICHIER_SORTIE.exists()

    for i, commune in enumerate(restantes, 1):
        print(f"[{i}/{len(restantes)}] {commune['name']} ({commune['region']})...", end=" ")
        try:
            df = recuperer_precipitations(openmeteo, commune)
            df.to_csv(FICHIER_SORTIE, mode="a", header=ecrire_entete, index=False)
            ecrire_entete = False
            print(f"OK ({len(df)} jours)")
        except Exception as e:
            print(f"ECHEC : {e}")

        if i < len(restantes):
            time.sleep(PAUSE_ENTRE_APPELS)

    print(f"Termine. Resultats dans {FICHIER_SORTIE}")


if __name__ == "__main__":
    main()
