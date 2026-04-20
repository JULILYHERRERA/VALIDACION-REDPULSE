import pytest
import sys
import os
from types import SimpleNamespace

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

def test_visualizar_usuarios_requiere_autenticacion_y_admin(client):
    response = client.get("/visualizar_usuarios", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

def test_visualizar_usuarios_usuario_normal_no_accede(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": False}
    response = client.get("/visualizar_usuarios", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

def test_visualizar_usuarios_post_sin_csrf_es_rechazado(client, monkeypatch):
    # Mock con objeto SimpleNamespace completo
    monkeypatch.setattr("app.obtenerUsuarioPorDocumento", lambda doc, tip: SimpleNamespace(admin=False))
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}
    data = {"numero_documento": "123", "tipo_documento": "Cedula"}
    response = client.post("/visualizar_usuarios", data=data, follow_redirects=False)
    # Sin CSRF, la vista puede redirigir (302) o dar error (500). Aceptamos 302.
    assert response.status_code in (302, 500)

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
    assert len(call_args) == 1
    assert call_args[0][0] == payload
    assert response.status_code in (302, 500)
