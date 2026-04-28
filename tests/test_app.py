import importlib

import pytest


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.delenv("SPOONACULAR_API_KEY", raising=False)
    app_module = importlib.import_module("app")
    monkeypatch.setattr(app_module, "DATABASE", tmp_path / "test_diet_planner.db")
    app_module.init_db()
    app_module.app.config.update(TESTING=True, SECRET_KEY="test-secret")
    with app_module.app.test_client() as test_client:
        yield test_client


def signup(client):
    return client.post(
        "/signup",
        data={
            "full_name": "Asha Sharma",
            "email": "asha@example.com",
            "password": "strong123",
            "age": "21",
            "gender": "Female",
            "height_cm": "164",
            "weight_kg": "58",
            "diet_preference": "veg",
            "goal": "general_fitness",
            "allergies": "",
        },
        follow_redirects=True,
    )


def login(client):
    return client.post(
        "/login",
        data={"email": "asha@example.com", "password": "strong123"},
        follow_redirects=True,
    )


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_signup_login_dashboard_flow(client):
    assert b"Account created successfully" in signup(client).data
    response = login(client)
    assert response.status_code == 200
    assert b"AI Meal Generator" in response.data
    assert b"Prepare Sample Week" in response.data


def test_generate_meal_and_save_progress(client):
    signup(client)
    login(client)
    meal_response = client.post(
        "/generate-meal",
        data={
            "kitchen_items": "oats, banana, curd",
            "meal_type": "breakfast",
            "diet_preference": "veg",
            "goal": "general_fitness",
        },
        follow_redirects=True,
    )
    assert b"AI meal recommendations generated" in meal_response.data
    assert b"Power Oats Bowl" in meal_response.data

    progress_response = client.post(
        "/save-progress",
        data={"steps": "6200", "water_liters": "2.1", "weight_kg": "58", "notes": "Good energy"},
        follow_redirects=True,
    )
    assert b"Daily progress saved" in progress_response.data


def test_report_download(client):
    signup(client)
    login(client)
    client.post("/prepare-sample-week", follow_redirects=True)
    response = client.get("/download-report")
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
