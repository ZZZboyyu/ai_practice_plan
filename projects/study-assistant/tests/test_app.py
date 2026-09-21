from fastapi.testclient import TestClient
from pathlib import Path
from app import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_tasks():
    response = client.get("/tasks")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_existing_task():
    response = client.get("/tasks/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_missing_task():
    response = client.get("/tasks/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_create_task():
    response = client.post(
        "/tasks",
        json={"title": "测试任务", "done": False},
    )

    assert response.status_code == 201
    assert response.json()["title"] == "测试任务"
    assert response.json()["done"] is False


def test_create_task_without_title():
    response = client.post(
        "/tasks",
        json={"done": False},
    )

    assert response.status_code == 422


def test_filter_tasks():
    response = client.get("/tasks?done=false")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

    for task in response.json():
        assert task["done"] is False
def test_update_task():
    response = client.put(
        "/tasks/1",
        json={"title": "更新后的任务", "done": True},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "更新后的任务",
        "done": True,
    }


def test_delete_task():
    response = client.delete("/tasks/1")

    assert response.status_code == 204
    assert response.content == b""


def test_update_missing_task():
    response = client.put(
        "/tasks/999999",
        json={"title": "不存在的任务"},
    )

    assert response.status_code == 404


def test_delete_missing_task():
    response = client.delete("/tasks/999999")

    assert response.status_code == 404
def test_create_task_with_empty_title():
    response = client.post(
        "/tasks",
        json={"title": ""},
    )
    assert response.status_code == 422
    
def test_update_task_with_empty_title():
    response = client.put(
        "/tasks/1",
        json={"title": ""},
    )
    assert response.status_code == 422


def test_chat(monkeypatch):
    monkeypatch.setattr(
        "app.ask_ai",
        lambda message: "这是测试回答",
    )

    response = client.post(
        "/chat",
        json={"message": "你好"},
    )

    assert response.status_code == 200
    assert response.json() == {"answer": "这是测试回答"}


def test_chat_with_empty_message():
    response = client.post(
        "/chat",
        json={"message": ""},
    )

    assert response.status_code == 422

def test_upload_txt():
    response = client.post(
        "/document/upload",
        files = {
            "file":(
                "notes.txt",
                "今日学习文件上传".encode("utf-8"),
                "text/plain",
            )
        }
    )
    assert response.status_code == 200
    assert response.json()["text"] == "今日学习文件上传"
    assert response.json()["char_count"] == 8

def test_upload_empty_txt():
    response = client.post(
        "/document/upload",
        files={
            "file": (
                "empty.txt",
                "   ".encode("utf-8"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "文件不能是空的"


def test_upload_invalid_pdf():
    response = client.post(
        "/document/upload",
        files = {
            "file":(
                "notes.pdf",
                "测试内容".encode("utf-8"), 
                "application/pdf",
            )
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "PDF 无法读取，请检查文件是否损坏或加密"

def test_upload_pdf():
    pdf_path = (
        Path(__file__).resolve().parent.parent
        / "output" / "pdf" / "day4-course-notes.pdf"
    )
    with pdf_path.open("rb") as file:
        response =client.post(
            "/document/upload",
            files={"file": ("notes.pdf", file, "application/pdf")},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["page_count"] == 2
    assert "第一章：文件上传" in data["pages"][0]["text"]
    assert "第二章：PDF 文字提取" in data["pages"][1]["text"]

def test_upload_scanned_pdf():
    pdf_path = (
        Path(__file__).resolve().parent.parent
        / "output" / "pdf" / "day4-scanned-notes.pdf"
    )
    with pdf_path.open("rb") as file:
        response =client.post(
            "/document/upload",
            files={"file": ("notes.pdf", file, "application/pdf")},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["page_count"] == 2
    assert "文件上传" in data["pages"][0]["text"]
    assert "文字提取" in data["pages"][1]["text"]

def test_upload_txt_then_get_document():
    upload_response = client.post(
        "/document/upload",
        files={
            "file": (
                "notes.txt",
                "今天学习资料保存".encode("utf-8"),
                "text/plain",
            )
        },
    )

    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    document_id = upload_data["id"]

    response = client.get(f"/documents/{document_id}")

    assert response.status_code == 200
    assert response.json()["filename"] == "notes.txt"
    assert response.json()["pages"][0]["text"] == "今天学习资料保存"
    assert response.json()["page_count"] == 1

    saved_path = Path(upload_data["storage_path"])
    assert saved_path.exists()
    assert saved_path.read_bytes() == "今天学习资料保存".encode("utf-8")
    queried_data = response.json()
    assert queried_data["storage_path"] == upload_data["storage_path"]

def test_get_missing_document():
    response = client.get("/documents/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "资料不存在"
    
def test_document_summary(monkeypatch):
    def fake_summary(pages):
        assert pages[0]["text"] == "Python 是编程语言。"
        return "【第1页】Python 是编程语言。"
    monkeypatch.setattr("app.summarize_document",fake_summary)
    upload_response = client.post(
        "/document/upload",
        files = {
            "file":(
                "notes.txt",
                "Python 是编程语言。".encode("utf-8"),
                "text/plain",
            )
        }
    )
    assert upload_response.status_code == 200
    document_id = upload_response.json()["id"]
    response = client.post(f"/documents/{document_id}/summary")
    assert response.status_code == 200
    assert response.json()["summary"] == "【第1页】Python 是编程语言。"

def test_summary_missing_document():
    response = client.post("/documents/999999/summary")

    assert response.status_code == 404
    assert response.json()["detail"] == "资料不存在"

def test_document_summary_failure(monkeypatch):
    def fake_summary(pages):
        raise ValueError("模拟ai没有返回文本")
        return "【第1页】Python 是编程语言。"
    monkeypatch.setattr("app.summarize_document",fake_summary)
    upload_response = client.post(
        "/document/upload",
        files = {
            "file":(
                "notes.txt",
                "Python 是编程语言。".encode("utf-8"),
                "text/plain",
            )
        }
    )
    assert upload_response.status_code == 200
    document_id = upload_response.json()["id"]
    response = client.post(f"/documents/{document_id}/summary")
    assert response.status_code == 502
    assert response.json()["detail"] == "ai摘要生成失败，请稍后再试"

def test_document_key_summary(monkeypatch):
        def fake_key_points(pages):
            assert pages[0]["text"] == "Python 是编程语言。"
            return "【第1页】知识点：Python 是编程语言。"
        monkeypatch.setattr("app.extract_key_points", fake_key_points)
        upload_response = client.post(
            "/document/upload",
            files = {
                "file":(
                    "notes.txt",
                    "Python 是编程语言。".encode("utf-8"),
                    "text/plain",
                )
            }
        )
        assert upload_response.status_code == 200
        document_id = upload_response.json()["id"]
        response = client.post(f"/documents/{document_id}/key-points")
        assert response.status_code == 200
        assert response.json()["key_points"] == "【第1页】知识点：Python 是编程语言。"