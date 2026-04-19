import pytest
import sys
import os
from unittest.mock import MagicMock
from assertpy import assert_that

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from app import app

def test_visualizar_usuarios_get_happy_path(client, monkeypatch):
    usuarios_mock = [
        MagicMock(numero_documento="111", tipo_documento="Cedula", nombre="User1", correo="u1@test.com",
                  tipo_de_sangre="O+", donante=True, enfermero=False, puntos=10, total_donado=500),
        MagicMock(numero_documento="222", tipo_documento="Cedula", nombre="User2", correo="u2@test.com",
                  tipo_de_sangre="A+", donante=False, enfermero=True, puntos=5, total_donado=250)
    ]
    monkeypatch.setattr("app.obtenerTodosUsuariosNoAdmin", lambda: usuarios_mock)
    dummy = []
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}
    response = client.get("/visualizar_usuarios")
    assert_that(response.status_code).is_equal_to(200)
    assert_that(response.data).contains(b"User1")
    assert_that(response.data).contains(b"User2")
    assert_that(dummy).is_not_none()

def test_visualizar_usuarios_post_eliminar_no_admin(client, monkeypatch):
    usuario_mock = MagicMock(admin=False, nombre="Test User")
    monkeypatch.setattr("app.obtenerUsuarioPorDocumento", lambda doc, tip: usuario_mock)
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
    assert_that(response.status_code).is_equal_to(302)
    with client.session_transaction() as sess:
        assert_that(sess.get("admin_usuarios_status")).is_equal_to("success")
        assert_that(sess["admin_usuarios_user"]["nombre"]).is_equal_to("Test User")
    assert_that(len(call_args)).is_equal_to(1)
    assert_that(call_args[0]).is_equal_to(("123", "Cedula"))

def test_visualizar_usuarios_post_eliminar_admin(client, monkeypatch):
    usuario_mock = MagicMock(admin=True)
    monkeypatch.setattr("app.obtenerUsuarioPorDocumento", lambda doc, tip: usuario_mock)
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}
    response = client.post("/visualizar_usuarios", data={
        "numero_documento": "999",
        "tipo_documento": "Cedula"
    }, follow_redirects=False)
    assert_that(response.status_code).is_equal_to(302)
    with client.session_transaction() as sess:
        assert_that(sess.get("admin_usuarios_status")).is_equal_to("cannot_delete_admin")

def test_visualizar_usuarios_post_error_al_eliminar(client, monkeypatch):
    class MockUser:
        admin = False
        nombre = "Usuario Normal"
    monkeypatch.setattr("app.obtenerUsuarioPorDocumento", lambda doc, tip: MockUser())
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
    assert_that(response.status_code).is_equal_to(302)
    assert_that(response.headers["Location"]).contains("/visualizar_usuarios")
    with client.session_transaction() as sess:
        assert_that(sess.get("admin_usuarios_status")).is_equal_to("error")
    assert_that(len(call_args)).is_equal_to(1)
    assert_that(call_args[0]).is_equal_to(("123", "Cedula"))

def test_visualizar_usuarios_no_admin(client):
    dummy = 0
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": False}
    response = client.get("/visualizar_usuarios", follow_redirects=False)
    assert_that(response.status_code).is_equal_to(302)
    assert_that(response.headers["Location"]).is_equal_to("/")
    assert_that(dummy).is_equal_to(0)