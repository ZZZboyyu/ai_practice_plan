import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app
import document_storage
from models import Base


TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


@pytest.fixture(autouse=True)
def isolate_uploads(tmp_path, monkeypatch):
    monkeypatch.setattr(document_storage, "UPLOAD_DIR", tmp_path / "uploads")


@pytest.fixture(autouse=True)
def isolate_database():
    Base.metadata.create_all(TEST_ENGINE)
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    db = TestingSessionLocal()
    db.add_all([
        app.TaskModel(id=1, title="测试任务1", done=False),
        app.TaskModel(id=2, title="测试任务2", done=True),
    ])
    db.commit()
    db.close()

    app.app.dependency_overrides[app.get_db] = override_get_db
    yield
    app.app.dependency_overrides.clear()
    db = TestingSessionLocal()
    db.query(app.TaskModel).delete()
    db.commit()
    db.close()
    Base.metadata.drop_all(TEST_ENGINE)
