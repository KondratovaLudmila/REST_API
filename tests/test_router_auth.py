from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from src.models.user import User
from src.routes.auth import security
from src.services.auth import auth_token


def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.confirm_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.get("username")
    assert "id" in data["user"]


def test_repeat_create_user(client, user):
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "user is already exists"


def test_signin_user_not_confirmed(client, user):
    response = client.post(
        "/api/auth/signin",
        data=user,
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"


def test_signin_user(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('username')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/signin",
        data=user,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"


def test_signin_wrong_password(client, user):
    response = client.post(
        "/api/auth/signin",
        data={"username": user.get('username'), "password": 'password'},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"


def test_signin_wrong_email(client, user):
    response = client.post(
        "/api/auth/signin",
        data={"username": 'email', "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"


def test_refresh_token(client, session, user):
    cur_user: User = session.query(User).filter(User.email == user.get('username')).first()
    response = client.get("/api/auth/refresh_token", headers={"Authorization": f"Bearer {cur_user.refresh_token}"})
    
    upd_user: User = session.query(User).filter(User.email == user.get('username')).first()
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["access_token"] is not None
    assert data["refresh_token"] == upd_user.refresh_token
    assert data["token_type"] is not None


def test_refresh_token_invalid_token(client):
    response = client.get("/api/auth/refresh_token", headers={"Authorization": "Bearer test"})
    
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid token"


def test_forgot_password(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.password_reset_email", mock_send_email)
    response = client.post("/api/auth/forgot_password", json={"email": user.get("username")})

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["result"] == True
    assert data["detail"] is not None


def test_reset_password(client, user, monkeypatch, session):
    mock_token = MagicMock(spec=auth_token)
    mock_token.get_payload.return_value = {"sub": user.get("username")}
    monkeypatch.setattr("src.routes.auth.auth_token", mock_token)

    cur_user: User = session.query(User).filter(User.email==user.get("username")).first()
    old_pass = cur_user.password
    new_pass = "123"
    
    response = client.post("/api/auth/reset_password/complete", json={"token": "test", "password": new_pass})

    cur_user: User = session.query(User).filter(User.email==user.get("username")).first()
    assert response.status_code == 200, response.text
    assert cur_user.password != old_pass
    assert cur_user.refresh_token is None



    



        
