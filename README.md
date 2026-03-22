# Livebox Dashboard

Interface web pour administrer votre box Orange (Livebox) depuis un navigateur.

## Fonctionnement

L'application est composée de deux parties :

- **Backend** (Python / FastAPI) — fait le lien entre le navigateur et l'API de la Livebox
- **Frontend** (Angular) — l'interface graphique servie par le backend

Au premier accès, vous saisissez l'URL de votre Livebox (par défaut `http://192.168.1.1`), votre identifiant et votre mot de passe. Le backend vérifie les credentials directement auprès de la box et vous délivre un token de session. Aucune configuration préalable n'est nécessaire.

## Déploiement avec Docker

### Prérequis

- Docker installé sur la machine hôte
- Être sur le même réseau que la Livebox (LAN ou VPN)

### Lancer l'application

```bash
docker run -d \
  --name livebox_dashboard \
  --restart unless-stopped \
  -p 4350:4350 \
  livebox_dashboard
```

Accédez ensuite à **http://\<ip-de-votre-serveur\>:4350** depuis votre navigateur.

### Construire l'image soi-même

```bash
git clone <url-du-repo>
cd livebox
docker build -t livebox_dashboard .
```

### Avec Docker Compose

```bash
docker compose up -d
```

## Développement local

### Backend

```bash
cd backend
uv sync
uv run uvicorn main:app --reload --port 4350
```

### Frontend

```bash
cd frontend
npm install
npm start        # démarre sur http://localhost:4200
```

Le frontend en mode dev proxifie automatiquement les appels API vers le backend sur le port 4350.
