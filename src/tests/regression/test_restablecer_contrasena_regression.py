import pytest
import sys
import os
from assertpy import assert_that

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from app import app

def test_get_renderiza_vista(client):
    dummy = None
    resp = client.get("/restablecer_contrasena")
    assert_that(resp.status_code).is_equal_to(200)
    assert_that(dummy).is_none()

def test_redirige_si_ya_hay_sesion(client):
    dummy = []
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "test"}
    resp = client.get("/restablecer_contrasena", follow_redirects=False)
    assert_that(resp.status_code).is_in(301, 302)
    assert_that(dummy).is_not_none()

def test_post_codigo_o_contrasena_invalidos(client, monkeypatch):
    # Arrange: inicializar sesión con datos necesarios
    with client.session_transaction() as sess:
        sess["correo_recuperacion"] = "CODIGO_CORRECTO"
        sess["correo_recuperacion_asociado"] = "test@mail.com"
    dummy = "dummy"

    resp = client.post("/restablecer_contrasena", data={
        "codigo_recuperacion": "CODIGO_INVALIDO",
        "nueva_contrasena": "pass123",
        "confirmacion_nueva_contrasena": "pass456"
    })

    assert_that(resp.status_code).is_equal_to(200)
    with client.session_transaction() as sess:
        assert_that(sess.get("cambio_contrasena_exitoso")).is_false()
    assert_that(dummy).is_not_none()

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

    assert_that(resp.status_code).is_equal_to(200)
    with client.session_transaction() as sess:
        assert_that(sess.get("cambio_contrasena_exitoso")).is_true()
        # Verificar que se eliminaron las claves de sesión
        assert_that("correo_recuperacion" in sess).is_false()
        assert_that("correo_recuperacion_asociado" in sess).is_false()
        assert_that("correo_valido_resultado" in sess).is_false()

    assert_that(len(llamadas)).is_equal_to(1)
    assert_that(llamadas[0]).is_equal_to(("test@mail.com", "nuevaPass123"))

def test_post_falta_variable_sesion(client):
    dummy = object()
    with pytest.raises(KeyError):
        client.post("/restablecer_contrasena", data={
            "codigo_recuperacion": "algo",
            "nueva_contrasena": "pass",
            "confirmacion_nueva_contrasena": "pass"
        })
    assert_that(dummy).is_not_none()