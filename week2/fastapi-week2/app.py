import logging
from fastapi import FastAPI, HTTPException, status, Depends
from typing import Optional
from pydantic import BaseModel, Field
from config import APP_NAME, LOG_FILE
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Task as TaskModel

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


app = FastAPI(title=APP_NAME)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, description="任务标题不能为空")
    done: bool = False


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    done: Optional[bool] = None


class Task(BaseModel):
    id: int
    title: str
    done: bool


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello, FastAPI!"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tasks", response_model=list[Task])
def list_tasks(
    done:Optional[bool] = None,
    db:Session = Depends(get_db),
):
    query = db.query(TaskModel)
    if done is not None:
        query = query.filter(TaskModel.done ==done)
    return query.all()

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int ,db:Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

@app.post("/tasks", status_code=status.HTTP_201_CREATED, response_model=Task)
def create_task(task_data: TaskCreate,db:Session = Depends(get_db)):
    new_task =TaskModel(
        title = task_data.title,
        done = task_data.done
    )
    logger.info("Creating task id=%s", new_task.title)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    for key, value in task_data.model_dump(exclude_none=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    logger.info("Updating task id=%s", task_id)
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    logger.info("Deleting task id=%s", task_id)
