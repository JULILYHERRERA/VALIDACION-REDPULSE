import pytest
import sys
import os
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    with app.test_client() as client:
        yield client


def test_visualizar_usuarios_get_happy_path(client, monkeypatch):
    """Prueba GET exitosa. Stub y Dummy."""
    # Stub: lista de usuarios simulada
    usuarios_mock = [
        MagicMock(numero_documento="111", tipo_documento="Cedula", nombre="User1", correo="u1@test.com",
                  tipo_de_sangre="O+", donante=True, enfermero=False, puntos=10, total_donado=500),
        MagicMock(numero_documento="222", tipo_documento="Cedula", nombre="User2", correo="u2@test.com",
                  tipo_de_sangre="A+", donante=False, enfermero=True, puntos=5, total_donado=250)
    ]
    monkeypatch.setattr("app.obtenerTodosUsuariosNoAdmin", lambda: usuarios_mock)
    # Dummy
    dummy = []

    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    response = client.get("/visualizar_usuarios")

    assert response.status_code == 200
    assert b"User1" in response.data
    assert b"User2" in response.data
    assert dummy is not None


def test_visualizar_usuarios_post_eliminar_no_admin(client, monkeypatch):
    """Prueba POST exitosa: eliminar usuario no admin. Stub + Spy."""
    # Stubs
    usuario_mock = MagicMock(admin=False, nombre="Test User")
    monkeypatch.setattr("app.obtenerUsuarioPorDocumento", lambda doc, tip: usuario_mock)

    # Spy: registrar llamada a eliminarUsuario
    call_args = []
    def spy_eliminarUsuario(doc, tip):
        call_args.append((doc, tip))
    monkeypatch.setattr("app.eliminarUsuario", spy_eliminarUsuario)

    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    response = client.post("/visualizar_usuarios", data={
        "numero_documento": "123",
        "tipo_documento": "Cedula"
    }, follow_redirects=False)

    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert sess["admin_usuarios_status"] == "success"
        assert sess["admin_usuarios_user"]["nombre"] == "Test User"

    # Verificar que el Spy registró la llamada
    assert len(call_args) == 1
    assert call_args[0] == ("123", "Cedula")


def test_visualizar_usuarios_post_eliminar_admin(client, monkeypatch):
    """Prueba unhappy: intento de eliminar admin. Stub."""
    # Stub: usuario admin
    usuario_mock = MagicMock(admin=True)
    monkeypatch.setattr("app.obtenerUsuarioPorDocumento", lambda doc, tip: usuario_mock)

    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    response = client.post("/visualizar_usuarios", data={
        "numero_documento": "999",
        "tipo_documento": "Cedula"
    }, follow_redirects=False)

    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert sess["admin_usuarios_status"] == "cannot_delete_admin"


def test_visualizar_usuarios_post_error_al_eliminar(client, monkeypatch):
    """Prueba unhappy: error inesperado al eliminar. Stub + Spy para contar llamadas."""
    class MockUser:
        admin = False
        nombre = "Usuario Normal"

    # Stub: usuario no admin
    monkeypatch.setattr("app.obtenerUsuarioPorDocumento", lambda doc, tip: MockUser())

    # Spy: registrar que se llamó a eliminarUsuario (aunque falle)
    call_args = []
    def spy_eliminarUsuario(doc, tip):
        call_args.append((doc, tip))
        raise Exception("Error de base de datos")
    monkeypatch.setattr("app.eliminarUsuario", spy_eliminarUsuario)

    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    response = client.post("/visualizar_usuarios", data={
        "numero_documento": "123",
        "tipo_documento": "Cedula"
    }, follow_redirects=False)

    assert response.status_code == 302
    assert "/visualizar_usuarios" in response.headers["Location"]

    with client.session_transaction() as sess:
        assert sess["admin_usuarios_status"] == "error"

    # Verificamos que el Spy registró la llamada a eliminarUsuario
    assert len(call_args) == 1
    assert call_args[0] == ("123", "Cedula")


def test_visualizar_usuarios_no_admin(client):
    """Prueba unhappy: usuario sin admin intenta acceder. Dummy."""
    # Dummy
    dummy = 0

    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": False}

    response = client.get("/visualizar_usuarios", follow_redirects=False)

    assert response.status_code == 302
    assert "/" in response.headers["Location"]
    assert dummy == 0