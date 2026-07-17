import json

with open("projections_2025_2055.json", "r", encoding="utf-8") as f:
    data = json.load(f)

dakar = data["Dakar"]
print("Scenarios disponibles :", list(dakar["scenarios"].keys()))

ssp1 = dakar["scenarios"]["SSP1"]
print("\nCles dans SSP1 :", list(ssp1.keys()))

for cle in ssp1.keys():
    if cle != "time":
        valeurs = ssp1[cle]
        print(f"\n{cle} - 5 premieres valeurs :", valeurs[:5])
