from pathlib import Path
from uuid import uuid4
from shutil import copyfileobj
from config import UPLOAD_DIR
from models import Document
from sqlalchemy.exc import SQLAlchemyError

def save_uploaded_file(file):
    UPLOAD_DIR.mkdir(parents=True,exist_ok=True)
    suffix = Path(file.filename).suffix.lower()
    save_path = UPLOAD_DIR / f"{uuid4().hex}{suffix}"
    file.file.seek(0)
    with save_path.open("xb") as destination:
        copyfileobj(file.file,destination)
    return save_path

def save_document(file,pages,db):
    save_path = save_uploaded_file(file)

    document = Document(
        filename = file.filename,
        storage_path = str(save_path),
        page_count = len(pages),
        pages = pages,
    )
    try:
        db.add(document)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        save_path.unlink()
        raise
    db.refresh(document)
    return document
