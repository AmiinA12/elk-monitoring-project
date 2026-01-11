# 🚀 ELK Monitoring Platform

> **Application de Monitoring et d'Analyse de Logs en Temps Réel avec Stack ELK**

[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-7.17.0-yellow.svg)](https://www.elastic.co/)
[![Flask](https://img.shields.io/badge/Flask-2.3.2-black.svg)](https://flask.palletsprojects.com/)

---

## 📋 Description

Ce projet implémente une **plateforme complète de monitoring et d'analyse de logs en temps réel** pour un environnement **E-Commerce**. Le système collecte, indexe, analyse et visualise les logs provenant de différents microservices (paiement, inventaire, authentification, notifications).

### Fonctionnalités Principales

✅ **Ingestion de Logs**: Upload de fichiers CSV/JSON via interface web  
✅ **Indexation Elasticsearch**: Recherche full-text ultra-rapide  
✅ **Dashboard Interactif**: KPIs, graphiques temps réel, statistiques  
✅ **Recherche Avancée**: Filtres par niveau, service, période  
✅ **Visualisations Kibana**: Graphiques, tableaux de bord personnalisables  
✅ **API RESTful**: Endpoints pour intégration externe  
✅ **Stockage Métadonnées**: MongoDB pour tracking des uploads  
✅ **Cache Redis**: Performance optimisée  

---

## 🎯 Scénario Choisi

**E-Commerce Platform Log Analysis**

Le système surveille les logs de:
- 💳 **Payment Service**: Transactions, erreurs de paiement
- 📦 **Inventory Service**: Gestion de stock, alertes
- 👤 **User Service**: Actions utilisateurs, sessions
- 🔐 **Auth Service**: Connexions, tentatives échouées
- 📧 **Notification Service**: Envoi d'emails, SMS

---

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│  Web App    │─────▶│  Logstash    │─────▶│Elasticsearch │
│  (Flask)    │      │  (Pipeline)  │      │  (Indexing)  │
└─────────────┘      └──────────────┘      └──────────────┘
       │                                            │
       │                                            │
       ▼                                            ▼
┌─────────────┐                            ┌──────────────┐
│  MongoDB    │                            │    Kibana    │
│ (Metadata)  │                            │(Visualization)│
└─────────────┘                            └──────────────┘
       │
       ▼
┌─────────────┐
│    Redis    │
│  (Cache)    │
└─────────────┘
```

---

## 🚀 Installation Rapide

### Prérequis
- Docker Desktop 20.10+
- 8GB RAM minimum (16GB recommandé)
- 10GB espace disque libre

### Démarrage en 3 étapes

```powershell
# 1. Naviguer vers le projet
cd elk-monitoring-project

# 2. Démarrer l'infrastructure
docker-compose up -d

# 3. Ouvrir l'application
start http://localhost:8000
```

**⏱️ Temps d'initialisation**: 2-3 minutes

---

## 📚 Documentation

### Guides Complets

- 📖 **[Installation Guide](docs/INSTALLATION.md)** - Setup détaillé et troubleshooting
- 🎨 **[Kibana Setup](docs/KIBANA_SETUP.md)** - Visualisations et dashboards
- 🔧 **[API Documentation](#api-endpoints)** - Endpoints REST

### Accès aux Services

| Service | URL | Description |
|---------|-----|-------------|
| **Web App** | http://localhost:8000 | Interface principale |
| **Kibana** | http://localhost:5601 | Dashboards et visualisations |
| **Elasticsearch** | http://localhost:9200 | API de recherche |
| **Health Check** | http://localhost:8000/health | Status des services |

---

## 🎨 Interface Web

### 📊 Dashboard
- **4 KPI Cards**: Total logs, INFO, WARNING, ERROR
- **Line Chart**: Évolution des logs sur 24h
- **Pie Chart**: Répartition par service
- **Table**: Logs récents

### ☁️ Upload
- **Drag & Drop**: Glisser-déposer vos fichiers
- **Formats supportés**: CSV, JSON
- **Progress Bar**: Suivi de l'upload
- **Historique**: Derniers fichiers uploadés

### 🔍 Search
- **Recherche Full-Text**: Dans tous les champs
- **Filtres**: Niveau, Service, Période
- **Pagination**: 50 résultats par page
- **Export CSV**: Téléchargement des résultats
- **Détails**: Modal pour inspection complète

---

## 🛠️ Technologies Utilisées

### Backend
- **Flask 2.3.2** - Framework web Python
- **Elasticsearch 7.17.0** - Moteur de recherche
- **Logstash 7.17.0** - Pipeline d'ingestion
- **MongoDB 5.0** - Base de données NoSQL
- **Redis 6.2** - Cache in-memory

### Frontend
- **Bootstrap 5.3.0** - Framework CSS
- **Chart.js 4.3.0** - Graphiques interactifs
- **Vanilla JavaScript** - Logique client

### Infrastructure
- **Docker Compose** - Orchestration des services
- **Kibana 7.17.0** - Visualisation

---

## 📊 API Endpoints

### Health & Stats
```http
GET /health
GET /api/v1/stats
```

### Dashboard
```http
GET /api/v1/dashboard/stats
```
Retourne: KPIs, timeline, distribution services, logs récents

### Search
```http
GET /api/v1/search?q=error&level=ERROR&service=payment-service&page=1&size=50
```
Paramètres:
- `q` - Recherche texte libre
- `level` - Filtre par niveau (INFO/WARNING/ERROR/DEBUG)
- `service` - Filtre par service
- `page` - Numéro de page
- `size` - Résultats par page

### Upload
```http
POST /api/v1/upload
Content-Type: multipart/form-data

file: <binary>
```

### Recent Uploads
```http
GET /api/v1/uploads/recent
```

---

## 🧪 Générer des Données de Test

```powershell
# Installer les dépendances
pip install faker pandas

# Générer 100 logs e-commerce
python scripts/generate_test_data.py --count 100

# Générer CSV uniquement
python scripts/generate_test_data.py --count 50 --format csv

# Générer JSON uniquement
python scripts/generate_test_data.py --count 50 --format json
```

Les fichiers sont créés dans `data/test/`

---

## 🔧 Commandes Docker Utiles

```powershell
# Voir les logs
docker-compose logs -f

# Redémarrer un service
docker-compose restart webapp

# Arrêter tout
docker-compose down

# Rebuild après modification
docker-compose build webapp
docker-compose up -d webapp

# Accéder à un conteneur
docker exec -it elk_webapp /bin/bash

# Monitorer les ressources
docker stats
```

---

## 📁 Structure du Projet

```
elk-monitoring-project/
├── webapp/                  # Application Flask
│   ├── templates/          # Pages HTML
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── upload.html
│   │   └── search.html
│   ├── static/             # Assets statiques
│   │   ├── css/style.css
│   │   └── js/
│   │       ├── dashboard.js
│   │       ├── upload.js
│   │       └── search.js
│   ├── app.py              # Application principale
│   ├── Dockerfile
│   └── requirements.txt
├── logstash/               # Configuration Logstash
│   ├── config/logstash.yml
│   └── pipeline/
│       ├── csv-pipeline.conf
│       └── json-pipeline.conf
├── data/                   # Stockage des données
│   ├── uploads/           # Fichiers à traiter
│   ├── test/              # Données de test
│   └── generated/         # Logs générés
├── scripts/
│   └── generate_test_data.py
├── docs/                   # Documentation
│   ├── INSTALLATION.md
│   ├── KIBANA_SETUP.md
│   └── kibana-dashboard-template.json
├── docker-compose.yml      # Orchestration Docker
├── .env.example           # Variables d'environnement
├── .gitignore
└── README.md
```

---

## 👥 Équipe

- **Développeur**: [Votre Nom]
- **Binôme**: [Nom du binôme]
- **Formation**: IT Business School
- **Projet**: Mini-Projet BigData Frameworks

---

## 📅 Planning

| Sprint | Période | Statut |
|--------|---------|--------|
| Sprint 1: Infrastructure & Backend | Semaine 1 | ✅ Terminé |
| Sprint 2: Frontend & Visualisation | Semaine 2 | ✅ Terminé |
| Sprint 3: Kibana Integration | Semaine 3 | ✅ Terminé |
| Tests & Documentation | Semaine 4 | 🔄 En cours |

---

## 🎓 Livrables

### Code Source
- ✅ Repository Git complet
- ✅ Docker Compose fonctionnel
- ✅ Application web déployable
- ✅ Scripts de génération de données

### Documentation
- ✅ README.md (ce fichier)
- ✅ Guide d'installation
- ✅ Guide Kibana
- ✅ Code commenté

### Visualisations
- ✅ Dashboard Kibana exporté
- ✅ 3+ visualisations
- ✅ Index patterns configurés

---

## 🚨 Troubleshooting

### Elasticsearch ne démarre pas
```powershell
# Vérifier les logs
docker-compose logs elasticsearch

# Augmenter la mémoire Docker (Settings → Resources)
# Minimum 4GB
```

### Port 8000 déjà utilisé
```powershell
# Trouver le processus
netstat -ano | findstr :8000

# Modifier le port dans docker-compose.yml
```

### Logstash ne traite pas les fichiers
```powershell
# Vérifier que les fichiers sont dans data/uploads/
# Vérifier les logs Logstash
docker-compose logs logstash
```

Consultez le [guide d'installation](docs/INSTALLATION.md) pour plus de solutions.

---

## 🔒 Sécurité - Production

⚠️ **Avant déploiement en production**:
- Changer tous les mots de passe par défaut
- Activer SSL/TLS
- Configurer les firewall rules
- Activer X-Pack Security (Elasticsearch)
- Limiter les ressources des conteneurs

---

## 📝 Licence

Ce projet est développé dans un cadre pédagogique pour IT Business School.

---

## 🙏 Remerciements

- Équipe Elastic pour la stack ELK
- Communauté Docker
- IT Business School

---

**💡 Besoin d'aide ?**
- 📖 Consultez la [documentation complète](docs/)
- 🔍 Vérifiez les [issues GitHub](#)
- 💬 Contactez l'équipe pédagogique

**✨ Bon Monitoring !**

