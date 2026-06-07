with open('dashboard/app.py', 'r') as f:
    content = f.read()

# 1. Remplacer l'appel avec bouton par sélecteur fond + appel direct
old1 = '''    _dept_sel = st.selectbox("🏘️ Département", _dept_list, key="eau_dept_select")
    if st.button("🗺️ Afficher la carte de " + _dept_sel):
        afficher_carte_commune_eau(_dept_sel)'''

new1 = '''    _dept_sel = st.selectbox("🏘️ Département", _dept_list, key="eau_dept_select")
    _FONDS = {
        "🗺️ OpenStreetMap": "open-street-map",
        "🌙 Sombre (Carto)": "carto-darkmatter",
        "⬜ Clair (Carto)": "carto-positron",
        "🏔️ Terrain (Stamen)": "stamen-terrain",
        "🖤 Contraste (Stamen)": "stamen-toner",
        "🎨 Aquarelle (Stamen)": "stamen-watercolor",
    }
    _fond_choisi = st.selectbox("🗺️ Fond de carte", list(_FONDS.keys()), key="fond_carte_select")
    _style = _FONDS[_fond_choisi]
    if st.button("🗺️ Afficher la carte de " + _dept_sel):
        afficher_carte_commune_eau(_dept_sel, map_style=_style)'''

if old1 in content:
    content = content.replace(old1, new1, 1)
    print('Appel: Done')
else:
    print('Appel: TEXTE NON TROUVE')

# 2. Modifier la signature de la fonction
old2 = 'def afficher_carte_commune_eau(commune_name):'
new2 = 'def afficher_carte_commune_eau(commune_name, map_style="open-street-map"):'

if old2 in content:
    content = content.replace(old2, new2, 1)
    print('Signature: Done')
else:
    print('Signature: TEXTE NON TROUVE')

# 3. Supprimer l'ancien sélecteur dans la fonction
old3 = '''    # Sélecteur fond de carte
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

    # Zoom adaptatif'''

new3 = '    # Zoom adaptatif'

if old3 in content:
    content = content.replace(old3, new3, 1)
    print('Selectbox interne: Done')
else:
    print('Selectbox interne: TEXTE NON TROUVE')

# 4. Utiliser map_style au lieu de style_carte
old4 = '            style=style_carte,'
new4 = '            style=map_style,'

if old4 in content:
    content = content.replace(old4, new4, 1)
    print('Style: Done')
else:
    print('Style: TEXTE NON TROUVE')

with open('dashboard/app.py', 'w') as f:
    f.write(content)
