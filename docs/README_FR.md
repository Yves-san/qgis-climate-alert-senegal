# Système d'Alerte Climatique - Sénégal

## 🌍 Objectif

Simuler l'évolution des risques climatiques au Sénégal de 2026 à 2046 pour aider les agriculteurs et décideurs à:
- Prévoir les impacts (inondations, sécheresses, érosion)
- Adapter les cultures
- Minimiser les pertes agricoles
- Planifier l'avenir

## 📊 Fonctionnalités

✅ **Simulation interactive** : Voir 20 ans d'évolution en temps réel
✅ **3 scénarios** : Optimiste / Moyen / Pessimiste
✅ **6 régions** : Fleuve, Saloum, Casamance, Sahel, Côte, Plateau
✅ **Alertes dynamiques** : Risques par région et type
✅ **Recommandations** : Cultures adaptées pour chaque situation
✅ **Export rapports** : Générer documents d'analyse
✅ **Cartes interactives** : Visualiser données géographiques

## 🚀 Démarrage rapide

```bash
# 1. Cloner
git clone https://github.com/Yves-san/qgis-climate-alert-senegal.git

# 2. Installer dépendances
pip install -r requirements.txt

# 3. Copier plugin dans QGIS
cp -r plugin_qgis ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/climate_alert

# 4. Redémarrer QGIS et activer le plugin
```

## 📱 Technologies

- **QGIS 3.16+** : SIG open-source
- **Python 3.7+** : Logique simulation
- **PyQt5** : Interface graphique
- **GeoJSON** : Format géospatial
- **YAML** : Configuration

## 🎯 Cas d'usage

- 🌾 **Agriculteurs** : Planifier cultures selon climat futur
- 🏛️ **Décideurs** : Politiques adaptation climatique
- 📚 **Étudiants** : Recherche climatologie/agriculture
- 🌍 **ONG** : Programmes résilience

## 📝 Documentation

- [Installation](docs/INSTALLATION.md)
- [Guide Utilisation](docs/USER_GUIDE.md)
- [Spécifications Techniques](docs/TECHNICAL_SPECS.md)

## 🤝 Contribution

Les contributions sont bienvenues ! Consultez les issues pour les améliorations proposées.

## 📄 Licence

MIT License - Voir LICENSE.md

## 👤 Auteur

**Yves-san**
- GitHub: [@Yves-san](https://github.com/Yves-san)
- Email: yvesmalou78@gmail.com

## 🙏 Remerciements

- QGIS Project
- NASA/ESA pour données climatiques
- ANSD (Agence Nationale Statistique Sénégal)
