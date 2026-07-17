import pandas as pd
df = pd.read_csv("precipitations_46_communes.csv")
print(f"Total communes : {df['commune_id'].nunique()}")
print(f"Total lignes : {len(df)}")
