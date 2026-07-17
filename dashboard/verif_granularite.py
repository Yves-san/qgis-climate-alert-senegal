import pandas as pd

df = pd.read_csv("../precipitations_46_communes.csv")
dakar = df[df["commune_name"] == "Dakar"].sort_values("date")

print("40 premiers jours de precipitation_sum (Dakar, nos donnees) :")
print(dakar["precipitation_sum"].head(40).tolist())

print(f"\nValeurs uniques sur les 40 premiers jours : {dakar['precipitation_sum'].head(40).nunique()}")
print(f"Valeurs uniques sur toute l'annee 2025 : {dakar[dakar['date'].str.startswith('2025')]['precipitation_sum'].nunique()} / 365 jours")
print(f"Valeurs uniques sur les 26 ans (2025-2050) : {dakar['precipitation_sum'].nunique()} / {len(dakar)} jours")
