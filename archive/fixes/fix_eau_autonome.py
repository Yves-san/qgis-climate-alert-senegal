with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '    st.markdown("### 🗺️ Carte hydraulique de " + selected_commune)\n    st.caption("Reseau hydraulique + forages PNADT filtrés pour la commune selectionnee")\n    if st.button("🗺️ Afficher la carte de " + selected_commune):\n        afficher_carte_commune_eau(selected_commune)'

new = '''    st.markdown("### 🗺️ Carte hydraulique par département")
    st.caption("Reseau hydraulique + forages PNADT filtrés pour la commune selectionnee")
    import json, os
    _path = os.path.join(os.path.dirname(__file__), "data", "senegal_communes.geojson")
    with open(_path, encoding="utf-8") as _f:
        _geo = json.load(_f)
    _dept_list = sorted([f["properties"]["name"] for f in _geo["features"]])
    _dept_sel = st.selectbox("🏘️ Département", _dept_list, key="eau_dept_select")
    if st.button("🗺️ Afficher la carte de " + _dept_sel):
        afficher_carte_commune_eau(_dept_sel)'''

if old in content:
    content = content.replace(old, new, 1)
    print('Done')
else:
    print('TEXTE NON TROUVE')

with open('dashboard/app.py', 'w') as f:
    f.write(content)
