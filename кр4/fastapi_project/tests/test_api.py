import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_user_success():
    response = client.post("/register", json={
        "username": "testuser",
        "age": 25,
        "email": "test@example.com",
        "password": "securepass123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "User registered"
    assert "user_id" in data


def test_register_user_invalid_age():
    response = client.post("/register", json={
        "username": "younguser",
        "age": 16,
        "email": "young@example.com",
        "password": "securepass123"
    })
    assert response.status_code == 422
    data = response.json()
    assert data["error_type"] == "ValidationError"
    errors = data["details"]["errors"]
    assert any(e["field"] == "age" for e in errors)


def test_register_user_invalid_email():
    response = client.post("/register", json={
        "username": "testuser2",
        "age": 25,
        "email": "not-an-email",
        "password": "securepass123"
    })
    assert response.status_code == 422
    data = response.json()
    assert data["error_type"] == "ValidationError"


def test_register_user_short_password():
    response = client.post("/register", json={
        "username": "testuser3",
        "age": 25,
        "email": "test3@example.com",
        "password": "short"
    })
    assert response.status_code == 422
    data = response.json()
    assert data["error_type"] == "ValidationError"


def test_register_duplicate_email():
    client.post("/register", json={
        "username": "user1",
        "age": 25,
        "email": "duplicate@example.com",
        "password": "securepass123"
    })
    response = client.post("/register", json={
        "username": "user2",
        "age": 30,
        "email": "duplicate@example.com",
        "password": "securepass456"
    })
    assert response.status_code == 400
    assert "Email already exists" in response.text


def test_register_duplicate_username():
    client.post("/register", json={
        "username": "uniqueuser",
        "age": 25,
        "email": "email1@example.com",
        "password": "securepass123"
    })
    response = client.post("/register", json={
        "username": "uniqueuser",
        "age": 30,
        "email": "email2@example.com",
        "password": "securepass456"
    })
    assert response.status_code == 400
    assert "Username already exists" in response.text


def test_get_users_empty():
    response = client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_users_after_registration():
    client.post("/register", json={
        "username": "viewer",
        "age": 25,
        "email": "viewer@example.com",
        "password": "securepass123"
    })
    
    response = client.get("/users")
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 1
    usernames = [u["username"] for u in users]
    assert "viewer" in usernames


def test_get_product_success():
    response = client.get("/product/5")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 5
    assert data["name"] == "Продукт"


def test_get_product_not_found():
    response = client.get("/product/0")
    assert response.status_code == 404
    data = response.json()
    assert data["error_type"] == "CustomExceptionB"
    assert "не найден" in data["message"]


def test_get_product_negative_id():
    response = client.get("/product/-5")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == -5  



def test_check_value_success():
    response = client.get("/check/50")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["value"] == 50


def test_check_value_negative():
    response = client.get("/check/-5")
    assert response.status_code == 400
    data = response.json()
    assert data["error_type"] == "CustomExceptionA"
    assert "меньше 0" in data["message"]


def test_check_value_too_large():
    response = client.get("/check/150")
    assert response.status_code == 404
    data = response.json()
    assert data["error_type"] == "CustomExceptionB"
    assert "больше 100" in data["message"]


def test_check_value_boundary_min():
    response = client.get("/check/0")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


def test_check_value_boundary_max():
    response = client.get("/check/100")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
