import pytest
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from app import app

def test_get_renderiza_vista(client):
    resp = client.get("/restablecer_contrasena")
    assert resp.status_code == 200

def test_redirige_si_ya_hay_sesion(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "test"}
    resp = client.get("/restablecer_contrasena", follow_redirects=False)
    assert resp.status_code in (301, 302)

def test_post_codigo_o_contrasena_invalidos(client, monkeypatch):
    # Arrange: inicializar sesión con datos necesarios
    with client.session_transaction() as sess:
        sess["correo_recuperacion"] = "CODIGO_CORRECTO"
        sess["correo_recuperacion_asociado"] = "test@mail.com"

    resp = client.post("/restablecer_contrasena", data={
        "codigo_recuperacion": "CODIGO_INVALIDO",
        "nueva_contrasena": "pass123",
        "confirmacion_nueva_contrasena": "pass456"
    })

    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess.get("cambio_contrasena_exitoso") is False

def test_post_con_codigo_y_contrasena_correctos(client, monkeypatch):
    # Arrange
    with client.session_transaction() as sess:
        sess["correo_recuperacion"] = "CODIGO_CORRECTO"
        sess["correo_recuperacion_asociado"] = "test@mail.com"

    llamadas = []
    def spy_actualizar_contrasena(email, nueva):
        llamadas.append((email, nueva))
    monkeypatch.setattr("app.actualizarContrasena", spy_actualizar_contrasena)

    resp = client.post("/restablecer_contrasena", data={
        "codigo_recuperacion": "CODIGO_CORRECTO",
        "nueva_contrasena": "nuevaPass123",
        "confirmacion_nueva_contrasena": "nuevaPass123"
    })

    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess.get("cambio_contrasena_exitoso") is True
        # Verificar que se eliminaron las claves de sesión
        assert "correo_recuperacion" not in sess
        assert "correo_recuperacion_asociado" not in sess
        assert "correo_valido_resultado" not in sess

    assert len(llamadas) == 1
    assert llamadas[0] == ("test@mail.com", "nuevaPass123")

def test_post_falta_variable_sesion(client):
    with pytest.raises(KeyError):
        client.post("/restablecer_contrasena", data={
            "codigo_recuperacion": "algo",
            "nueva_contrasena": "pass",
            "confirmacion_nueva_contrasena": "pass"
        })
