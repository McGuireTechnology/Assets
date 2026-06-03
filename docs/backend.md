# Backend

The backend is a FastAPI application.

It uses SQLModel on top of SQLAlchemy with a repo-local SQLite database for development.

```powershell
.\scripts\python.ps1 -m uvicorn app.main:app --app-dir backend --reload
```

OpenAPI documentation is available at `/docs` while the API is running.
