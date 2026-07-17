import pandas as pd
df = pd.read_csv("precipitations_46_communes.csv")
resultat = df.groupby("commune_name").agg(
    total_jours=("precipitation_sum", "size"),
    valeurs_valides=("precipitation_sum", lambda x: x.notna().sum())
)
resultat["pourcentage"] = (resultat["valeurs_valides"] / resultat["total_jours"] * 100).round(2)
pd.set_option("display.max_rows", None)
print(resultat.sort_values("pourcentage"))
print()
print(f"Minimum: {resultat['pourcentage'].min()}%")
print(f"Maximum: {resultat['pourcentage'].max()}%")
print(f"Moyenne: {resultat['pourcentage'].mean().round(2)}%")
