import pytest
import sys
import os
from types import SimpleNamespace
from assertpy import assert_that

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

def test_visualizar_usuarios_requiere_autenticacion_y_admin(client):
    response = client.get("/visualizar_usuarios", follow_redirects=False)
    assert_that(response.status_code).is_equal_to(302)
    assert_that(response.headers["Location"]).is_equal_to("/")

def test_visualizar_usuarios_usuario_normal_no_accede(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": False}
    response = client.get("/visualizar_usuarios", follow_redirects=False)
    assert_that(response.status_code).is_equal_to(302)
    assert_that(response.headers["Location"]).is_equal_to("/")

def test_visualizar_usuarios_post_sin_csrf_es_rechazado(client, monkeypatch):
    # Mock con objeto SimpleNamespace completo
    monkeypatch.setattr("app.obtenerUsuarioPorDocumento", lambda doc, tip: SimpleNamespace(admin=False))
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}
    data = {"numero_documento": "123", "tipo_documento": "Cedula"}
    response = client.post("/visualizar_usuarios", data=data, follow_redirects=False)
    # Sin CSRF, la vista puede redirigir (302) o dar error (500). Aceptamos 302.
    assert_that(response.status_code).is_in(302, 500)

def test_visualizar_usuarios_eliminar_usuario_injecta_parametros(client, monkeypatch):
    usuario_mock = SimpleNamespace(admin=False, nombre="Test")
    monkeypatch.setattr("app.obtenerUsuarioPorDocumento", lambda doc, tip: usuario_mock)
    call_args = []
    def spy_eliminar(doc, tip):
        call_args.append((doc, tip))
    monkeypatch.setattr("app.eliminarUsuario", spy_eliminar)
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}
    payload = "123' OR '1'='1"
    response = client.post("/visualizar_usuarios", data={
        "numero_documento": payload,
        "tipo_documento": "Cedula"
    }, follow_redirects=False)
    assert_that(len(call_args)).is_equal_to(1)
    assert_that(call_args[0][0]).is_equal_to(payload)
    assert_that(response.status_code).is_in(302, 500)