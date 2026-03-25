

import pytest
import sys
import os

# agrega la carpeta src al path (igual que tu ejemplo)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

# -----------------------------
# PRUEBA 1 (Camino 1):
# Si ya hay sesión -> redirige a home
# Secuencia: 1-2-3-15
# -----------------------------
def test_login_redirige_si_ya_hay_sesion(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "test"}

    resp = client.get("/login", follow_redirects=False)
    assert resp.status_code in (301, 302)

    assert "/" in resp.headers.get("Location", "")

# -----------------------------
# PRUEBA 2 (Camino 2):
# Si existe indicador cambio contraseña -> lo limpia (None) y renderiza login
# Secuencia: 1-2-4-5-6-14-15 (GET)
# -----------------------------
def test_login_get_limpia_indicador_cambio_contrasena(client):
    with client.session_transaction() as sess:
        sess["cambio_contrasena_exitoso"] = True

    resp = client.get("/login")
    assert resp.status_code == 200

    with client.session_transaction() as sess:
        assert "cambio_contrasena_exitoso" in sess
        assert sess["cambio_contrasena_exitoso"] is None

# -----------------------------
# PRUEBA 3 (Camino 3):
# GET normal sin sesión -> renderiza login
# Secuencia: 1-2-4-6-14-15
# -----------------------------
def test_login_get_renderiza_vista(client):
    resp = client.get("/login")
    assert resp.status_code == 200

# -----------------------------
# PRUEBA 4 (Camino 4):
# POST credenciales inválidas -> guarda login_verificacion_resultado=False
# Secuencia: 1-2-4-6-7-8-9-10-14-15
# -----------------------------
def test_login_post_credenciales_invalidas(client, monkeypatch):
    import app as modulo

    # verificacionLogin devuelve False
    monkeypatch.setattr(modulo, "verificacionLogin", lambda doc, tipo, contra: False)

    # si es inválido NO debe intentar consultar usuario ni generar sesión
    llamadas = {"obtener": 0, "generar": 0}

    def mock_obtener(doc, tipo):
        llamadas["obtener"] += 1

    def mock_generar(*args, **kwargs):
        llamadas["generar"] += 1

    monkeypatch.setattr(modulo, "obtenerUsuarioPorDocumento", mock_obtener)
    monkeypatch.setattr(modulo, "generarUsuarioSesion", mock_generar)

    resp = client.post("/login", data={
        "numero_documento": "123",
        "tipo_documento": "Cedula de Ciudadania",
        "contrasena": "mala"
    })

    assert resp.status_code == 200

    with client.session_transaction() as sess:
        assert sess["login_verificacion_resultado"] is False
        assert "user_data" not in sess

    assert llamadas["obtener"] == 0
    assert llamadas["generar"] == 0

# -----------------------------
# PRUEBA 5 (Camino 5):
# POST credenciales válidas -> guarda login_verificacion_resultado=True y user_data
# Secuencia: 1-2-4-6-7-8-9-10-11-12-13-14-15
# -----------------------------
def test_login_post_credenciales_validas_guarda_user_data(client, monkeypatch):
    import app as modulo

    # verificacionLogin devuelve True
    monkeypatch.setattr(modulo, "verificacionLogin", lambda doc, tipo, contra: True)

    # usuario fake (con los atributos que tu código usa)
    class UsuarioFake:
        nombre = "Ana"
        contrasena = "hash"
        correo = "ana@mail.com"
        numero_documento = "123"
        donante = True
        admin = False
        enfermero = False
        puntos = 0
        total_donado = 0
        tipo_de_sangre = "O+"
        tipo_documento = "Cedula de Ciudadania"
        perfil_imagen_link = None
        perfil_imagen_deletehash = None

    # mock obtenerUsuarioPorDocumento
    monkeypatch.setattr(modulo, "obtenerUsuarioPorDocumento", lambda doc, tipo: UsuarioFake())

    # mock generarUsuarioSesion (lo que quede guardado en session['user_data'])
    monkeypatch.setattr(modulo, "generarUsuarioSesion", lambda *args: {"nombre": "Ana", "numero_documento": "123"})

    resp = client.post("/login", data={
        "numero_documento": "123",
        "tipo_documento": "Cedula de Ciudadania",
        "contrasena": "ok"
    })

    assert resp.status_code == 200

    with client.session_transaction() as sess:
        assert sess["login_verificacion_resultado"] is True
        assert sess["user_data"] == {"nombre": "Ana", "numero_documento": "123"}