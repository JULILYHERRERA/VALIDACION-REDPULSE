import pytest
import sys
import os
from unittest.mock import MagicMock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from app import app

# =====================================================
# REGRESSION 1 – Limpieza de flag de cambio de contraseña
# =====================================================
def test_regression_login_limpia_flags(client):
    """Verifica que al cargar el login se limpia el indicador de cambio de contraseña."""
    with client.session_transaction() as sess:
        sess["cambio_contrasena_exitoso"] = True

    client.get("/login")

    with client.session_transaction() as sess:
        assert sess.get("cambio_contrasena_exitoso") is None

# =====================================================
# REGRESSION 2 – Flujo completo Donante
# =====================================================
def test_regression_login_flujo_completo_donante(client, monkeypatch):
    """Verifica el flujo completo de login para un donante."""
    import app as modulo

    class UsuarioFake:
        nombre = "Donante Test"
        contrasena = "hash"
        correo = "donante@test.com"
        numero_documento = "111"
        donante = True
        admin = False
        enfermero = False
        puntos = 10
        total_donado = 500
        tipo_de_sangre = "O+"
        tipo_documento = "Cedula de Ciudadania"
        perfil_imagen_link = "https://link.com"
        perfil_imagen_deletehash = "hash123"

    monkeypatch.setattr(modulo, "verificacionLogin", lambda doc, tipo, contra: True)
    monkeypatch.setattr(modulo, "obtenerUsuarioPorDocumento", lambda doc, tipo: UsuarioFake())
    
    # Mock de generarUsuarioSesion con todos los campos
    def mock_generar_sesion(*args):
        return {
            "nombre": args[0],
            "numero_documento": args[4],
            "donante": args[5],
            "admin": args[6],
            "enfermero": args[7]
        }
    monkeypatch.setattr(modulo, "generarUsuarioSesion", mock_generar_sesion)

    response = client.post("/login", data={
        "numero_documento": "111",
        "tipo_documento": "Cedula de Ciudadania",
        "contrasena": "pass"
    })

    assert response.status_code == 200
    with client.session_transaction() as sess:
        user_data = sess.get("user_data")
        assert user_data["nombre"] == "Donante Test"
        assert user_data["donante"] is True
        assert user_data["admin"] is False

# =====================================================
# REGRESSION 3 – Flujo completo Admin
# =====================================================
def test_regression_login_flujo_completo_admin(client, monkeypatch):
    """Verifica el flujo completo de login para un administrador."""
    import app as modulo

    class UsuarioFake:
        nombre = "Admin Test"
        contrasena = "hash"
        correo = "admin@test.com"
        numero_documento = "999"
        donante = False
        admin = True
        enfermero = False
        puntos = 0
        total_donado = 0
        tipo_de_sangre = "A+"
        tipo_documento = "Cedula de Ciudadania"
        perfil_imagen_link = None
        perfil_imagen_deletehash = None

    monkeypatch.setattr(modulo, "verificacionLogin", lambda doc, tipo, contra: True)
    monkeypatch.setattr(modulo, "obtenerUsuarioPorDocumento", lambda doc, tipo: UsuarioFake())
    
    def mock_generar_sesion(*args):
        return {
            "nombre": args[0],
            "admin": args[6]
        }
    monkeypatch.setattr(modulo, "generarUsuarioSesion", mock_generar_sesion)

    response = client.post("/login", data={
        "numero_documento": "999",
        "tipo_documento": "Cedula de Ciudadania",
        "contrasena": "admin_pass"
    })

    assert response.status_code == 200
    with client.session_transaction() as sess:
        user_data = sess.get("user_data")
        assert user_data["nombre"] == "Admin Test"
        assert user_data["admin"] is True

