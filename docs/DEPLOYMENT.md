# Déploiement

Le projet est conçu pour deux cibles complémentaires : **frontend statique sur Vercel** et **API conteneurisée Docker** sur n'importe quel runtime (Render, Fly.io, Scaleway, AWS ECS, GCP Cloud Run).

## 1. Frontend · Vercel

```bash
cd frontend
npm i -g vercel
vercel link
vercel --prod
```

Le `frontend/vercel.json` définit déjà :
- pas de build (HTML + JS pur via CDN)
- headers de sécurité (X-Frame-Options, CSP-friendly)
- cache 5 minutes par défaut
- rewrite SPA-style sur `index.html`

> **Variable d'environnement à définir dans Vercel ·**
> avant le déploiement, éditer `frontend/app.js` ligne `API_BASE` pour pointer
> sur l'URL de l'API déployée (étape suivante).

## 2. API · Docker

### Build local

```bash
docker build -t urban-data-explorer-api:1.0.0 .
docker run -p 8000:8000 \
    -e JWT_SECRET="$(openssl rand -hex 32)" \
    -e DEMO_USER=admin -e DEMO_PASSWORD=admin \
    urban-data-explorer-api:1.0.0
```

### Full-stack local

```bash
docker compose up --build
# → API   http://localhost:8000
# → Front http://localhost:5500
```

### Cloud · Render

1. Créer un service Web sur https://render.com → "New Web Service".
2. Source · ce repo, branche `main`, runtime `Docker`.
3. Variables d'environnement ·
   - `JWT_SECRET` (générer via `openssl rand -hex 32`)
   - `DEMO_USER`, `DEMO_PASSWORD`
4. Le `HEALTHCHECK` Docker garantit le rolling restart sain.

### Cloud · Fly.io

```bash
fly launch --copy-config --no-deploy
fly secrets set JWT_SECRET=$(openssl rand -hex 32)
fly deploy
```

### Cloud · GCP Cloud Run

```bash
gcloud run deploy ude-api \
    --source . \
    --port 8000 \
    --region europe-west1 \
    --allow-unauthenticated \
    --set-env-vars JWT_SECRET=...
```

## 3. CI/CD · GitHub Actions

`.github/workflows/ci.yml` exécute à chaque push :
- `ruff check` (lint)
- `pytest -q` (tests)
- `python scripts/seed_demo_db.py` (sanity du seed)
- `python scripts/build_report.py` (build PDF)
- `python scripts/build_slides.py` (build PPT)
- API smoke test (boot + curl `/health`)
- Upload des livrables (PDF, PPT, DuckDB) en artifacts (rétention 14 j)

Pour automatiser le déploiement (continuous delivery), ajouter un job
`deploy` qui appelle `vercel --prod --token $VERCEL_TOKEN` (frontend) et
`flyctl deploy --remote-only` (API), gated sur `if: github.ref == 'refs/heads/main'`.

## 4. Sécurité production

Avant exposition publique ·
- [ ] Régénérer `JWT_SECRET` (32 octets minimum)
- [ ] Changer `DEMO_USER` / `DEMO_PASSWORD` ou brancher Auth0 / Cognito
- [ ] Restreindre le CORS (`api/main.py`) au domaine frontend uniquement
- [ ] Activer rate-limiting (slowapi, NGINX, Cloudflare)
- [ ] Configurer un WAF (Cloudflare, AWS WAF) sur l'API
- [ ] Logs centralisés (Datadog, Grafana Loki, OpenTelemetry)

## 5. Observabilité (optionnel)

Endpoints suggérés à wrapper :
- `prometheus_client` pour exposer `/metrics`
- `opentelemetry-instrumentation-fastapi` pour traces distribuées
- Sentry pour le tracking d'erreurs frontend (`Sentry.init({ dsn })`)
