with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '    st.markdown("### 🗺️ Carte des 4218 forages officiels du Sénégal")\n    st.caption("Source : Base de données PNADT — Programme National d Aménagement du Territoire")\n    if st.button("🗺️ Afficher la carte des forages (peut prendre quelques secondes)"):\n        afficher_carte_forages()'

new = '''    st.markdown("### 🗺️ Carte hydraulique de " + selected_commune)
    st.caption("Reseau hydraulique + forages PNADT filtrés pour la commune selectionnee")
    if st.button("🗺️ Afficher la carte de " + selected_commune):
        afficher_carte_commune_eau(selected_commune)
    st.markdown("---")
    st.markdown("### 🗺️ Carte des 4218 forages officiels du Sénégal")
    st.caption("Source : Base de données PNADT — Programme National d Aménagement du Territoire")
    if st.button("🗺️ Afficher tous les forages du Senegal"):
        afficher_carte_forages()'''

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done' if old in content else 'TEXTE NON TROUVE')
