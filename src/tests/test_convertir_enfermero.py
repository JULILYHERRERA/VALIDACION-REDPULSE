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


def test_convertir_enfermero_happy_path(client, monkeypatch):
    """Prueba exitosa. Stubs y Spy para actualizarEstadoEnfermero."""
    # Stubs
    monkeypatch.setattr("app.verificarExistenciaUsuario", lambda ced, tip: True)
    monkeypatch.setattr("app.obtenerUsuarioPorDocumento", lambda ced, tip: MagicMock(
        enfermero=False, nombre="Juan Perez", numero_documento="123", tipo_documento="Cedula"))

    # Spy: registrar llamada a actualizarEstadoEnfermero
    call_args = []
    def spy_actualizarEstadoEnfermero(ced, tip, estado):
        call_args.append((ced, tip, estado))
    monkeypatch.setattr("app.actualizarEstadoEnfermero", spy_actualizarEstadoEnfermero)

    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True, "nombre": "Admin"}

    response = client.post("/convertir_enfermero", data={
        "cedula": "123",
        "tipo_documento": "Cedula de Ciudadania"
    }, follow_redirects=False)

    assert response.status_code == 302
    assert "/convertir_enfermero" in response.headers["Location"]

    with client.session_transaction() as sess:
        assert sess["admin_conversion_status"] == "success"
        assert sess["admin_conversion_user"]["nombre"] == "Juan Perez"

    # Verificar que el Spy registró la llamada
    assert len(call_args) == 1
    assert call_args[0] == ("123", "Cedula de Ciudadania", True)


def test_convertir_enfermero_usuario_no_existe(client, monkeypatch):
    """Prueba unhappy: usuario no existe. Stub y Dummy."""
    # Stub
    monkeypatch.setattr("app.verificarExistenciaUsuario", lambda ced, tip: False)
    # Dummy
    dummy = "no usado"

    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    response = client.post("/convertir_enfermero", data={
        "cedula": "999",
        "tipo_documento": "Cedula"
    }, follow_redirects=False)

    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert sess["admin_conversion_status"] == "not_found"
    assert dummy is not None


def test_convertir_enfermero_ya_es_enfermero(client, monkeypatch):
    """Prueba unhappy: usuario ya es enfermero. Stub."""
    monkeypatch.setattr("app.verificarExistenciaUsuario", lambda ced, tip: True)
    monkeypatch.setattr("app.obtenerUsuarioPorDocumento", lambda ced, tip: MagicMock(
        enfermero=True, nombre="Maria", numero_documento="456", tipo_documento="Cedula"))

    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    response = client.post("/convertir_enfermero", data={
        "cedula": "456",
        "tipo_documento": "Cedula"
    }, follow_redirects=False)

    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert sess["admin_conversion_status"] == "already_nurse"


def test_convertir_enfermero_get_con_estado(client):
    """Prueba GET: renderiza template y limpia sesión. Uso de Dummy."""
    # Dummy
    dummy = None

    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True, "nombre": "Admin"}
        sess["admin_conversion_status"] = "success"
        sess["admin_conversion_user"] = {"nombre": "Test", "documento": "123"}

    response = client.get("/convertir_enfermero")

    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert "admin_conversion_status" not in sess
        assert "admin_conversion_user" not in sess
    assert dummy is None  # dummy no usado


def test_convertir_enfermero_no_admin(client):
    """Prueba unhappy: usuario no administrador -> redirige a home. Dummy."""
    # Dummy
    dummy = {}

    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": False, "nombre": "Usuario"}

    response = client.get("/convertir_enfermero", follow_redirects=False)

    assert response.status_code == 302
    assert "/" in response.headers["Location"]
    assert dummy is not None