import json
from database import SessionLocal
from models import Task

with open("tasks.json","r",encoding = "utf_8") as f:
    tasks = json.load(f)

db = SessionLocal()
for task in tasks:
    db_task = Task(
        id = task["id"],
        title=task["title"],
        done=task["done"],
    )
    db.add(db_task)
db.commit()
db.close()
print(f"成功迁移 {len(tasks)} 条任务")