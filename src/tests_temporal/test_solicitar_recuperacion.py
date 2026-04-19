import pytest
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from app import app

def test_get_renderiza_vista(client):
    """Prueba GET: renderiza página. Uso de Dummy."""
    # Arrange
    dummy = None  # Dummy

    # Act
    resp = client.get("/solicitar_recuperacion")

    # Assert
    assert resp.status_code == 200
    assert dummy is None

def test_redirige_si_ya_hay_sesion(client):
    """Prueba: si hay sesión activa, redirige a home. Uso de Dummy."""
    # Arrange
    dummy = {}  # Dummy
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "test"}

    # Act
    resp = client.get("/solicitar_recuperacion", follow_redirects=False)

    # Assert
    assert resp.status_code in (301, 302)
    assert dummy is not None

def test_post_correo_no_registrado(client, monkeypatch):
    """POST con correo no registrado. Stub + Dummy."""
    # Arrange
    monkeypatch.setattr("app.verificarCorreo", lambda email: False)  # Stub
    dummy = "placeholder"  # Dummy

    # Act
    resp = client.post("/solicitar_recuperacion", data={"correo": "no@existe.com"})

    # Assert
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess["correo_valido_resultado"] is False
    assert dummy is not None

def test_post_correo_registrado_envia_codigo(client, monkeypatch):
    """POST con correo registrado. Stubs + Spy."""
    # Arrange
    monkeypatch.setattr("app.verificarCorreo", lambda email: True)  # Stub
    monkeypatch.setattr("app.obtenerCodigoRecuperacion", lambda email: "ABC123")  # Stub

    # Spy: registra llamada a Notificaciones.recuperar_contra_notificacion
    llamadas = {"count": 0, "args": None}
    def spy_enviar(self, email, codigo):          # self es la instancia de Notificaciones
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
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess["correo_valido_resultado"] is True
        assert sess["correo_recuperacion"] == "ABC123"
        assert sess["correo_recuperacion_asociado"] == correo
    assert llamadas["count"] == 1
    assert llamadas["args"] == (correo, "ABC123")

def test_post_correo_registrado_error_email(client, monkeypatch):
    """POST con correo registrado pero fallo al enviar email. Stub que lanza excepción."""
    # Arrange
    monkeypatch.setattr("app.verificarCorreo", lambda email: True)  # Stub
    monkeypatch.setattr("app.obtenerCodigoRecuperacion", lambda email: "ABC123")  # Stub

    def stub_error(self, email, codigo):
        raise Exception("Error de envío")

    monkeypatch.setattr(
        "servicios.notificaciones_servicio.Notificaciones.recuperar_contra_notificacion",
        stub_error
    )

    # Act & Assert
    with pytest.raises(Exception, match="Error de envío"):
        client.post("/solicitar_recuperacion", data={"correo": "si@existe.com"})