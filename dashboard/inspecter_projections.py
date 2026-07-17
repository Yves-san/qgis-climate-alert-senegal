import json

with open("projections_2025_2055.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Type racine : {type(data)}")

if isinstance(data, dict):
    print(f"Cles principales : {list(data.keys())[:20]}")
    premiere_cle = list(data.keys())[0]
    print(f"\nExemple ({premiere_cle}) :")
    print(json.dumps(data[premiere_cle], indent=2, ensure_ascii=False)[:2000])
elif isinstance(data, list):
    print(f"Nombre d'elements : {len(data)}")
    print("\nPremier element :")
    print(json.dumps(data[0], indent=2, ensure_ascii=False)[:2000])
