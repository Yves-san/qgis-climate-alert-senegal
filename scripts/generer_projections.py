import json
import os
from datetime import date, timedelta

# Tendances CMIP6 pour le Sénégal par zone
ZONES = {
    "Nord": {
        "communes": ["Louga", "Linguère", "Kébémer", "Podor", "Dagana", 
                     "Richard-Toll", "Saint-Louis", "Ranérou"],
        "SSP1": {"temp": +1.2, "precip": -0.10, "vent": +0.05},
        "SSP2": {"temp": +2.1, "precip": -0.18, "vent": +0.08},
        "SSP5": {"temp": +3.5, "precip": -0.28, "vent": +0.12},
    },
    "Centre": {
        "communes": ["Diourbel", "Bambey", "Mbacké", "Kaolack", "Kaffrine",
                     "Gossas", "Nioro du Rip", "Fatick", "Foundiougne", 
                     "Sokone", "Thiès", "Mbour", "Tivaouane", "Mékhe", 
                     "Khombole", "Dakar", "Pikine", "Guediawaye", 
                     "Rufisque", "Bargny"],
        "SSP1": {"temp": +1.0, "precip": -0.08, "vent": +0.04},
        "SSP2": {"temp": +1.8, "precip": -0.14, "vent": +0.07},
        "SSP5": {"temp": +3.0, "precip": -0.22, "vent": +0.10},
    },
    "Fleuve": {
        "communes": ["Matam", "Kanel", "Bakel"],
        "SSP1": {"temp": +1.3, "precip": -0.12, "vent": +0.05},
        "SSP2": {"temp": +2.3, "precip": -0.15, "vent": +0.09},
        "SSP5": {"temp": +3.8, "precip": -0.25, "vent": +0.13},
    },
    "Est": {
        "communes": ["Tambacounda", "Goudiry", "Koumpentoum", 
                     "Kédougou", "Saraya", "Salékata"],
        "SSP1": {"temp": +1.1, "precip": -0.07, "vent": +0.04},
        "SSP2": {"temp": +1.9, "precip": -0.12, "vent": +0.07},
        "SSP5": {"temp": +3.2, "precip": -0.20, "vent": +0.11},
    },
    "Sud": {
        "communes": ["Kolda", "Vélingara", "Médina Yoro Foulah",
                     "Sédhiou", "Goudomp", "Bounkiling", "Ziguinchor",
                     "Bignona", "Oussouye"],
        "SSP1": {"temp": +0.9, "precip": -0.05, "vent": +0.03},
        "SSP2": {"temp": +1.5, "precip": -0.08, "vent": +0.06},
        "SSP5": {"temp": +2.5, "precip": -0.15, "vent": +0.09},
    },
}

def get_zone_tendance(commune, scenario):
    for zone, info in ZONES.items():
        if commune in info["communes"]:
            return info[scenario]
    return ZONES["Centre"][scenario]

# Charger données réelles
with open("dashboard/data/journalier/climate_journalier.json") as f:
    donnees_reelles = json.load(f)

os.makedirs("dashboard/data/projections", exist_ok=True)

projections = {}

for commune, data in donnees_reelles.items():
    print(f"⏳ Projection {commune}...", end=" ", flush=True)
    projections[commune] = {
        "lat": data["lat"],
        "lon": data["lon"],
        "scenarios": {}
    }

    daily = data["daily"]
    n_jours = len(daily["time"])

    # Moyenne de référence 2000-2024
    temps_ref = [t for t in daily["temperature_2m_mean"] if t is not None]
    precip_ref = [p for p in daily["precipitation_sum"] if p is not None]
    vent_ref = [v for v in daily["windspeed_10m_max"] if v is not None]

    temp_moy = sum(temps_ref) / len(temps_ref)
    precip_moy = sum(precip_ref) / len(precip_ref)
    vent_moy = sum(vent_ref) / len(vent_ref)

    for scenario in ["SSP1", "SSP2", "SSP5"]:
        tendance = get_zone_tendance(commune, scenario)
        delta_temp = tendance["temp"]
        delta_precip = tendance["precip"]
        delta_vent = tendance["vent"]

        dates = []
        temp_mean = []
        temp_max = []
        temp_min = []
        precip = []
        eto = []
        vent = []

        # Générer chaque jour 2025-2055
        debut = date(2025, 1, 1)
        fin = date(2055, 12, 31)
        jour = debut
        annee_debut = 2025
        annee_fin = 2055
        total_ans = annee_fin - annee_debut

        while jour <= fin:
            # Progression linéaire de la tendance
            progression = (jour.year - annee_debut) / total_ans

            # Trouver le jour équivalent dans les données réelles
            # (même mois/jour, année aléatoire dans 2000-2024)
            mois = jour.month
            day = jour.day

            # Moyenne du même mois dans les données réelles
            vals_mois = []
            for i, t in enumerate(daily["time"]):
                if t[5:7] == f"{mois:02d}":
                    if daily["temperature_2m_mean"][i] is not None:
                        vals_mois.append({
                            "temp_mean": daily["temperature_2m_mean"][i],
                            "temp_max": daily["temperature_2m_max"][i] or 0,
                            "temp_min": daily["temperature_2m_min"][i] or 0,
                            "precip": daily["precipitation_sum"][i] or 0,
                            "eto": daily["et0_fao_evapotranspiration"][i] or 0,
                            "vent": daily["windspeed_10m_max"][i] or 0,
                        })

            if vals_mois:
                n = len(vals_mois)
                base_temp = sum(v["temp_mean"] for v in vals_mois) / n
                base_tmax = sum(v["temp_max"] for v in vals_mois) / n
                base_tmin = sum(v["temp_min"] for v in vals_mois) / n
                base_p = sum(v["precip"] for v in vals_mois) / n
                base_e = sum(v["eto"] for v in vals_mois) / n
                base_v = sum(v["vent"] for v in vals_mois) / n
            else:
                base_temp = temp_moy
                base_tmax = temp_moy + 4
                base_tmin = temp_moy - 4
                base_p = precip_moy
                base_e = 5.0
                base_v = vent_moy

            # Appliquer tendance progressive
            dates.append(str(jour))
            temp_mean.append(round(base_temp + delta_temp * progression, 1))
            temp_max.append(round(base_tmax + delta_temp * progression, 1))
            temp_min.append(round(base_tmin + delta_temp * progression, 1))
            precip.append(round(max(0, base_p * (1 + delta_precip * progression)), 2))
            eto.append(round(base_e * (1 + 0.05 * progression), 2))
            vent.append(round(base_v * (1 + delta_vent * progression), 1))

            jour += timedelta(days=1)

        projections[commune]["scenarios"][scenario] = {
            "time": dates,
            "temperature_2m_mean": temp_mean,
            "temperature_2m_max": temp_max,
            "temperature_2m_min": temp_min,
            "precipitation_sum": precip,
            "et0_fao_evapotranspiration": eto,
            "windspeed_10m_max": vent,
        }

    print(f"✅")

# Sauvegarder
with open("dashboard/data/projections/projections_2025_2055.json", "w") as f:
    json.dump(projections, f)

print(f"\n✅ Projections générées pour {len(projections)} communes !")
print(f"Période : 2025-2055 (11323 jours)")
print(f"Scénarios : SSP1, SSP2, SSP5")
print(f"Variables : 6 par jour par commune")
