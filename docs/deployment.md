# Deployment

Assets is planned as a three-surface deployment:

| Surface | Platform | Responsibility |
| --- | --- | --- |
| Documentation | GitHub Pages | Public VitePress documentation site |
| Frontend | Cloudflare Pages | Vue/Vite application and static assets |
| Backend API | DigitalOcean | FastAPI application runtime |
| Database | DigitalOcean PostgreSQL | Persistent application data |

## Documentation

The docs site lives in `docs/` and is deployed to GitHub Pages from `main`.

- Build command: `npm run build`
- Working directory: `docs/`
- Output directory: `docs/.vitepress/dist`
- Current workflow: `.github/workflows/docs-pages.yml`

The published documentation uses the custom domain configured in `docs/.vitepress/public/CNAME`.

## Frontend

The frontend lives in `frontend/` and is planned for Cloudflare Pages.

- Build command: `npm run build`
- Working directory: `frontend/`
- Output directory: `frontend/dist`

Cloudflare Pages should provide the API base URL at build time:

```text
VITE_API_BASE_URL=https://<api-host>
```

The frontend should not store server secrets. Anything sensitive belongs in the backend environment.

## Backend API

The backend lives in `backend/` and is planned for DigitalOcean.

- Runtime: Python 3.13
- Application server: Uvicorn
- ASGI app: `app.main:app`
- Container: `backend/Dockerfile`
- App spec: `.do/app.yaml`

Expected production command shape:

```sh
python -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
```

Production configuration should come from environment variables rather than checked-in files.

The DigitalOcean App Platform spec in `.do/app.yaml` defines the `api` service, uses `backend/` as the source directory, builds `backend/Dockerfile`, and checks `/health`.

Deploy or update through `doctl` after creating/configuring the app:

```sh
doctl apps create --spec .do/app.yaml
```

```sh
doctl apps update <app-id> --spec .do/app.yaml
```

Before deploying, set `ASSETS_CORS_ORIGINS` in `.do/app.yaml` to the Cloudflare Pages production origin.

## Database

Local development uses SQLite by default. Production is planned for DigitalOcean PostgreSQL.

The backend should use a production database URL supplied by the DigitalOcean environment:

```text
DATABASE_URL=postgresql://...
```

SQLite remains useful for local development, but production migrations, backups, and connection limits should be designed around PostgreSQL.

The starter `.do/app.yaml` provisions a DigitalOcean PostgreSQL dev database with `production: false`. For production, use a managed database cluster and update the database block with `production: true` and the target `cluster_name`.

## Open Decisions

- Choose the DigitalOcean runtime target for FastAPI, such as App Platform, Droplet, or container deployment.
- Decide how database migrations will be authored and applied.
- Decide whether Cloudflare Pages previews should target a shared staging API or per-branch API environments.
- Define production, staging, and preview environment variable names.
