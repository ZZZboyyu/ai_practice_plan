from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "tasks.db"
UPLOAD_DIR = BASE_DIR / "uploads"
DATA_FILE = BASE_DIR / "tasks.json"
LOG_FILE = BASE_DIR / "app.log"
APP_NAME = "FastAPI week2 Practice"
