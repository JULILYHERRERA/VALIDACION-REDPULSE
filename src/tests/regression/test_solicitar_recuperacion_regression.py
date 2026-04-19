import pytest
import sys
import os
from assertpy import assert_that

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from app import app

def test_get_renderiza_vista(client):
    """Prueba GET: renderiza página. Uso de Dummy."""
    # Arrange
    dummy = None

    # Act
    resp = client.get("/solicitar_recuperacion")

    # Assert (Fluent)
    assert_that(resp.status_code).is_equal_to(200)
    assert_that(dummy).is_none()

def test_redirige_si_ya_hay_sesion(client):
    """Prueba: si hay sesión activa, redirige a home."""
    # Arrange
    dummy = {}
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "test"}

    # Act
    resp = client.get("/solicitar_recuperacion", follow_redirects=False)

    # Assert
    assert_that(resp.status_code).is_in(301, 302)
    assert_that(dummy).is_not_none()

def test_post_correo_no_registrado(client, monkeypatch):
    """POST con correo no registrado. Stub + Dummy."""
    # Arrange
    monkeypatch.setattr("app.verificarCorreo", lambda email: False)
    dummy = "placeholder"

    # Act
    resp = client.post("/solicitar_recuperacion", data={"correo": "no@existe.com"})

    # Assert
    assert_that(resp.status_code).is_equal_to(200)
    with client.session_transaction() as sess:
        assert_that(sess["correo_valido_resultado"]).is_false()
    assert_that(dummy).is_not_none()

def test_post_correo_registrado_envia_codigo(client, monkeypatch):
    """POST con correo registrado. Stubs + Spy."""
    # Arrange
    monkeypatch.setattr("app.verificarCorreo", lambda email: True)
    monkeypatch.setattr("app.obtenerCodigoRecuperacion", lambda email: "ABC123")

    llamadas = {"count": 0, "args": None}
    def spy_enviar(self, email, codigo):
        llamadas["count"] += 1
        llamadas["args"] = (email, codigo)

    monkeypatch.setattr(
        "servicios.notificaciones_servicio.Notificaciones.recuperar_contra_notificacion",
        spy_enviar
    )

    correo = "si@existe.com"

    # Act
    resp = client.post("/solicitar_recuperacion", data={"correo": correo})

    # Assert
    assert_that(resp.status_code).is_equal_to(200)
    with client.session_transaction() as sess:
        assert_that(sess["correo_valido_resultado"]).is_true()
        assert_that(sess["correo_recuperacion"]).is_equal_to("ABC123")
        assert_that(sess["correo_recuperacion_asociado"]).is_equal_to(correo)
    assert_that(llamadas["count"]).is_equal_to(1)
    assert_that(llamadas["args"]).is_equal_to((correo, "ABC123"))

def test_post_correo_registrado_error_email(client, monkeypatch):
    """POST con correo registrado pero fallo al enviar email."""
    # Arrange
    monkeypatch.setattr("app.verificarCorreo", lambda email: True)
    monkeypatch.setattr("app.obtenerCodigoRecuperacion", lambda email: "ABC123")

    def stub_error(self, email, codigo):
        raise Exception("Error de envío")

    monkeypatch.setattr(
        "servicios.notificaciones_servicio.Notificaciones.recuperar_contra_notificacion",
        stub_error
    )

    # Act & Assert
    with pytest.raises(Exception, match="Error de envío"):
        client.post("/solicitar_recuperacion", data={"correo": "si@existe.com"})