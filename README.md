# Flowlance Backend API

API backend de Flowlance, construite avec Django et Django REST Framework, pour gérer:
- Authentification JWT
- Profils `FREELANCE` et `COMPANY`
- Offres d'emploi et candidatures
- Messagerie interne
- Endpoints IA (OpenRouter) pour génération d'annonces, feedback CV et messages RH

- Lien vers le Frontend (React): https://github.com/Yethiii/flowlance_frontend.git
- Lien vers l'API en production: https://flowlance-api.onrender.com/api

## Stack technique

- Python 3.12+
- Django 5.2
- Django REST Framework
- Authentification: SimpleJWT
- Base de données: PostgreSQL, SQLite
- Hébergement et fichiers statiques: Render / Whitenoise
- Traitement de fichiers: `PyPDF2` (pour l'extraction de texte des CV)
- Intelligence artificielle: OpenRouter API

## Fonctionnalités

- Inscription utilisateur avec rôles publics `FREELANCE` et `COMPANY`
- Création automatique du profil lié via signal Django
- Gestion complète des profils freelance/entreprise
- Catalogue d'offres + filtres/recherche/tri
- Candidatures avec workflow de statut
- Messagerie bilatérale + compteur de notifications
- Dashboards de matching IA côté freelance et entreprise

## Prérequis

- Python 3.12 ou supérieur
- `pip`
- Docker + Docker Compose (optionnel, recommandé pour PostgreSQL)

## Installation locale

```bash
# Créer et activer l'environnement virtuel
python -m venv venv
# L'activer sur Windows:
venv\Scripts\activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration environnement

Créer un fichier `.env` à la racine:

```env
OPENROUTER_API_KEY=[votre_cle_api_openrouter]
DATABASE_URL=postgres://admin:password@localhost:5432/flowlance_db
```

Variables importantes:
- `OPENROUTER_API_KEY`: obligatoire pour les endpoints IA.
- `DATABASE_URL`: optionnelle. Si absente, fallback automatique sur SQLite (`db.sqlite3`).

## Lancer le projet

```bash
# Appliquer les migrations
python manage.py migrate

# Créer un superuser (optionnel)
python manage.py createsuperuser

# Démarrer l'API
python manage.py runserver
```

Base URL locale: `http://127.0.0.1:8000`

## Base de données PostgreSQL avec Docker

Le dépôt inclut un `docker-compose.yml` prêt à l'emploi:

```bash
docker compose up -d
```

## Authentification

Le projet utilise JWT (SimpleJWT):

```http
Authorization: Bearer <votre_access_token>
```

- Obtenir un token: `POST /api/token/` (avec email et mot de passe)
- Renouveler un token: `POST /api/token/refresh/`

## API - Endpoints principaux

Préfixe global: `/api/`

### Auth et utilisateur

- `POST /api/register/`
- `POST /api/token/`
- `POST /api/token/refresh/`
- `GET /api/users/me/`

### Profils freelance

- `GET|POST /api/freelances/`
- `GET|PATCH|DELETE /api/freelances/{id}/`
- `POST /api/freelances/deactivate/`
- `DELETE /api/freelances/delete_account/`

### Profils entreprise

- `GET|POST /api/companies/`
- `GET|PATCH|DELETE /api/companies/{id}/`
- `POST /api/companies/deactivate/`
- `DELETE /api/companies/delete_account/`

### Compétences, référentiels et parcours

- `GET /api/sectors/`
- `GET /api/soft-skills/`
- `GET /api/hard-skills/`
- `GET|POST|PATCH|DELETE /api/my-skills/`
- `GET|POST|PATCH|DELETE /api/languages/`
- `GET|POST|PATCH|DELETE /api/educations/`
- `GET|POST|PATCH|DELETE /api/certifications/`
- `GET|POST|PATCH|DELETE /api/licenses/`

### Offres et candidatures

- `GET|POST /api/job-offers/`
- `GET|PATCH|DELETE /api/job-offers/{id}/`
- `GET|POST /api/applications/`
- `GET|PATCH|DELETE /api/applications/{id}/`
- `PATCH /api/applications/{id}/status/` (entreprise)
- `GET /api/company/applications/`

Filtres sur `job-offers`:
- `offer_sector`
- `offer_location`
- `search` (titre + description)
- `ordering` (`offer_created_at`)

### Messagerie et notifications

- `GET|POST|DELETE /api/messages/{other_user_id}/`
- `GET /api/conversations/`
- `GET /api/notifications/`

### IA (OpenRouter)

- `POST /api/generate-job/` (entreprise active)
- `POST /api/cv-advice/` (freelance, PDF requis)
- `POST /api/generate-rejection/` (entreprise)
- `GET /api/dashboard/freelance/`
- `GET /api/dashboard/company/`

## Déploiement

Le projet inclut déjà des dépendances prod (`gunicorn`, `whitenoise`, `dj-database-url`).

Checklist minimale:

1. Passer `DEBUG=False`
2. Définir un `SECRET_KEY` fort via variable d'environnement
3. Restreindre `ALLOWED_HOSTS`
4. Configurer `DATABASE_URL` vers la DB de production
5. Configurer CORS avec les domaines frontend réels
6. Exécuter `collectstatic`
7. Lancer via Gunicorn (exemple):

```bash
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

## Licence

Ce projet est actuellement privé.

## Auteur

**Laetitia Voué** - Projet d'intégration réalisé dans le cadre du BAC3 Informatique.
