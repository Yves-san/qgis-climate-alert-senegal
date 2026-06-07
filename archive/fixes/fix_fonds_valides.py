with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '''    _FONDS = {
        "🗺️ OpenStreetMap": "open-street-map",
        "🌙 Sombre (Carto)": "carto-darkmatter",
        "⬜ Clair (Carto)": "carto-positron",
        "🏔️ Terrain (Stamen)": "stamen-terrain",
        "🖤 Contraste (Stamen)": "stamen-toner",
        "🎨 Aquarelle (Stamen)": "stamen-watercolor",
    }'''

new = '''    _FONDS = {
        "🗺️ OpenStreetMap": "open-street-map",
        "🌙 Sombre (Carto)": "carto-darkmatter",
        "⬜ Clair (Carto)": "carto-positron",
        "🔵 Fond blanc": "white-bg",
    }'''

if old in content:
    content = content.replace(old, new, 1)
    print('Done')
else:
    print('TEXTE NON TROUVE')

with open('dashboard/app.py', 'w') as f:
    f.write(content)
