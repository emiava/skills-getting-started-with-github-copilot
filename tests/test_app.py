import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

@pytest.fixture
def client():
    return TestClient(app)

def test_root_redirect(client):
    response = client.get("/")
    assert response.status_code == 200
    assert str(response.url).endswith("/static/index.html")

def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data

def test_signup_success(client):
    # Test successful signup
    response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up test@example.com for Chess Club" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Chess Club"]["participants"]

def test_signup_activity_not_found(client):
    response = client.post("/activities/NonExistent/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"

def test_signup_already_signed_up(client):
    # First signup
    client.post("/activities/Programming%20Class/signup?email=duplicate@example.com")
    
    # Try to signup again
    response = client.post("/activities/Programming%20Class/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student already signed up for this activity"

def test_unregister_success(client):
    # First signup
    client.post("/activities/Gym%20Class/signup?email=unregister@example.com")
    
    # Then unregister
    response = client.delete("/activities/Gym%20Class/participants/unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered unregister@example.com from Gym Class" in data["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    data = response.json()
    assert "unregister@example.com" not in data["Gym Class"]["participants"]

def test_unregister_activity_not_found(client):
    response = client.delete("/activities/NonExistent/participants/test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"

def test_unregister_not_signed_up(client):
    response = client.delete("/activities/Basketball%20Team/participants/notsigned@example.com")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student is not signed up for this activity"