import json, sqlite3, os

path = 'dashboard/projections_2025_2055.json'
with open(path) as f:
    proj = json.load(f)

mapping = {
    'Kebemer': 'Kébémer', 'Kedougou': 'Kédougou', 'Linguere': 'Linguère',
    'Mbacke': 'Mbacké', 'Medina Yoro Fula': 'Médina Yoro Foulah',
    'Mekhe': 'Mékhe', 'Sedhiou': 'Sédhiou', 'Thies': 'Thiès',
    'Velingara': 'Vélingara', 'Salemata': 'Salékata',
}

conn = sqlite3.connect('dashboard/demo_climate.db')
cur = conn.cursor()
sc_map = {"SSP1-1.9":"SSP1", "SSP2-4.5":"SSP2", "SSP5-8.5":"SSP5"}
updated = 0

cur.execute("SELECT DISTINCT commune_name FROM commune_climate_data")
communes_db = [r[0] for r in cur.fetchall()]

for commune_db in communes_db:
    commune_json = mapping.get(commune_db, commune_db)
    if commune_json not in proj:
        print(f"Absent: {commune_db}")
        continue
    for sc_label, sc_key in sc_map.items():
        if sc_key not in proj[commune_json]['scenarios']:
            continue
        ssp = proj[commune_json]['scenarios'][sc_key]
        times = ssp['time']
        precip = ssp['precipitation_sum']
        precip_by_year = {}
        for t, p in zip(times, precip):
            y = t[:4]
            precip_by_year[y] = precip_by_year.get(y, 0) + p
        all_totals = list(precip_by_year.values())
        ref = sum(all_totals) / len(all_totals)
        std_ref = (sum((x-ref)**2 for x in all_totals)/len(all_totals))**0.5
        if std_ref == 0:
            std_ref = ref * 0.15
        for year, total in precip_by_year.items():
            spi = (total - ref) / std_ref
            drought = max(0, min(1, (ref - total) / ref)) if total < ref else 0
            cur.execute("""UPDATE commune_climate_data
                SET drought_index=?, spi_index=?
                WHERE commune_name=? AND scenario=? AND year=? AND resolution='annual'""",
                (round(drought, 3), round(spi, 3), commune_db, sc_label, int(year)))
            updated += cur.rowcount

conn.commit()
conn.close()
print(f"Mis a jour: {updated} lignes")
