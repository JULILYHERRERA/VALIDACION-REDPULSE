import pytest
import sys
import os
from app import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# API 1 – GET Login responde correctamente
# =====================================================
def test_api_login_get(client):
    """Verifica que la página de login carga correctamente."""
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b"login" in resp.data.lower()

# =====================================================
# API 2 – POST Login exitoso
# =====================================================
def test_api_login_post_exitoso(client, monkeypatch):
    """Verifica que un login con credenciales válidas crea la sesión."""
    import app as modulo

    class UsuarioFake:
        nombre = "Juan"
        contrasena = "hash"
        correo = "juan@test.com"
        numero_documento = "123456"
        donante = True
        admin = False
        enfermero = False
        puntos = 10
        total_donado = 500
        tipo_de_sangre = "O+"
        tipo_documento = "Cedula de Ciudadania"
        perfil_imagen_link = None
        perfil_imagen_deletehash = None

    monkeypatch.setattr(modulo, "verificacionLogin", lambda doc, tipo, contra: True)
    monkeypatch.setattr(modulo, "obtenerUsuarioPorDocumento", lambda doc, tipo: UsuarioFake())
    monkeypatch.setattr(modulo, "generarUsuarioSesion", lambda *args: {"nombre": "Juan", "doc": "123456"})

    resp = client.post("/login", data={
        "numero_documento": "123456",
        "tipo_documento": "Cedula de Ciudadania",
        "contrasena": "password123"
    })

    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess.get("login_verificacion_resultado") is True
        assert sess.get("user_data") == {"nombre": "Juan", "doc": "123456"}

# =====================================================
# API 3 – POST Login fallido
# =====================================================
def test_api_login_post_fallido(client, monkeypatch):
    """Verifica que un login con credenciales inválidas marca el error en sesión."""
    import app as modulo

    monkeypatch.setattr(modulo, "verificacionLogin", lambda doc, tipo, contra: False)

    resp = client.post("/login", data={
        "numero_documento": "123456",
        "tipo_documento": "Cedula de Ciudadania",
        "contrasena": "wrong_password"
    })

    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess.get("login_verificacion_resultado") is False
        assert "user_data" not in sess

# =====================================================
# API 4 – Redirección si ya hay sesión
# =====================================================
def test_api_login_redireccion_si_sesion(client):
    """Verifica que si ya hay sesión, redirige al home."""
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Juan"}

    resp = client.get("/login", follow_redirects=False)
    assert resp.status_code in (301, 302)
    assert resp.headers.get("Location") in ("/", "http://localhost/")
