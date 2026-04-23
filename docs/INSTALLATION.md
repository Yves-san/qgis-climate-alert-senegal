# Installation du Plugin Climate Alert pour QGIS

## Prérequis
- QGIS 3.16 ou supérieur
- Python 3.7+
- Git

## Étapes d'installation

### 1. Télécharger le plugin

```bash
git clone https://github.com/Yves-san/qgis-climate-alert-senegal.git
cd qgis-climate-alert-senegal
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Copier le plugin dans QGIS

#### Sur Windows:
```bash
xcopy plugin_qgis "%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\climate_alert" /E /I /Y
```

#### Sur macOS/Linux:
```bash
cp -r plugin_qgis ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/climate_alert
```

### 4. Redémarrer QGIS

Fermez et réouvrez QGIS complètement.

### 5. Activer le plugin

1. Allez à **Extensions** → **Gérer et installer des extensions**
2. Cherchez "Climate Alert"
3. Cliquez **Installer l'extension**
4. Redémarrez QGIS

### 6. Utiliser le plugin

Une nouvelle icône 🌍 apparaît dans la barre d'outils. Cliquez dessus pour ouvrir le plugin.

## Dépannage

### Le plugin n'apparaît pas
- Vérifiez que le dossier `climate_alert` existe dans le répertoire plugins QGIS
- Vérifiez que le fichier `metadata.txt` est présent
- Redémarrez QGIS

### Erreur de modules manquants
```bash
pip install --upgrade numpy matplotlib geojson PyYAML
```
