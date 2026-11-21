# <img src="docs/assets/icons/building.svg" width="18" height="18" alt=""> UrbanHub - Jumeau Numérique & Plateforme Data Lake Smart City

> **Projet M2 IPSSI** - Architecture Data Lake & Entrepôts de Données  
> Système Big Data pour la collecte, le stockage et l'analyse croisée de données urbaines (Batch, Streaming, IoT).

---

## <img src="docs/assets/icons/list.svg" width="18" height="18" alt=""> Sommaire

1. [Présentation du projet](#présentation-du-projet)
2. [Architecture du Data Lake](#architecture-du-data-lake)
3. [Organisation du Répertoire](#organisation-du-répertoire)
4. [Sources de Données & Périmètre](#sources-de-données--périmètre)
5. [Prérequis & État de l'Environnement](#prérequis--état-de-lenvironnement)
6. [Guide de Démarrage Rapide](#guide-de-démarrage-rapide)
7. [Documentation & Suivi](#documentation--suivi)
8. [Livrables Attendus](#livrables-attendus)

---

## <img src="docs/assets/icons/book-open.svg" width="18" height="18" alt=""> Présentation du projet

Une **Smart City** moderne génère en continu d'importants volumes de données hétérogènes :
- Capteurs environnementaux et qualité de l'air (IoT)
- Observations météorologiques historiques et actuelles (Batch)
- Réseaux de transport et mobilités douces en libre-service (Streaming)

**UrbanHub** est un jumeau numérique urbain capable d'ingérer ces flux, d'assurer leur gouvernance au sein d'un **Data Lake structuré en architecture médaillon (Bronze ➔ Silver ➔ Gold)**, et de croiser ces données pour éclairer la prise de décision publique.

---

## <img src="docs/assets/icons/building.svg" width="18" height="18" alt=""> Architecture du Data Lake

Le système s'articule autour de trois couches de stockage et de raffinage de données :

```text
       SOURCES                          DATA LAKE                            RESTITUTION
 ┌──────────────────┐
 │ Open-Meteo Météo │──(Batch)────┐
 └──────────────────┘             │
 ┌──────────────────┐             ▼
 │ CityBikes Vélos  │──(Stream)──►[ BRONZE ]  Données brutes horodatées (CSV / JSON)
 └──────────────────┘             │
 ┌──────────────────┐             ▼
 │ OpenAQ Pollution │──(IoT)─────►[ SILVER ]  Tables nettoyées, typées, dédupliquées (Parquet)
 └──────────────────┘             │
                                  ▼
                                  [  GOLD  ]  Indicateurs agrégés & tables croisées
                                  │
                                  ▼
                         [ Dashboard Voilà ]  Visualisations & KPI interactifs
```

- **<img src="docs/assets/icons/layers-bronze.svg" width="18" height="18" alt=""> Bronze :** Stockage brut des payloads API et fichiers sources avec métadonnées d'ingestion (S3 / MinIO).
- **<img src="docs/assets/icons/layers-silver.svg" width="18" height="18" alt=""> Silver :** Format Parquet colonnaire optimisé, schéma strict, timestamps unifiés en UTC, conversions d'unités et déduplication.
- **<img src="docs/assets/icons/layers-gold.svg" width="18" height="18" alt=""> Gold :** Vues décisionnelles agrégées par ville et heure (`weather_daily`, `mobility_station_latest`, `pollution_hourly`, `city_hourly`).

---

## <img src="docs/assets/icons/folder.svg" width="18" height="18" alt=""> Organisation du Répertoire

```text
UrbanHub/
├── docs/                                  # Documentation projet & suivi
│   ├── ENONCE.md                          # Cahier des charges et consignes détaillées
│   ├── PLAN.md                            # Feuille de route chronologique et rôles
│   ├── AVANCEMENT.md                      # Journal de bord et checklist de progression
│   ├── GUIDE_TECHNIQUE.md                 # Recettes, patterns de code et capitalisation des TPs
│   ├── DATALAKE_CLOUD_GUIDE.md            # Bascule du Data Lake local vers Cloudflare R2
│   ├── MIGRATION_OPENMETEO.md             # Passage de la météo NOAA à Open-Meteo
│   ├── RESULTATS_NOAA.md                  # Bilan de référence Open-Meteo 2022–2026
│   ├── ARCHIVE_RESULTATS_NOAA.md          # Bilan historique NOAA 2020–2024
│   ├── CONCLUSIONS_POLLUTION.md           # Conclusions pollution et croisement météo (5 ans)
│   └── assets/icons/                      # Icônes SVG utilisées dans les documents
├── config/
│   └── cities.yml                         # Référentiel des villes et métadonnées
├── scripts/                               # Collecte et outils
│   ├── openmeteo_batch.py                 # Batch météo Open-Meteo (Paris, Lyon, Lille)
│   ├── citybikes_stream.py                # Micro-batch CityBikes (toutes les 5 min)
│   ├── citybikes_archive.py               # Archives mensuelles CityBikes (data.citybik.es), 5 ans
│   ├── openaq_archive.py                  # Archive publique OpenAQ (S3), 2022 à 2026, conversion Silver
│   ├── openmeteo_archive.py               # Météo 2022 à 2026 avec visibilité (ERA5 + historical-forecast)
│   ├── archives_to_gold.py                # Tables Gold historiques (météo, pollution, city_hourly_history)
│   ├── citybikes_archive_gold.py          # Gold mobilité historique (remplissage, usage) depuis l'archive CityBikes
│   ├── noaa_batch.py                      # Ancien batch NOAA, conservé comme historique
│   └── init_datalake.py                   # Création et test des buckets
├── src/
│   └── openaq_pipeline.py                 # Ingestion et traitement OpenAQ (Bronze, Silver, Gold)
├── notebooks/
│   ├── 01_openmeteo_batch.ipynb           # Analyse météo Open-Meteo
│   ├── 01_noaa_batch.ipynb                # Analyse NOAA 2020-2024 (historique)
│   ├── 02_citybikes_stream.ipynb          # Pilotage de la collecte CityBikes
│   ├── 03_openaq_iot.ipynb                # Pollution OpenAQ et table croisée city_hourly
│   ├── 04_analyses_mobilite.ipynb         # Analyses de mobilité et croisement vélos, météo, pollution
│   ├── 05_dashboard.ipynb                 # Tableau de bord interactif Voilà
│   ├── 06_archives_citybikes.ipynb        # Archives CityBikes sur 5 ans (plan, téléchargement, schéma)
│   └── 07_analyses_historiques.ipynb      # Analyses sur 5 ans : météo, pollution et leur croisement
├── demos/                                 # Vidéos finales (non versionnées)
│   ├── Démo-UrbanHub-Partie1.mp4          # Batch météo, Data Lake et vue météo
│   └── Démo-UrbanHub-Partie2.mp4          # Streaming, IoT, croisements et Dashboard
├── Dockerfile, docker-compose.yml         # Jupyter, Voilà et MinIO
├── pyproject.toml, uv.lock                # Environnement Python (uv sync)
├── requirements.txt                       # Mêmes dépendances, utilisées par le Dockerfile
├── .env.example                           # Modèle de configuration d'environnement
└── README.md                              # Guide principal du projet (ce fichier)
```

---

## <img src="docs/assets/icons/globe.svg" width="18" height="18" alt=""> Sources de Données & Périmètre

### 1. Flux Batch - Météo Open-Meteo

**Source officielle :** [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api), modèle ECMWF IFS, données modélisées aux coordonnées de **Paris, Lyon et Lille**. Le lot va du 1er janvier 2020 à la dernière heure UTC terminée à l’exécution ; il ne représente pas un ensemble de stations couvrant toute la France. La visibilité est nulle au sens SQL quand l’API ne la fournit pas (notamment en 2020–2024). La pluie liquide en mm est alignée sur le début de l’intervalle d’accumulation d’une heure.

```bash
python scripts/openmeteo_batch.py           # lot local
python scripts/openmeteo_batch.py --upload  # actualisation des tables partagées R2
```

- Bronze : `openmeteo/year=AAAA/city_id=VILLE/archive.json` et `openmeteo/manifest.json`.
- Silver : `weather/openmeteo/year=AAAA/weather_hourly.parquet`.
- Gold : `kpis/weather_hourly.parquet` sur `(city_id, hour_utc)` en UTC ; `kpis/weather_daily.parquet` sur `(city_id, day_utc)` en UTC. Le rafraîchissement météo n’est pas planifié automatiquement.
- Analyse : [bilan météo Open-Meteo 2022–2026](docs/RESULTATS_NOAA.md) et [notebook 01 sur le flux Open-Meteo](notebooks/01_openmeteo_batch.ipynb).

#### Ancien flux - archive NOAA ISD
- **Source :** [Archive NOAA ISD Global Hourly (NODD)](https://registry.opendata.aws/noaa-global-hourly/).
- **Périmètre :** Stations françaises (`CTRY=FR`) sur les cinq dernières années civiles complètes de l’archive ISD : 2020–2024. L’archive s’arrête le 24 août 2025 ; pour un croisement avec les collectes actuelles, utiliser [GHCNh](https://www.ncei.noaa.gov/products/global-historical-climatology-network-hourly).
- **Variables :** `station_id`, `timestamp`, `temperature`, `wind_speed`, `wind_direction`, `pressure`, `precipitation`, `visibility`.
- **Enjeux métier :** Détection d'anomalies climatiques, corrélations météo-visibilité, saisonnalité.

Depuis la racine, avec les dépendances du projet installées :

```bash
# Échantillon 2025 : Paris-Orly, Lyon–Saint-Exupéry et Lille–Lesquin
python scripts/noaa_batch.py --workers 3
# Lot France : cinq années civiles complètes, 2020–2024
python scripts/noaa_batch.py --mode france --workers 8
```

Le script reprend les CSV déjà téléchargés et distingue les fichiers absents (HTTP 404) des erreurs dans `bronze/noaa/manifest.json`. Les sorties sont sous `data/noaa-<mode>-<début>-<fin>/`. Avec `--upload`, le Gold du lot France est archivé sous `kpis/noaa/` ; l’échantillon utilise le préfixe `sample/2025-2025/`. L’analyse historique est dans [le notebook NOAA](notebooks/01_noaa_batch.ipynb).

Le [bilan archivé du lot NOAA France 2020–2024](docs/ARCHIVE_RESULTATS_NOAA.md) recense les livrables, les conclusions météo et la limite des mesures de pluie.

### 2. Flux Streaming - Mobilité CityBikes
- **Source :** [CityBikes API](http://api.citybik.es/v2/networks)
- **Fréquence :** Collecte automatisée toutes les 5 minutes (300 s, choix de l'équipe ; l'énoncé indique 2 à 3 minutes).
- **Variables :** `station_id`, `station_name`, `latitude`, `longitude`, `bikes_available`, `free_slots`, `timestamp`.
- **Enjeux métier :** Pression sur les stations, détection des ruptures de stock / saturations, pics journaliers.

### 3. Flux IoT - Pollution atmosphérique OpenAQ
- **Source :** [OpenAQ API v3](https://api.openaq.org/)
- **Polluants ciblés :** `PM2.5`, `PM10`, `NO2`, `O3`, `CO`.
- **Variables :** `sensor_id`, `latitude`, `longitude`, `pollutant`, `value`, `unit`, `timestamp`.
- **Enjeux métier :** Identification des points chauds, variations diurnes, profils d'émissions.

### 4. Analyses Croisées
- Alignement temporel sur l'heure UTC par agglomération.
- Interaction météo / qualité de l'air (dispersion, vent, pluie).
- Impact des intempéries sur l'usage des mobilités douces.

---

## <img src="docs/assets/icons/sliders.svg" width="18" height="18" alt=""> Prérequis & État de l'Environnement

- **Docker Desktop** (Compose v2) : fait tourner Jupyter, Voilà et MinIO.
- **Python 3.11 et `uv` 0.11+** : pour lancer les scripts hors Docker. `uv sync` installe l'environnement figé dans `uv.lock`, avec les mêmes versions que l'image Docker (pandas 3.1.1, pyarrow 26.0.1).
- **Data Lake :** Cloudflare R2 partagé (recommandé, clés à demander à l'équipe) ou MinIO local (`urbanhub-minio`, ports `9000` et `9001`, identifiants locaux `minioadmin` / `minioadmin123`).
- **API :**
  - `CityBikes` : répond `HTTP 429` si on la sollicite trop vite ; l'intervalle de collecte est de 5 minutes (300 s).
  - `Open-Meteo` : gratuit, usage non commercial, sans clé.
  - `OpenAQ v3` : clé gratuite de 64 caractères hexadécimaux dans `OPENAQ_API_KEY` ; une clé invalide renvoie `HTTP 401`.
- **Collecte en continu :** les trois flux ont un service Docker dans le profil `collect` (`docker compose --profile collect up -d`). Une seule machine doit les faire tourner, car CityBikes limite les appels par adresse. Voir [DEPLOIEMENT_CONTINU.md](docs/DEPLOIEMENT_CONTINU.md).

---

## <img src="docs/assets/icons/rocket.svg" width="18" height="18" alt=""> Guide de Démarrage Rapide

### 1. Cloner et entrer dans le dossier
```powershell
git clone https://github.com/Thekorzeremi/UrbanHub.git
cd UrbanHub
```

### 2. Configurer le fichier `.env`
```powershell
Copy-Item .env.example .env
```
Renseigner les clés R2 (ou le bloc MinIO local, avec `MINIO_ENDPOINT=minio:9000` dans Docker) et `OPENAQ_API_KEY`. Ce fichier n'est jamais versionné.

### 3. Démarrer la plateforme
```powershell
docker compose up -d --build
```
Dashboard : [http://localhost:8866](http://localhost:8866) | Jupyter : [http://localhost:8888](http://localhost:8888) | Console MinIO : [http://localhost:9001](http://localhost:9001).

### 4. Initialiser et tester le Data Lake
```powershell
docker compose exec jupyter python scripts/init_datalake.py
```

### 5. Environnement Python local (scripts et notebooks hors Docker)
```powershell
uv sync
```
```powershell
uv run python scripts/citybikes_stream.py
```
```powershell
uv run jupyter notebook
```

---

## <img src="docs/assets/icons/book-open.svg" width="18" height="18" alt=""> Documentation & Suivi

- <img src="docs/assets/icons/book-open.svg" width="18" height="18" alt=""> [Cahier des charges complet (ENONCE.md)](docs/ENONCE.md)
- <img src="docs/assets/icons/map.svg" width="18" height="18" alt=""> [Feuille de route & Plan d'architecture (PLAN.md)](docs/PLAN.md)
- <img src="docs/assets/icons/bar-chart.svg" width="18" height="18" alt=""> [Tableau de bord de l'avancement (AVANCEMENT.md)](docs/AVANCEMENT.md)
- <img src="docs/assets/icons/wind.svg" width="18" height="18" alt=""> [Conclusions pollution et croisement météo (CONCLUSIONS_POLLUTION.md)](docs/CONCLUSIONS_POLLUTION.md)
- <img src="docs/assets/icons/book-open.svg" width="18" height="18" alt=""> [Guide Technique & Recettes d'Architecture (GUIDE_TECHNIQUE.md)](docs/GUIDE_TECHNIQUE.md)
- <img src="docs/assets/icons/cloud.svg" width="18" height="18" alt=""> [Guide Data Lake Cloud & Bascule R2 (DATALAKE_CLOUD_GUIDE.md)](docs/DATALAKE_CLOUD_GUIDE.md)
- <img src="docs/assets/icons/thermometer.svg" width="18" height="18" alt=""> [Migration météo NOAA vers Open-Meteo (MIGRATION_OPENMETEO.md)](docs/MIGRATION_OPENMETEO.md)
- <img src="docs/assets/icons/rocket.svg" width="18" height="18" alt=""> [Faire tourner la collecte en continu (DEPLOIEMENT_CONTINU.md)](docs/DEPLOIEMENT_CONTINU.md)
- <img src="docs/assets/icons/hard-drive.svg" width="18" height="18" alt=""> [Dashboard sans R2, avec un MinIO local (MODE_LOCAL_MINIO.md)](docs/MODE_LOCAL_MINIO.md)
- <img src="docs/assets/icons/list.svg" width="18" height="18" alt=""> [Messages à envoyer à l'équipe (MESSAGES_EQUIPE.md)](docs/MESSAGES_EQUIPE.md)
- <img src="docs/assets/icons/clipboard.svg" width="18" height="18" alt=""> [Reste à faire, répartition et budget de stockage (RESTE_A_FAIRE.md)](docs/RESTE_A_FAIRE.md)

---

## <img src="docs/assets/icons/package.svg" width="18" height="18" alt=""> Livrables Attendus

1. **Scripts d'ingestion & pipelines :** Code modulaire et documenté pour les 3 flux.
2. **Stockage structuré :** Données partitionnées dans MinIO (Bronze ➔ Silver ➔ Gold).
3. **Analyses exploratoires & visualisations :** Notebooks avec graphiques et interprétations métier rigoureuses.
4. **Vidéos de démonstration :**
   - `demos/Démo-UrbanHub-Partie1.mp4` (Batch météo Open-Meteo & Data Lake)
   - `demos/Démo-UrbanHub-Partie2.mp4` (Flux continus CityBikes/OpenAQ, analyses croisées & dashboard)
