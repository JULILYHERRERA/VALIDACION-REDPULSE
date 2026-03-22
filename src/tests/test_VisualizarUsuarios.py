import pytest
import sys
import os
from unittest.mock import MagicMock

# Agregar src al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    with app.test_client() as client:
        yield client


def test_visualizar_usuarios_get_happy_path(client, monkeypatch):
    """Prueba GET exitosa: muestra lista de usuarios no admin"""
    # Arrange
    usuarios_mock = [
        MagicMock(numero_documento="111", tipo_documento="Cedula", nombre="User1", correo="u1@test.com",
                  tipo_de_sangre="O+", donante=True, enfermero=False, puntos=10, total_donado=500),
        MagicMock(numero_documento="222", tipo_documento="Cedula", nombre="User2", correo="u2@test.com",
                  tipo_de_sangre="A+", donante=False, enfermero=True, puntos=5, total_donado=250)
    ]
    monkeypatch.setattr("app.obtenerTodosUsuariosNoAdmin", lambda: usuarios_mock)

    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    # Act
    response = client.get("/visualizar_usuarios")

    # Assert
    assert response.status_code == 200
    assert b"User1" in response.data
    assert b"User2" in response.data


def test_visualizar_usuarios_post_eliminar_no_admin(client, monkeypatch):
    """Prueba POST exitosa: eliminar usuario no administrador"""
    # Arrange
    from app import obtenerUsuarioPorDocumento, eliminarUsuario

    usuario_mock = MagicMock(admin=False, nombre="Test User")
    monkeypatch.setattr("app.obtenerUsuarioPorDocumento", lambda doc, tip: usuario_mock)
    monkeypatch.setattr("app.eliminarUsuario", lambda doc, tip: None)

    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    # Act
    response = client.post("/visualizar_usuarios", data={
        "numero_documento": "123",
        "tipo_documento": "Cedula"
    }, follow_redirects=False)

    # Assert
    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert sess["admin_usuarios_status"] == "success"
        assert sess["admin_usuarios_user"]["nombre"] == "Test User"


def test_visualizar_usuarios_post_eliminar_admin(client, monkeypatch):
    """Prueba unhappy: intento de eliminar administrador"""
    # Arrange
    from app import obtenerUsuarioPorDocumento

    usuario_mock = MagicMock(admin=True)
    monkeypatch.setattr("app.obtenerUsuarioPorDocumento", lambda doc, tip: usuario_mock)

    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    # Act
    response = client.post("/visualizar_usuarios", data={
        "numero_documento": "999",
        "tipo_documento": "Cedula"
    }, follow_redirects=False)

    # Assert
    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert sess["admin_usuarios_status"] == "cannot_delete_admin"


def test_visualizar_usuarios_post_error_al_eliminar(client, monkeypatch):
    """Prueba unhappy: error inesperado al eliminar usuario (base de datos falla)"""
    # Arrange
    from app import obtenerUsuarioPorDocumento, eliminarUsuario

    # Simulamos un usuario NO administrador
    class MockUser:
        admin = False
        nombre = "Usuario Normal"

    monkeypatch.setattr("app.obtenerUsuarioPorDocumento", lambda doc, tip: MockUser())

    # Simulamos que eliminarUsuario lanza una excepción (error de BD)
    def mock_eliminar_falla(doc, tip):
        raise Exception("Error de base de datos")
    monkeypatch.setattr("app.eliminarUsuario", mock_eliminar_falla)

    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    # Act
    response = client.post("/visualizar_usuarios", data={
        "numero_documento": "123",
        "tipo_documento": "Cedula"
    }, follow_redirects=False)

    # Assert
    assert response.status_code == 302
    assert "/visualizar_usuarios" in response.headers["Location"]

    with client.session_transaction() as sess:
        assert sess["admin_usuarios_status"] == "error"


def test_visualizar_usuarios_no_admin(client):
    """Prueba unhappy: usuario sin admin intenta acceder"""
    # Arrange
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": False}

    # Act
    response = client.get("/visualizar_usuarios", follow_redirects=False)

    # Assert
    assert response.status_code == 302
    assert "/" in response.headers["Location"]