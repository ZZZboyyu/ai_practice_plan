from fastapi.testclient import TestClient

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
