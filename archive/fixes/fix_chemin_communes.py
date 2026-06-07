with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '''    chemins = [
        os.path.join(os.path.dirname(__file__), "..", "data", "communes", "senegal_communes.geojson"),
        os.path.join(os.path.dirname(__file__), "data", "communes", "senegal_communes.geojson"),
        "/sdcard/Documents/qgis-climate-alert-senegal/data/communes/senegal_communes.geojson",
    ]'''

new = '''    chemins = [
        os.path.join(os.path.dirname(__file__), "data", "senegal_communes.geojson"),
        os.path.join(os.path.dirname(__file__), "..", "data", "communes", "senegal_communes.geojson"),
        os.path.join(os.path.dirname(__file__), "data", "communes", "senegal_communes.geojson"),
    ]'''

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done' if old in content else 'TEXTE NON TROUVE')
