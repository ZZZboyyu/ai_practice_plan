# FastAPI Task API

A learning project with task CRUD, status filtering, Pydantic validation,
SQLite persistence through SQLAlchemy, logging, and pytest API tests.

## Run (PowerShell)

Run all commands from the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m uvicorn app:app --reload
```

Open http://127.0.0.1:8000/docs to try the API.
SQLite tables are created when the application is imported.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Tests use a separate in-memory SQLite database.
Database commit-failure rollback is not currently covered.

## Files

- `app.py`: API routes, request and response models, database dependency.
- `models.py`: SQLAlchemy task table.
- `database.py`: SQLite engine and session factory.
- `config.py`: application name and file paths.
- `tests/`: isolated API tests.
- `storage.py`: earlier JSON storage exercise, unused by the current API.
- `migrate.py`: one-time import of a local tasks.json into SQLite. Do not
  rerun against existing IDs; duplicate primary keys will fail.

Local task data, logs, virtual environments and environment files are excluded
from Git. A fresh checkout starts with an empty database.
