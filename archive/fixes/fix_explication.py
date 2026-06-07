with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '        st.plotly_chart(fig,use_container_width=True)\n        if df["spi"].notna().any():'

new = '''        st.plotly_chart(fig,use_container_width=True)
        drought_2025 = df["drought"].iloc[0]
        drought_2055 = df["drought"].iloc[-1]
        hausse = drought_2055 - drought_2025
        if drought_2055 >= 0.6:
            niveau = "CRITIQUE"
            couleur = "error"
        elif drought_2055 >= 0.3:
            niveau = "MODERE"
            couleur = "warning"
        else:
            niveau = "NORMAL"
            couleur = "success"
        texte = (
            "**Comment lire ce graphique ?**\\n\\n"
            "La ligne jaune montre comment la secheresse va evoluer a " + selected_commune + " entre 2025 et 2055. "
            "Plus la ligne monte, plus la secheresse sera severe.\\n\\n"
            "**Situation en 2025 :** niveau de secheresse a " + f"{drought_2025:.2f}" + " sur 1.\\n\\n"
            "**Situation en 2055 :** niveau prevu a " + f"{drought_2055:.2f}" + " sur 1 — niveau " + niveau + ".\\n\\n"
            "**Hausse prevue :** +" + f"{hausse:.2f}" + " points d ici 2055.\\n\\n"
            "**Les 2 lignes de seuil :**\\n"
            "- Ligne orange pointillee (0.3) : a partir de ce niveau, les agriculteurs doivent commencer a economiser l eau et adapter leurs cultures.\\n"
            "- Ligne rouge tiretee (0.6) : niveau critique — risque serieux de perte de recolte et de manque d eau pour les animaux.\\n\\n"
            "**Ce que cela signifie pour vous :**\\n"
        )
        if drought_2055 >= 0.6:
            texte += (
                "- La situation sera tres difficile a " + selected_commune + " d ici 2055.\\n"
                "- Commencez des maintenant a prevoir des cultures resistantes a la secheresse comme le mil et le sorgho.\\n"
                "- Construisez ou renforcez vos reserves d eau (citernes, bassins).\\n"
                "- Renseignez-vous aupres de l ANACIM et des services agricoles locaux pour des aides."
            )
        elif drought_2055 >= 0.3:
            texte += (
                "- La secheresse sera moderee mais il faut s y preparer.\\n"
                "- Privilegiez les varietes de cultures adaptees a la chaleur et au manque de pluie.\\n"
                "- Surveillez le niveau de vos puits et forages chaque annee."
            )
        else:
            texte += (
                "- La situation reste geerable pour ce scenario.\\n"
                "- Continuez vos pratiques agricoles habituelles en restant vigilant.\\n"
                "- Suivez les alertes meteo de l ANACIM chaque saison."
            )
        if couleur == "error":
            st.error(texte)
        elif couleur == "warning":
            st.warning(texte)
        else:
            st.success(texte)
        if df["spi"].notna().any():'''

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done')
