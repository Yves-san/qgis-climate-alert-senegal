with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = '''        with st.expander("Cest quoi le SPI ? Cliquez pour comprendre"):
            st.markdown("Le SPI mesure si les pluies sont normales ou insuffisantes par rapport aux 30 dernieres annees.")
            st.markdown("SPI positif : bonnes pluies. SPI negatif : secheresse.")
            st.markdown("Sources : ANACIM, NASA, Copernicus")'''

new = '''        with st.expander("Cest quoi le SPI ? Cliquez pour comprendre"):
            st.markdown("""
### Le SPI en langage simple

Le **SPI** (Indice de Precipitation Standardise) est un chiffre qui dit si les pluies sont normales, trop faibles ou trop fortes par rapport aux 30 dernieres annees dans votre region.

---

### Comment lire le chiffre ?

| Valeur SPI | Signification | Couleur |
|---|---|---|
| superieur a +1 | Pluies tres abondantes | Vert fonce |
| 0 a +1 | Pluies normales ou bonnes | Vert |
| 0 a -0.5 | Legerement sec | Jaune |
| -0.5 a -1 | Secheresse moderee | Orange |
| inferieur a -1 | Secheresse severe | Rouge |

---

### La formule utilisee

SPI = (pluies de cette annee - moyenne historique) divise par ecart-type

- Si les pluies de cette annee sont superieures a la moyenne : SPI positif
- Si les pluies de cette annee sont inferieures a la moyenne : SPI negatif
- Plus le chiffre est negatif, plus la secheresse est severe

---

### Exemple concret

Kaolack recoit normalement 600 mm de pluie par an.
- Si en 2040 il tombe 750 mm : SPI = +1.25 (bonne annee)
- Si en 2040 il tombe 450 mm : SPI = -1.25 (secheresse moderee)
- Si en 2040 il tombe 300 mm : SPI = -2.5 (secheresse severe)

Saint-Louis recoit normalement 280 mm par an.
- Meme si il tombe peu de pluie, si cest normal pour Saint-Louis, le SPI reste proche de 0.

---

### A quoi ca sert concretement ?

- Savoir a lavance si la saison sera bonne ou mauvaise
- Decider quoi planter selon la quantite deau disponible
- Gerer les reserves deau des puits, forages et mares
- Alerter les autorites avant une crise de secheresse

---

### Sources des donnees

- **ANACIM** : Agence Nationale de lAviation Civile et de la Meteorologie du Senegal
- **NASA POWER** : donnees satellitaires mondiales
- **Copernicus ERA5** : service meteorologique europeen
- Modeles climatiques SSP1-1.9, SSP2-4.5, SSP5-8.5
            """)'''

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done')
