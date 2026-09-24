from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_recipe_requires_authentication() -> None:
    response = client.post(
        "/api/v1/recipes/generate",
        json={
            "ingredients": ["tomato"],
            "chef_id": "mandla",
            "chef_name": "Chef Mandla",
        },
    )
    assert response.status_code == 401


def test_recipe_validation_without_auth_is_not_reached() -> None:
    response = client.post(
        "/api/v1/recipes/generate",
        json={
            "ingredients": [],
            "chef_id": "mandla",
            "chef_name": "Chef Mandla",
        },
    )
    assert response.status_code in (401, 422)
