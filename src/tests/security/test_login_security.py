import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# SEGURIDAD 1 – Campos vacíos en Login
# =====================================================
def test_security_login_campos_vacios(client, monkeypatch):
    """Verifica que el login con campos vacíos se maneje sin errores."""
    import app as modulo

    # Simulamos que el controlador devuelve False para campos vacíos
    monkeypatch.setattr(modulo, "verificacionLogin", lambda doc, tipo, contra: False)

    resp = client.post("/login", data={
        "numero_documento": "",
        "tipo_documento": "",
        "contrasena": ""
    })

    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess.get("login_verificacion_resultado") is False

# =====================================================
# SEGURIDAD 2 – Intento de inyección SQL en campos de Login
# =====================================================
def test_security_login_inyeccion_sql_simulada(client, monkeypatch):
    """Verifica que intentos de inyección SQL se manejen correctamente (vía mocks)."""
    import app as modulo

    # Simulamos que el controlador detecta o simplemente no encuentra el usuario
    monkeypatch.setattr(modulo, "verificacionLogin", lambda doc, tipo, contra: False)

    resp = client.post("/login", data={
        "numero_documento": "111 OR 1=1",
        "tipo_documento": "Cedula de Ciudadania",
        "contrasena": "' OR '1'='1"
    })

    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess.get("login_verificacion_resultado") is False

# =====================================================
# SEGURIDAD 3 – Persistencia de sesión (No redirección si no hay sesión)
# =====================================================
def test_security_login_acceso_anonimo(client):
    """Verifica que el acceso a la página de login es público."""
    resp = client.get("/login")
    assert resp.status_code == 200

# =====================================================
# SEGURIDAD 4 – Redirección si ya hay sesión
# =====================================================
def test_security_login_redireccion_con_sesion(client):
    """Verifica que un usuario ya autenticado no pueda volver a loguearse."""
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Autenticado"}

    resp = client.post("/login", data={}, follow_redirects=False)
    assert resp.status_code in (301, 302)
