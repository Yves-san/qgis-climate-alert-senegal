import json

with open("projections_2025_2055.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("projections_2025_2055.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

print("Recompacte.")
