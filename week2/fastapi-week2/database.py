from sqlalchemy import create_engine
from models import Base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./tasks.db"




engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

Base.metadata.create_all(engine)
SessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine
)