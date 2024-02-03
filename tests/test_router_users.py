import pytest
from unittest.mock import MagicMock

from cloudinary.uploader import upload_image

from src.models.user import User
from pathlib import Path

@pytest.fixture
def cur_user(client, session, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.confirm_email", mock_send_email)
    client.post("api/auth/signup", json=user)
    new_user: User = session.query(User).filter(User.email==user.get("username")).first()
    new_user.confirmed = True
    session.commit()

    return new_user


def test_users_me(client, session, cur_user):
    
    response = client.get("/api/users/me")

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == cur_user.id
    assert data["email"]
    assert data["avatar"] is None
    assert data["created_at"]
    assert data["updated_at"]


def test_user_avatar(client, session, cur_user, monkeypatch):
    url = "www.test/1212/reeyey.jpeg"
    public_id = "1212/reeyey"
    mock_upload = MagicMock()
    mock_upload.return_value = MagicMock(url=url, public_id=public_id)
    monkeypatch.setattr("src.services.media.upload_image", mock_upload)

    file_name = "test.jpeg"
    path = Path(file_name)
    if not path.exists():
        path.touch()

    response = client.patch("/api/users/avatar" ,files={"file": open(file_name, 'rb')})

    if path.exists():
        path.unlink()

    assert response.status_code == 200, response.text
    upd_user = session.query(User).filter(User.email==cur_user.email).first()
    assert upd_user.avatar == url
    assert upd_user.avatar_cld == public_id
    assert upd_user.id == cur_user.id

    
    