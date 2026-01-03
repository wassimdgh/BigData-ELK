# Projet Big Data - IoT Smart Building Monitoring Platform

## 📋 Description
Plateforme de monitoring et d'analyse de logs pour un bâtiment intelligent équipé de capteurs IoT.

## 🏢 Scénario B: Infrastructure IoT / Smart Building

### Types de logs traités:
- 🌡️ Capteurs (température, humidité, luminosité, CO2)
- ⚠️ Alertes (anomalies détectées, seuils dépassés)
- 🔧 Maintenance préventive
- ⚡ Consommation énergétique
- 👥 Occupation des espaces

### KPI à suivre:
- Température moyenne par zone et par heure
- Nombre d'alertes critiques par jour
- Consommation énergétique en temps réel
- Taux d'occupation des espaces
- Prévisions de maintenance

## 🛠️ Stack Technique

### Backend
- **Python 3.11+** avec Flask
- **Elasticsearch 8.x** - Indexation et recherche
- **Logstash 8.x** - Ingestion de données
- **Kibana 8.x** - Visualisation
- **MongoDB** - Stockage métadonnées
- **Redis** - Cache et sessions

### Frontend
- HTML5, CSS3, JavaScript
- Bootstrap 5
- Chart.js pour visualisations
- DataTables.js

### DevOps
- Docker & Docker Compose
- Git & GitHub

## 🚀 Installation et Démarrage

### Prérequis
- Docker Desktop installé
- Python 3.11+
- Git
- 8GB RAM minimum
- 20GB espace disque

### Étapes d'installation

1. **Cloner le repository**
```bash
git clone <votre-repo>
cd BigData
```

2. **Créer l'environnement virtuel Python**
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

4. **Démarrer les services Docker**
```bash
docker-compose up -d
```

5. **Vérifier les services**
- Elasticsearch: http://localhost:9200
- Kibana: http://localhost:5601
- Application Web: http://localhost:8000
- MongoDB: localhost:27017
- Redis: localhost:6379

6. **Générer des données de test**
```bash
python scripts/generate_iot_data.py
```

## 📁 Structure du Projet

```
BigData/
├── app/                          # Application Flask
│   ├── __init__.py
│   ├── models/                   # Modèles de données
│   ├── routes/                   # Routes API
│   ├── services/                 # Logique métier
│   ├── templates/                # Templates HTML
│   └── static/                   # CSS, JS, images
├── config/                       # Configurations
│   ├── elasticsearch/
│   ├── logstash/
│   └── kibana/
├── scripts/                      # Scripts utilitaires
│   ├── generate_iot_data.py
│   └── init_elasticsearch.py
├── tests/                        # Tests unitaires
├── docs/                         # Documentation
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## 📊 Fonctionnalités

### Fonctionnalités de Base (Obligatoires)
- ✅ Upload de fichiers logs (CSV/JSON)
- ✅ Ingestion via Logstash
- ✅ Indexation Elasticsearch
- ✅ Recherche en texte libre
- ✅ Dashboard de visualisation
- ✅ Interface web intuitive

### Modules Intermédiaires (3 minimum)
- [ ] Authentification et gestion des rôles
- [ ] Cache Redis pour performances
- [ ] API REST complète avec Swagger
- [ ] Dashboards personnalisables
- [ ] Export de données (CSV, JSON, PDF)

### Modules Avancés (2 pour 20/20)
- [ ] Système d'alerting en temps réel
- [ ] WebSocket pour mises à jour temps réel
- [ ] Machine Learning pour prédiction de pannes
- [ ] CI/CD avec GitHub Actions

## 🎯 Cas d'Usage Prioritaires

1. **Alerte température critique**
   - Déclencher une alerte si température > seuil

2. **Optimisation énergétique**
   - Analyser les patterns de consommation

3. **Prédiction de pannes**
   - ML sur données historiques

## 📈 API Endpoints

```
GET  /api/v1/logs              - Liste paginée des logs
GET  /api/v1/logs/:id          - Détail d'un log
POST /api/v1/upload            - Upload fichier
GET  /api/v1/search            - Recherche
GET  /api/v1/stats             - Statistiques globales
GET  /api/v1/files             - Liste fichiers uploadés
```

## 🧪 Tests

```bash
# Tests unitaires
pytest tests/

# Tests d'intégration
pytest tests/integration/

# Coverage
pytest --cov=app tests/
```

## 📝 Documentation

Voir le dossier `docs/` pour:
- Architecture technique
- Guide utilisateur
- Documentation API
- Diagrammes UML

## 👥 Auteurs

[Votre Nom]

## 📅 Date

Novembre 2025

## 📄 Licence

Projet académique - Mini-Projet Big Data Frameworks
