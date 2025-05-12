# import pytest
from fastapi.testclient import TestClient
from app.routes.auth import router, create_access_token
from ..app import create_app

app = create_app()

app.include_router(router)
client = TestClient(app)

def test_login_for_access_token():
    response = client.post(
        "/token",
        data={"username": "johndoe", "password": "secret"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_for_access_token_invalid_credentials():
    response = client.post(
        "/token",
        data={"username": "johndoe", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

def test_read_users_me():
    access_token = create_access_token(data={"sub": "johndoe"})
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "johndoe"

def test_read_users_me_no_token():
    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

def test_read_users_me_invalid_token():
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid token"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}

def test_read_own_items():
    access_token = create_access_token(data={"sub": "johndoe"})
    response = client.get(
        "/users/me/items/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json() == [{"item_id": "Foo", "owner": "johndoe"}]

def test_read_own_items_no_token():
    response = client.get("/users/me/items/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

def test_read_own_items_invalid_token():
    response = client.get(
        "/users/me/items/",
        headers={"Authorization": "Bearer invalid token"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}