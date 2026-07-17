import json

with open("projections_2025_2055.json", "r", encoding="utf-8") as f:
    data = json.load(f)

if "Mékhe" in data and "Méckhé" not in data:
    import pandas as pd
    df_csv = pd.read_csv("../precipitations_46_communes.csv", parse_dates=["date"])
    meckhe = df_csv[df_csv["commune_name"] == "Meckhe"].sort_values("date")
    dates_reelles = meckhe["date"].dt.strftime("%Y-%m-%d").tolist()
    valeurs_reelles = meckhe["precipitation_sum"].tolist()

    scenarios = data["Mékhe"]["scenarios"]
    for nom_scenario, contenu_scenario in scenarios.items():
        if "precipitation_sum" in contenu_scenario:
            del contenu_scenario["precipitation_sum"]
        contenu_scenario["time_precipitation"] = dates_reelles
        contenu_scenario["precipitation_sum"] = valeurs_reelles

    with open("projections_2025_2055.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Mekhe -> {len(valeurs_reelles)} jours reels mis en place")
else:
    print("Rien a faire (deja fait ou cle absente)")
