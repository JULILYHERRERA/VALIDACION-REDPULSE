import time
import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# PERFORMANCE 1 – Carga de la página de Login
# =====================================================
def test_performance_login_renderizado(client):
    """Verifica que la página de login carga rápidamente 10 veces."""
    start = time.time()
    for _ in range(10):
        client.get("/login")
    end = time.time()
    
    assert (end - start) < 1.0  # Menos de 1 segundo para 10 cargas

# =====================================================
# PERFORMANCE 2 – Procesamiento de Login POST
# =====================================================
def test_performance_login_post(client, monkeypatch):
    """Verifica que el procesamiento de login (mocked) es rápido."""
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
    monkeypatch.setattr(modulo, "generarUsuarioSesion", lambda *args: {"nombre": "Juan"})

    start = time.time()
    for _ in range(10):
        client.post("/login", data={
            "numero_documento": "123456",
            "tipo_documento": "Cedula de Ciudadania",
            "contrasena": "password123"
        })
    end = time.time()
    
    assert (end - start) < 1.0  # Menos de 1 segundo para 10 logins
