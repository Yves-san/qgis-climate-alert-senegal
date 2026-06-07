with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '        fig_sup = go.Figure()\n        for feat in gj_hydro["features"]:'

new = '''        import json as __jh
        import os as __osh
        chemin_hydro = __osh.path.join(__osh.path.dirname(__file__), "..", "data", "hydrographie_sn.geojson")
        if not __osh.path.exists(chemin_hydro):
            chemin_hydro = __osh.path.join(__osh.path.dirname(__file__), "data", "hydrographie_sn.geojson")
        with open(chemin_hydro, encoding="utf-8") as __fh:
            gj_hydro = __jh.load(__fh)
        fig_sup = go.Figure()
        for feat in gj_hydro["features"]:'''

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done' if old in content else 'TEXTE NON TROUVE')
