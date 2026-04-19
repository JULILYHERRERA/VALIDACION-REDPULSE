import pytest
import sys
import os
from unittest.mock import MagicMock
from assertpy import assert_that

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from app import app

def test_convertir_enfermero_happy_path(client, monkeypatch):
    """Prueba exitosa. Stubs y Spy para actualizarEstadoEnfermero."""
    # Arrange
    monkeypatch.setattr("app.verificarExistenciaUsuario", lambda ced, tip: True)
    monkeypatch.setattr("app.obtenerUsuarioPorDocumento", lambda ced, tip: MagicMock(
        enfermero=False, nombre="Juan Perez", numero_documento="123", tipo_documento="Cedula"))

    call_args = []
    def spy_actualizarEstadoEnfermero(ced, tip, estado):
        call_args.append((ced, tip, estado))
    monkeypatch.setattr("app.actualizarEstadoEnfermero", spy_actualizarEstadoEnfermero)

    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True, "nombre": "Admin"}

    # Act
    response = client.post("/convertir_enfermero", data={
        "cedula": "123",
        "tipo_documento": "Cedula de Ciudadania"
    }, follow_redirects=False)

    # Assert
    assert_that(response.status_code).is_equal_to(302)
    assert_that(response.headers["Location"]).contains("/convertir_enfermero")

    with client.session_transaction() as sess:
        assert_that(sess["admin_conversion_status"]).is_equal_to("success")
        assert_that(sess["admin_conversion_user"]["nombre"]).is_equal_to("Juan Perez")

    assert_that(call_args).is_length(1)
    assert_that(call_args[0]).is_equal_to(("123", "Cedula de Ciudadania", True))

def test_convertir_enfermero_usuario_no_existe(client, monkeypatch):
    """Prueba unhappy: usuario no existe. Stub y Dummy."""
    # Arrange
    monkeypatch.setattr("app.verificarExistenciaUsuario", lambda ced, tip: False)
    dummy = "no usado"

    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    # Act
    response = client.post("/convertir_enfermero", data={
        "cedula": "999",
        "tipo_documento": "Cedula"
    }, follow_redirects=False)

    # Assert
    assert_that(response.status_code).is_equal_to(302)
    with client.session_transaction() as sess:
        assert_that(sess["admin_conversion_status"]).is_equal_to("not_found")
    assert_that(dummy).is_not_none()

def test_convertir_enfermero_ya_es_enfermero(client, monkeypatch):
    """Prueba unhappy: usuario ya es enfermero. Stub."""
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
    assert_that(response.status_code).is_equal_to(302)
    with client.session_transaction() as sess:
        assert_that(sess["admin_conversion_status"]).is_equal_to("already_nurse")

def test_convertir_enfermero_get_con_estado(client):
    """Prueba GET: renderiza template y limpia sesión. Uso de Dummy."""
    # Arrange
    dummy = None
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True, "nombre": "Admin"}
        sess["admin_conversion_status"] = "success"
        sess["admin_conversion_user"] = {"nombre": "Test", "documento": "123"}

    # Act
    response = client.get("/convertir_enfermero")

    # Assert
    assert_that(response.status_code).is_equal_to(200)
    with client.session_transaction() as sess:
        assert_that(sess).does_not_contain_key("admin_conversion_status")
        assert_that(sess).does_not_contain_key("admin_conversion_user")
    assert_that(dummy).is_none()

def test_convertir_enfermero_no_admin(client):
    """Prueba unhappy: usuario no administrador -> redirige a home. Dummy."""
    # Arrange
    dummy = {}
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": False, "nombre": "Usuario"}

    # Act
    response = client.get("/convertir_enfermero", follow_redirects=False)

    # Assert
    assert_that(response.status_code).is_equal_to(302)
    assert_that(response.headers["Location"]).is_equal_to("/")
    assert_that(dummy).is_not_none()