import pytest
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from app import app

def test_get_renderiza_vista(client):
    """GET: renderiza página. Uso de Dummy."""
    # Arrange
    dummy = None  # Dummy

    # Act
    resp = client.get("/restablecer_contrasena")

    # Assert
    assert resp.status_code == 200
    assert dummy is None

def test_redirige_si_ya_hay_sesion(client):
    """Si hay sesión activa, redirige a home. Uso de Dummy."""
    # Arrange
    dummy = []  # Dummy
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "test"}

    # Act
    resp = client.get("/restablecer_contrasena", follow_redirects=False)

    # Assert
    assert resp.status_code in (301, 302)
    assert dummy is not None

def test_post_codigo_o_contrasena_invalidos(client, monkeypatch):
    """POST con código incorrecto o contraseñas no coincidentes. Stub + Dummy."""
    # Arrange
    with client.session_transaction() as sess:
        sess["correo_recuperacion"] = "CODIGO_CORRECTO"
        sess["correo_recuperacion_asociado"] = "test@mail.com"
    dummy = "dummy"  # Dummy

    # Act
    resp = client.post("/restablecer_contrasena", data={
        "codigo_recuperacion": "CODIGO_INVALIDO",
        "nueva_contrasena": "pass123",
        "confirmacion_nueva_contrasena": "pass456"
    })

    # Assert
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess["cambio_contrasena_exitoso"] is False
    assert dummy is not None

def test_post_con_codigo_y_contrasena_correctos(client, monkeypatch):
    """POST válido: actualiza contraseña y limpia sesión. Stubs + Spy."""
    # Arrange
    with client.session_transaction() as sess:
        sess["correo_recuperacion"] = "CODIGO_CORRECTO"
        sess["correo_recuperacion_asociado"] = "test@mail.com"

    # Stub: actualizarContrasena no hace nada
    def stub_actualizar_contrasena(email, nueva):
        pass
    monkeypatch.setattr("app.actualizarContrasena", stub_actualizar_contrasena)

    # Spy: registrar llamada a actualizarContrasena
    llamadas = []
    def spy_actualizar_contrasena(email, nueva):
        llamadas.append((email, nueva))
    monkeypatch.setattr("app.actualizarContrasena", spy_actualizar_contrasena)

    # Act
    resp = client.post("/restablecer_contrasena", data={
        "codigo_recuperacion": "CODIGO_CORRECTO",
        "nueva_contrasena": "nuevaPass123",
        "confirmacion_nueva_contrasena": "nuevaPass123"
    })

    # Assert
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess["cambio_contrasena_exitoso"] is True
        assert "correo_recuperacion" not in sess
        assert "correo_recuperacion_asociado" not in sess
        assert "correo_valido_resultado" not in sess
    assert len(llamadas) == 1
    assert llamadas[0] == ("test@mail.com", "nuevaPass123")

def test_post_falta_variable_sesion(client):
    """POST sin la variable de sesión 'correo_recuperacion'. Dummy (la variable falta, se espera KeyError)."""
    # Arrange
    dummy = object()  # Dummy
    # No se establece 'correo_recuperacion' en sesión

    # Act & Assert
    with pytest.raises(KeyError):
        client.post("/restablecer_contrasena", data={
            "codigo_recuperacion": "algo",
            "nueva_contrasena": "pass",
            "confirmacion_nueva_contrasena": "pass"
        })
    assert dummy is not None