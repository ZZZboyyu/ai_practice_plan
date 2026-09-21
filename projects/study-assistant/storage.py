"""任务数据的 JSON 文件读写工具。"""
import json
from config import DATA_FILE
def load_tasks():
    if not DATA_FILE.exists():
        
            return[]
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data,list) else []
    except (OSError,json.JSONDecodeError):
        return []

def save_tasks(tasks: list[dict[str, object]]) -> None:
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(tasks, file, ensure_ascii=False, indent=2)
    except (OSError):
        print(f"Failed to save tasks to {DATA_FILE}")
        raise
