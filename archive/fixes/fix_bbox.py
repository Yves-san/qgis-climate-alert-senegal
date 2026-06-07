with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '    path = os.path.join(os.path.dirname(__file__), "..", "data", "communes", "senegal_communes.geojson")\n    if not os.path.exists(path):\n        return None'

new = '''    chemins = [
        os.path.join(os.path.dirname(__file__), "..", "data", "communes", "senegal_communes.geojson"),
        os.path.join(os.path.dirname(__file__), "data", "communes", "senegal_communes.geojson"),
        "/sdcard/Documents/qgis-climate-alert-senegal/data/communes/senegal_communes.geojson",
    ]
    path = next((p for p in chemins if os.path.exists(p)), None)
    if path is None:
        return None'''

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done' if old in content else 'TEXTE NON TROUVE')
