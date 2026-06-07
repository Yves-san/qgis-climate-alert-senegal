with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '''    # Zoom adaptatif selon la taille du département
    import math
    lat_range = bbox["maxlat"] - bbox["minlat"]
    lon_range = bbox["maxlon"] - bbox["minlon"]
    max_range = max(lat_range, lon_range)
    if max_range < 0.5: zoom_auto = 10
    elif max_range < 1.0: zoom_auto = 9
    elif max_range < 2.0: zoom_auto = 8
    elif max_range < 4.0: zoom_auto = 7
    else: zoom_auto = 6

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",'''

new = '''    # Sélecteur fond de carte
    FONDS_CARTE = {
        "🗺️ OpenStreetMap": "open-street-map",
        "🌙 Sombre (Carto)": "carto-darkmatter",
        "⬜ Clair (Carto)": "carto-positron",
        "🏔️ Terrain (Stamen)": "stamen-terrain",
        "🖤 Contraste (Stamen)": "stamen-toner",
        "🎨 Aquarelle (Stamen)": "stamen-watercolor",
    }
    fond_choisi = st.selectbox(
        "🗺️ Fond de carte",
        list(FONDS_CARTE.keys()),
        key="fond_carte_select"
    )
    style_carte = FONDS_CARTE[fond_choisi]

    # Zoom adaptatif selon la taille du département
    import math
    lat_range = bbox["maxlat"] - bbox["minlat"]
    lon_range = bbox["maxlon"] - bbox["minlon"]
    max_range = max(lat_range, lon_range)
    if max_range < 0.5: zoom_auto = 10
    elif max_range < 1.0: zoom_auto = 9
    elif max_range < 2.0: zoom_auto = 8
    elif max_range < 4.0: zoom_auto = 7
    else: zoom_auto = 6

    fig.update_layout(
        mapbox=dict(
            style=style_carte,'''

if old in content:
    content = content.replace(old, new, 1)
    print('Done')
else:
    print('TEXTE NON TROUVE')

with open('dashboard/app.py', 'w') as f:
    f.write(content)
