# 🌍 Senegal Climate Alert System

> Données climatiques journalières · mensuelles · annuelles pour les **557 communes du Sénégal** (2025-2055).

[![Tests](https://github.com/YvesKingsman/qgis-climate-alert-senegal/actions/workflows/test.yml/badge.svg)](...)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Démarrage rapide

```bash
git clone https://github.com/YvesKingsman/qgis-climate-alert-senegal.git
cd qgis-climate-alert-senegal

# Installer les dépendances
pip install -r requirements.txt

# Initialiser la base de données + communes
python main.py --init

# Générer des données de démonstration (5 communes)
python main.py --generate 5

# Lancer l'API REST
python main.py --api
# → http://localhost:8000/docs

# Lancer le dashboard Streamlit
streamlit run dashboard/app.py
# → http://localhost:8501
```

---

## 📦 Architecture

```
senegal_climate_system/
├── data/           # DB schema + générateur communes
├── models/         # Multi-résolution manager, query engine, indicateurs
├── visualization/  # Graphiques matplotlib + cartes Folium
├── api/            # FastAPI REST API
├── ml/             # Modèles LSTM + Random Forest
├── dashboard/      # Streamlit (8 pages)
├── tests/          # pytest (unit + integration)
├── scripts/        # Initialisation, génération, backup
├── docker/         # Dockerfiles + docker-compose
└── .github/        # CI/CD GitHub Actions
```

---

## 🌡️ Données disponibles

| Résolution  | Points/commune/an | Cas d'usage              |
|-------------|-------------------|--------------------------|
| Journalière | ~11 000           | Événements extrêmes      |
| Mensuelle   | 12                | Tendances saisonnières   |
| Annuelle    | 1                 | Projection 30 ans        |

**Scénarios CMIP6** : SSP1-1.9 (+1.2°C) · SSP2-4.5 (+1.8°C) · SSP5-8.5 (+2.8°C)

---

## 🔌 API Endpoints

| Méthode | Endpoint                        | Description               |
|---------|---------------------------------|---------------------------|
| GET     | `/api/communes`                 | Liste des communes        |
| GET     | `/api/climate/{resolution}`     | Données climatiques       |
| GET     | `/api/statistics/{commune}`     | Statistiques & tendances  |
| GET     | `/api/risk/{commune}`           | Niveau de risque + recs   |

---

## 🐳 Docker

```bash
cd docker
docker-compose up -d
# API:        http://localhost:8000
# Dashboard:  http://localhost:8501
```

---

## 🧪 Tests

```bash
pytest tests/ -v --cov=. --cov-report=html
# Rapport: htmlcov/index.html
```

---

## 📄 Licence

MIT © 2025 YvesKingsman
