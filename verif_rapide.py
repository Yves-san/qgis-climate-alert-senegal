import pandas as pd
df = pd.read_csv("precipitations_46_communes.csv")
print(f"Lignes: {len(df)}")
print(f"Communes uniques: {df['commune_id'].nunique()}")
print(df.groupby("commune_id").size().describe())
