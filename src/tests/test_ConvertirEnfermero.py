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


def test_convertir_enfermero_happy_path(client, monkeypatch):
    """Prueba exitosa: usuario admin convierte a otro usuario a enfermero"""
    # Arrange
    monkeypatch.setattr("app.verificarExistenciaUsuario", lambda ced, tip: True)
    monkeypatch.setattr("app.obtenerUsuarioPorDocumento", lambda ced, tip: MagicMock(
        enfermero=False, nombre="Juan Perez", numero_documento="123", tipo_documento="Cedula"))
    monkeypatch.setattr("app.actualizarEstadoEnfermero", lambda ced, tip, estado: None)

    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True, "nombre": "Admin"}

    # Act
    response = client.post("/convertir_enfermero", data={
        "cedula": "123",
        "tipo_documento": "Cedula de Ciudadania"
    }, follow_redirects=False)

    # Assert
    assert response.status_code == 302
    assert "/convertir_enfermero" in response.headers["Location"]

    with client.session_transaction() as sess:
        assert sess["admin_conversion_status"] == "success"
        assert sess["admin_conversion_user"]["nombre"] == "Juan Perez"


def test_convertir_enfermero_usuario_no_existe(client, monkeypatch):
    """Prueba unhappy: usuario no existe"""
    # Arrange
    monkeypatch.setattr("app.verificarExistenciaUsuario", lambda ced, tip: False)

    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    # Act
    response = client.post("/convertir_enfermero", data={
        "cedula": "999",
        "tipo_documento": "Cedula"
    }, follow_redirects=False)

    # Assert
    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert sess["admin_conversion_status"] == "not_found"


def test_convertir_enfermero_ya_es_enfermero(client, monkeypatch):
    """Prueba unhappy: el usuario ya es enfermero"""
    # Arrange
    monkeypatch.setattr("app.verificarExistenciaUsuario", lambda ced, tip: True)
    monkeypatch.setattr("app.obtenerUsuarioPorDocumento", lambda ced, tip: MagicMock(
        enfermero=True, nombre="Maria", numero_documento="456", tipo_documento="Cedula"))

    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    # Act
    response = client.post("/convertir_enfermero", data={
        "cedula": "456",
        "tipo_documento": "Cedula"
    }, follow_redirects=False)

    # Assert
    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert sess["admin_conversion_status"] == "already_nurse"


def test_convertir_enfermero_get_con_estado(client):
    """Prueba GET: renderiza template y limpia sesión"""
    # Arrange
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True, "nombre": "Admin"}
        sess["admin_conversion_status"] = "success"
        sess["admin_conversion_user"] = {"nombre": "Test", "documento": "123"}

    # Act
    response = client.get("/convertir_enfermero")

    # Assert
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert "admin_conversion_status" not in sess
        assert "admin_conversion_user" not in sess


def test_convertir_enfermero_no_admin(client):
    """Prueba unhappy: usuario no administrador -> redirige a home"""
    # Arrange
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": False, "nombre": "Usuario"}

    # Act
    response = client.get("/convertir_enfermero", follow_redirects=False)

    # Assert
    assert response.status_code == 302
    assert "/" in response.headers["Location"]