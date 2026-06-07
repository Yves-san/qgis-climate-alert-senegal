with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '    st.markdown("### 🗺️ Carte des 4218 forages officiels du Sénégal")\n    st.caption("Source : Base de données PNADT — Programme National d Aménagement du Territoire")\n    afficher_carte_forages()'

new = '''    st.markdown("### 🗺️ Carte des 4218 forages officiels du Sénégal")
    st.caption("Source : Base de données PNADT — Programme National d Aménagement du Territoire")
    if st.button("🗺️ Afficher la carte des forages (peut prendre quelques secondes)"):
        afficher_carte_forages()'''

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done1' if old in content else 'TEXTE1 NON TROUVE')
with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '    st.markdown("### Carte superposee — Reseau hydraulique et forages")\n    st.caption("Traits bleus = cours d eau. Points = 4218 forages officiels PNADT")'

new = '''    st.markdown("### Carte superposee — Reseau hydraulique et forages")
    st.caption("Traits bleus = cours d eau. Points = 4218 forages officiels PNADT")
    if not st.button("🗺️ Afficher la carte superposee (peut prendre quelques secondes)"):
        st.info("Cliquez sur le bouton pour afficher la carte")
        return'''

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done2' if old in content else 'TEXTE2 NON TROUVE')
