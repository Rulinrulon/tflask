import pytest
from flask import g, session
from flaskr.db import get_db

def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a', 'passwordcheck': 'a', 'email': 'a@a'}
    )
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None

@pytest.mark.parametrize(('username', 'password', 'passwordcheck', 'email', 'message'), (
    ('', '','','', b'Inserte nombre de usuario.'),
    ('a', '','','', b'Inserte una contrasena.'),
    ('a', '123','321','', b'Las contrasenas no coinciden'),
    ('test', 'test', 'test', 'test@gmail.com', b'El usuario {username} o la direccion de mail {email} ya estan en uso.'),
))
def test_register_validate_input(client, username, password, passwordcheck, email, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password, 'passwordcheck': passwordcheck, 'email': email}
    )
    assert message in response.data

def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'

@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Nombre de usuario incorrecto.'),
    ('test', 'a', b'Contrasena incorrecta.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session