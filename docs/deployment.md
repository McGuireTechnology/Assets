# Deployment

Assets is planned as a three-surface deployment:

| Surface | Platform | Responsibility |
| --- | --- | --- |
| Documentation | GitHub Pages | Public VitePress documentation site |
| Frontend | Cloudflare Pages | Vue/Vite application and static assets |
| Backend API | DigitalOcean | FastAPI application runtime |
| Database | DigitalOcean PostgreSQL | Persistent application data |

## Local Docker

The local Docker stack is defined in `compose.yaml` and runs the frontend, backend, docs, and PostgreSQL together.

```sh
mise run docker:up
```

| Service | URL |
| --- | --- |
| Frontend | `http://localhost:5173` |
| Backend API | `http://localhost:8000` |
| API docs | `http://localhost:8000/docs` |
| Documentation | `http://localhost:5174` |
| PostgreSQL | `localhost:5433` |

The backend container connects to PostgreSQL through the Compose service name and uses the same `DATABASE_URL` environment variable expected in production.

Stop the stack with:

```sh
mise run docker:down
```

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

Expected production command shape:

```sh
python -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
```

Production configuration should come from environment variables rather than checked-in files.

Configure the DigitalOcean App Platform service in the dashboard rather than with a checked-in app spec.

Recommended backend settings:

| Setting | Value |
| --- | --- |
| Source directory | `backend` |
| Dockerfile path | `Dockerfile` |
| HTTP port | `8080` |
| Health check path | `/health` |

Set `ASSETS_CORS_ORIGINS` to the Cloudflare Pages production origin.

## Database

Local development uses SQLite by default. Production is planned for DigitalOcean PostgreSQL.

The backend should use a production database URL supplied by the DigitalOcean environment:

```text
DATABASE_URL=postgresql://...
```

SQLite remains useful for local development, but production migrations, backups, and connection limits should be designed around PostgreSQL.

For production, use a managed DigitalOcean PostgreSQL cluster and provide its private connection string to the backend as `DATABASE_URL`.

## Open Decisions

- Choose the DigitalOcean runtime target for FastAPI, such as App Platform, Droplet, or container deployment.
- Decide how database migrations will be authored and applied.
- Decide whether Cloudflare Pages previews should target a shared staging API or per-branch API environments.
- Define production, staging, and preview environment variable names.
