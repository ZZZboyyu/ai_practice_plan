import logging
import httpx
from document_ai import extract_key_points, summarize_document
from ai_client import ask_ai
from fastapi import FastAPI, HTTPException, status, Depends
from typing import Optional
from pydantic import BaseModel, Field
from config import APP_NAME, LOG_FILE
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, File
from database import SessionLocal
from models import Task as TaskModel
from pypdf import PdfReader
from pypdf.errors import PyPdfError
from read_pdf import extract_pdf_pages
from document_storage import save_document
from sqlalchemy.exc import SQLAlchemyError
from models import Document as DocumentModel

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


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    answer: str


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


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        return ChatResponse(answer=ask_ai(request.message))
    except (httpx.HTTPError, ValueError) as error:
        logger.error("AI request failed: %s", error)
        raise HTTPException(status_code=502, detail="无法连接 AI 服务")


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
@app.post("/document/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    filename = (file.filename or "").lower()
    if filename.endswith(".pdf"):
        try:
            pages = extract_pdf_pages(file.file)
        except (PyPdfError, ValueError):
            raise HTTPException(
                status_code=400,
                detail="PDF 无法读取，请检查文件是否损坏或加密",
            )

        try:
            document = save_document(file, pages, db)
        except (OSError, SQLAlchemyError):
            raise HTTPException(
                status_code=500,
                detail="资料保存失败，请稍后重试",
            )

        return {
            "id": document.id,
            "filename": document.filename,
            "page_count": document.page_count,
            "pages": document.pages,
            "storage_path": document.storage_path,
        }
    if not file.filename or not file.filename.lower().endswith(".txt"):
        raise HTTPException(status_code = 400, detail = "目前只支持txt和pdf")
    content = file.file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code = 400,
            detail = "文件编码不是 UTF-8，请转换后再上传",
        )
    if not text.strip():
        raise HTTPException(
            status_code = 400,
            detail = "文件不能是空的",
        )
    pages = [{
        "page_number": 1,
        "text": text,
        "char_count": len(text),
    }]

    try:
        document = save_document(file, pages, db)
    except (OSError, SQLAlchemyError):
        raise HTTPException(
            status_code=500,
            detail="资料保存失败，请稍后重试",
        )

    return {
        "id": document.id,
        "filename": document.filename,
        "text": text,
        "char_count": len(text),
        "storage_path": document.storage_path,
    }

@app.get("/documents/{document_id}")
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.get(DocumentModel, document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="资料不存在")

    return {
        "id": document.id,
        "filename": document.filename,
        "page_count": document.page_count,
        "pages": document.pages,
        "storage_path": document.storage_path,
    }

@app.post("/documents/{document_id}/summary")
def create_document_summary(
    document_id : int,
    db:Session = Depends(get_db),
):
    document = db.get(DocumentModel,document_id)
    if document is None:
        raise HTTPException(status_code = 404,detail = "资料不存在")
    if not any(page["text"].strip() for page in document.pages):
        raise HTTPException(status_code = 422,detail = "资料没有可总结文字")
    try:
        summary = summarize_document(document.pages)
    except(httpx.HTTPError,ValueError):
        raise HTTPException(
            status_code = 502,
            detail = "ai摘要生成失败，请稍后再试",
        )
    return{
        "document_id":document.id,
        "summary":summary,
    }

@app.post("/documents/{document_id}/key-points")
def create_document_key_points(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.get(DocumentModel, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="资料不存在")
    if not any(page["text"].strip() for page in document.pages):
        raise HTTPException(status_code=422, detail="资料没有可提取的文字")
    try:
        key_points = extract_key_points(document.pages)
    except (httpx.HTTPError, ValueError):
        raise HTTPException(status_code=502, detail="知识点生成失败，请稍后再试")
    return {
        "document_id": document.id,
        "key_points": key_points,
    }
