from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_recipe_validation_rejects_empty_ingredients():
    response = client.post(
        "/api/v1/recipes/generate",
        json={"ingredients": [], "chef_id": "chef-zama", "chef_name": "Chef Zama"},
    )
    assert response.status_code == 422
