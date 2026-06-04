# Assets

Assets is scaffolded as a small full-stack workspace by McGuire Technology, LLC - Assets:

- `frontend/` - Vue 3 site powered by Vite.
- `backend/` - FastAPI service.
- `docs/` - VitePress documentation site.

## Bootstrap

Install the Mise-managed toolchain after cloning. Mise provides Node and Python from [mise.toml](mise.toml).

macOS/Linux:

```sh
./scripts/install.sh
source ./scripts/activate.sh
mise --version
```

The activation script must be sourced so it can update the current shell's `PATH`. It also adds an `(Assets)` prompt marker for the current session.

Windows:

```powershell
.\scripts\install.ps1
. .\scripts\activate.ps1
mise --version
```

If Mise is already installed, you can run the setup directly:

```sh
mise install --locked
```

```sh
mise run bootstrap
```

The macOS/Linux installer keeps the `mise` binary in `.cache/mise/bin/mise` when it is not already installed globally. Source `scripts/activate.sh` or run `scripts/activate.ps1` in a new shell session to put the repo-local Mise on `PATH`, enable Mise shims, store Mise-managed tools under `.cache/mise/data`, and keep Python/npm project dependencies under `.cache/`.

Tool downloads are pinned by [mise.lock](mise.lock). Update it with `mise lock` when changing [mise.toml](mise.toml).

Do not run `mise activate` by itself; it prints shell code. Use `source ./scripts/activate.sh`, or run `eval "$(mise activate zsh)"` after `mise` is already on `PATH`.

VS Code uses the workspace terminal profile in [.vscode/settings.json](.vscode/settings.json) to activate the project automatically for new integrated terminals. If `mise` has not been installed yet, the terminal opens normally and prints the install command to run. Codex guidance lives in [AGENTS.md](AGENTS.md), which tells coding agents to source the activation script before project commands.

## Frontend

```sh
mise run frontend:dev
```

The Vue app expects the API at `http://localhost:8000` by default. Override it with `VITE_API_BASE_URL`.

## Backend

Local development uses a repo-local SQLite database by default:

```text
sqlite:///./.data/assets.sqlite3
```

Run the API:

```sh
mise run backend:dev
```

FastAPI will serve the OpenAPI UI at `http://localhost:8000/docs`.

## Documentation

```sh
mise run docs:dev
```

VitePress will serve docs at `http://localhost:5174`.

## GitHub Pages

The docs site is deployed automatically to GitHub Pages from `main` via `.github/workflows/docs-pages.yml`.
The published site uses the custom domain `assets.mcguire.technology` via `docs/.vitepress/public/CNAME`.
