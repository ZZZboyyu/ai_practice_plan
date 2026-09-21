from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, JSON

Base = declarative_base()
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    done = Column(Boolean,default = False)

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    page_count = Column(Integer, nullable=False)
    pages = Column(JSON, nullable=False)