import json, sqlite3

PRECIP_REF_HISTORIQUE = {
    'Dakar': 366, 'Pikine': 366, 'Guediawaye': 366, 'Rufisque': 400, 'Bargny': 380,
    'Thies': 520, 'Mekhe': 480, 'Tivaouane': 490, 'Khombole': 500, 'Mbour': 600,
    'Saint-Louis': 280, 'Dagana': 270, 'Podor': 220, 'Richard-Toll': 260,
    'Louga': 320, 'Kebemer': 370, 'Linguere': 300,
    'Matam': 500, 'Kanel': 450, 'Ranérou': 420,
    'Kaolack': 753, 'Fatick': 720, 'Gossas': 680, 'Foundiougne': 750, 'Nioro du Rip': 750,
    'Diourbel': 600, 'Mbacke': 580, 'Bambey': 600, 'Kaffrine': 721,
    'Tambacounda': 900, 'Bakel': 650, 'Goudiry': 800, 'Koumpentoum': 850,
    'Kolda': 1100, 'Velingara': 1050, 'Medina Yoro Fula': 1000,
    'Ziguinchor': 1400, 'Bignona': 1300, 'Oussouye': 1350,
    'Sedhiou': 1150, 'Bounkiling': 1100, 'Goudomp': 1150,
    'Kedougou': 1300, 'Salemata': 1200, 'Saraya': 1150,
}

with open('dashboard/projections_2025_2055.json') as f:
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
    ref = PRECIP_REF_HISTORIQUE.get(commune_db, 600)
    std_ref = ref * 0.20
    if commune_json not in proj:
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
        for year, total in precip_by_year.items():
            spi = (total - ref) / std_ref
            drought = max(0, min(1, (ref - total) / ref)) if total < ref else 0
            cur.execute("""UPDATE commune_climate_data
                SET drought_index=?, spi_index=?
                WHERE commune_name=? AND scenario=? AND year=? AND resolution='annual'""",
                (round(drought,3), round(spi,3), commune_db, sc_label, int(year)))
            updated += cur.rowcount

conn.commit()
conn.close()
print(f"Mis a jour: {updated} lignes")
