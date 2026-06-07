with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '''        import json as __jh
        import os as __osh
        chemin_hydro = __osh.path.join(__osh.path.dirname(__file__), "..", "data", "hydrographie_sn.geojson")
        if not __osh.path.exists(chemin_hydro):
            chemin_hydro = __osh.path.join(__osh.path.dirname(__file__), "data", "hydrographie_sn.geojson")
        with open(chemin_hydro, encoding="utf-8") as __fh:
            gj_hydro = __jh.load(__fh)'''

new = '        gj_hydro = charger_hydrographie()'

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done' if old in content else 'TEXTE NON TROUVE')

with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '''    if __os2.path.exists(chemin_forages):
        with open(chemin_forages, encoding="utf-8") as __f2:
            forages_gj = __json2.load(__f2)'''

new = '    forages_gj = charger_forages()\n    if forages_gj is not None:'

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done2' if old in content else 'TEXTE2 NON TROUVE')
