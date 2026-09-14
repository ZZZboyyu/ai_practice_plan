from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base
Base = declarative_base()
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    done = Column(Boolean,default = False)