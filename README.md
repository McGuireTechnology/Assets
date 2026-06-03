# Assets

Assets is scaffolded as a small full-stack workspace by McGuire Technology, LLC - Assets:

- `frontend/` - Vue 3 site powered by Vite.
- `backend/` - FastAPI service.
- `docs/` - VitePress documentation site.

## Frontend

```powershell
.\scripts\npm.ps1 --workspace frontend run dev
```

The Vue app expects the API at `http://localhost:8000` by default. Override it with `VITE_API_BASE_URL`.

## Backend

Local development uses a repo-local SQLite database by default:

```text
sqlite:///./.data/assets.sqlite3
```

Run the API:

```powershell
.\scripts\python.ps1 -m uvicorn app.main:app --app-dir backend --reload
```

FastAPI will serve the OpenAPI UI at `http://localhost:8000/docs`.

## Documentation

```powershell
.\scripts\npm.ps1 --workspace docs run dev
```

VitePress will serve docs at `http://localhost:5174`.

## GitHub Pages

The docs site is deployed automatically to GitHub Pages from `main` via `.github/workflows/docs-pages.yml`.
The published site uses the custom domain `assets.mcguire.technology` via `docs/.vitepress/public/CNAME`.
