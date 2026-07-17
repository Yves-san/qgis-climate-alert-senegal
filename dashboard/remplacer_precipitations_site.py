"""
Supprime completement l'ancien precipitation_sum et le remplace par les
vraies donnees journalieres Open-Meteo, limitees a 2025-2050.
"""

import json
import shutil
import unicodedata
import re
from pathlib import Path

import pandas as pd

FICHIER_JSON = Path("projections_2025_2055.json")
FICHIER_CSV = Path("../precipitations_46_communes.csv")


def normaliser(nom):
    nfkd = unicodedata.normalize("NFKD", nom)
    sans_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
    sans_accents = sans_accents.replace("-", " ")
    sans_accents = re.sub(r"\s+", " ", sans_accents)
    return sans_accents.lower().strip()


def main():
    if not FICHIER_JSON.exists():
        print(f"ERREUR : {FICHIER_JSON} introuvable dans le dossier courant.")
        return
    if not FICHIER_CSV.exists():
        print(f"ERREUR : {FICHIER_CSV} introuvable. Ajuste le chemin dans le script.")
        return

    sauvegarde = FICHIER_JSON.with_suffix(".json.bak")
    if not sauvegarde.exists():
        shutil.copy2(FICHIER_JSON, sauvegarde)
        print(f"Sauvegarde creee : {sauvegarde}")
    else:
        print(f"Sauvegarde deja existante ({sauvegarde}), non ecrasee.")

    print("Chargement du CSV des precipitations reelles...")
    df_csv = pd.read_csv(FICHIER_CSV, parse_dates=["date"])
    df_csv["commune_norm"] = df_csv["commune_name"].apply(normaliser)

    print("Chargement du JSON du site (peut prendre un moment, fichier volumineux)...")
    with open(FICHIER_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    communes_json = list(data.keys())
    print(f"{len(communes_json)} communes dans le JSON du site.")

    remplacees = []
    non_trouvees = []

    for nom_json in communes_json:
        nom_norm = normaliser(nom_json)
        sous_ensemble = df_csv[df_csv["commune_norm"] == nom_norm]

        if sous_ensemble.empty:
            non_trouvees.append(nom_json)
            continue

        sous_ensemble = sous_ensemble.sort_values("date")
        dates_reelles = sous_ensemble["date"].dt.strftime("%Y-%m-%d").tolist()
        valeurs_reelles = sous_ensemble["precipitation_sum"].tolist()

        scenarios = data[nom_json].get("scenarios", {})
        for nom_scenario, contenu_scenario in scenarios.items():
            if "precipitation_sum" in contenu_scenario:
                del contenu_scenario["precipitation_sum"]
            contenu_scenario["time_precipitation"] = dates_reelles
            contenu_scenario["precipitation_sum"] = valeurs_reelles

        remplacees.append(nom_json)
        print(f"  {nom_json} -> {len(valeurs_reelles)} jours reels (2025-2050) mis en place")

    print(f"\n{len(remplacees)} commune(s) remplacee(s).")
    if non_trouvees:
        print(f"{len(non_trouvees)} commune(s) NON trouvee(s) dans le CSV :")
        for n in non_trouvees:
            print(f"  - {n}")

    print("\nSauvegarde du JSON modifie...")
    with open(FICHIER_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Termine.")


if __name__ == "__main__":
    main()
