import json
import pandas as pd
import numpy as np
import os

BASE = os.path.dirname(os.path.abspath(__file__))

model_names = ["CMCC_CM2_VHR4", "FGOALS_f3_H", "HiRAM_SIT_HR", "MRI_AGCM3_2_S",
               "EC_Earth3P_HR", "MPI_ESM1_2_XR", "NICAM16_8S"]

print("Chargement des CSV temperatures...")
dfs = []
for m in model_names:
    df = pd.read_csv(os.path.join(BASE, f"temperature_{m}.csv"), parse_dates=["date"])
    df["date"] = df["date"].dt.tz_localize(None).dt.normalize()
    dfs.append(df)

# Moyenne des 7 modeles par jour
df_all = pd.concat(dfs)
df_mean = df_all.groupby("date").agg(
    temp_mean=("temperature_2m_mean", "mean"),
    temp_max=("temperature_2m_max", "mean"),
    temp_min=("temperature_2m_min", "mean"),
).reset_index()
df_mean["date_str"] = df_mean["date"].dt.strftime("%Y-%m-%d")
date_to_row = {row["date_str"]: row for _, row in df_mean.iterrows()}
print(f"Dates disponibles: {df_mean['date_str'].min()} → {df_mean['date_str'].max()}")

print("Chargement du JSON...")
json_path = os.path.join(BASE, "projections_2025_2055.json")
with open(json_path, encoding="utf-8") as f:
    proj = json.load(f)

communes = list(proj.keys())
print(f"Communes: {len(communes)}")

replaced = 0
for commune in communes:
    for sc_key in proj[commune]["scenarios"]:
        sc = proj[commune]["scenarios"][sc_key]
        dates = sc["time"]
        n = len(dates)
        new_mean, new_max, new_min = [], [], []
        for d in dates:
            d_str = d[:10]
            if d_str in date_to_row:
                row = date_to_row[d_str]
                new_mean.append(round(float(row["temp_mean"]), 1))
                new_max.append(round(float(row["temp_max"]), 1))
                new_min.append(round(float(row["temp_min"]), 1))
            else:
                # Garder ancienne valeur si date hors plage
                idx = dates.index(d)
                new_mean.append(sc["temperature_2m_mean"][idx])
                new_max.append(sc["temperature_2m_max"][idx])
                new_min.append(sc["temperature_2m_min"][idx])
        sc["temperature_2m_mean"] = new_mean
        sc["temperature_2m_max"] = new_max
        sc["temperature_2m_min"] = new_min
        replaced += 1

print(f"Scenarios mis a jour: {replaced}")

# Sauvegarde
out_path = os.path.join(BASE, "projections_2025_2055.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(proj, f, ensure_ascii=False, separators=(",", ":"))
print(f"JSON sauvegarde -> {out_path}")

# Verification
with open(out_path, encoding="utf-8") as f:
    verif = json.load(f)
print("Verification Kaolack SSP1 temp_mean 5 premiers:", verif["Kaolack"]["scenarios"]["SSP1"]["temperature_2m_mean"][:5])
