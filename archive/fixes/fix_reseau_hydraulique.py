with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '''    else:
        afficher_section_hydraulique(selected_commune, selected_scenario)'''

new = '''    else:
        import json, os
        _path2 = os.path.join(os.path.dirname("dashboard/app.py"), "dashboard", "data", "senegal_communes.geojson")
        with open(_path2, encoding="utf-8") as _f2:
            _geo2 = json.load(_f2)
        _dept_list2 = sorted([f["properties"]["name"] for f in _geo2["features"]])
        _FONDS2 = {
            "🗺️ OpenStreetMap": "open-street-map",
            "🌙 Sombre (Carto)": "carto-darkmatter",
            "⬜ Clair (Carto)": "carto-positron",
            "🔵 Fond blanc": "white-bg",
        }
        _fond2 = st.selectbox("🗺️ Fond de carte", list(_FONDS2.keys()), key="fond_reseau_select")
        _style2 = _FONDS2[_fond2]
        _dept2 = st.selectbox("🏘️ Département", _dept_list2, key="reseau_dept_select")
        if st.button("🗺️ Afficher la carte de " + _dept2):
            afficher_carte_commune_eau(_dept2, map_style=_style2)'''

if old in content:
    content = content.replace(old, new, 1)
    print('Done')
else:
    print('TEXTE NON TROUVE')

with open('dashboard/app.py', 'w') as f:
    f.write(content)
