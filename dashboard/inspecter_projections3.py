import json

with open("projections_2025_2055.json", "r", encoding="utf-8") as f:
    data = json.load(f)

dakar = data["Dakar"]["scenarios"]["SSP1"]
precip = dakar["precipitation_sum"]
temp = dakar["temperature_2m_mean"]
dates = dakar["time"]

print("40 premiers jours de precipitation_sum :")
print(precip[:40])
print("\n40 premiers jours de temperature_2m_mean :")
print(temp[:40])
print(f"\nValeurs uniques sur les 40 premiers jours (precip) : {len(set(precip[:40]))}")
print(f"Valeurs uniques sur les 40 premiers jours (temp) : {len(set(temp[:40]))}")
