import sqlite3

CORRECTIONS = {
    'Kaolack': 600,
    'Kaffrine': 650,
    'Gossas': 580,
    'Nioro du Rip': 700,
    'Foundiougne': 680,
}

conn = sqlite3.connect('dashboard/demo_climate.db')
cur = conn.cursor()

for commune, ref in CORRECTIONS.items():
    std_ref = ref * 0.20
    cur.execute("""SELECT scenario, year, spi_index FROM commune_climate_data
                   WHERE commune_name=? AND resolution='annual'""", (commune,))
    rows = cur.fetchall()
    for sc, year, old_spi in rows:
        cur.execute("""SELECT spi_index FROM commune_climate_data
                       WHERE commune_name=? AND scenario=? AND year=? AND resolution='annual'""",
                   (commune, sc, year))
        pass

import json
with open('dashboard/projections_2025_2055.json') as f:
    proj = json.load(f)

sc_map = {"SSP1-1.9":"SSP1", "SSP2-4.5":"SSP2", "SSP5-8.5":"SSP5"}

for commune_db, ref in CORRECTIONS.items():
    std_ref = ref * 0.20
    commune_json = commune_db
    if commune_json not in proj:
        continue
    for sc_label, sc_key in sc_map.items():
        if sc_key not in proj[commune_json]['scenarios']:
            continue
        ssp = proj[commune_json]['scenarios'][sc_key]
        precip_by_year = {}
        for t, p in zip(ssp['time'], ssp['precipitation_sum']):
            y = t[:4]
            precip_by_year[y] = precip_by_year.get(y, 0) + p
        for year, total in precip_by_year.items():
            spi = (total - ref) / std_ref
            drought = max(0, min(1, (ref - total) / ref)) if total < ref else 0
            cur.execute("""UPDATE commune_climate_data
                SET drought_index=?, spi_index=?
                WHERE commune_name=? AND scenario=? AND year=? AND resolution='annual'""",
                (round(drought,3), round(spi,3), commune_db, sc_label, int(year)))
        print(f"{commune_db}: ref={ref}mm mis a jour")

conn.commit()
conn.close()
print("Done")
