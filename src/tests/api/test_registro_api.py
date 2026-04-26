import pytest
import sys
import os
from app import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# API 1 – POST responde correctamente (flujo exitoso)
# =====================================================
def test_api_post_responde_ok(client, monkeypatch):
    import app as modulo

    # ===================== ARRANGE =====================
    class UsuarioFake:
        nombre = "Ana"
        contrasena = "123"
        correo = "ana@mail.com"
        numero_documento = "111"
        tipo_documento = "CC"
        donante = False
        admin = False
        enfermero = False
        puntos = 0
        total_donado = 0
        tipo_de_sangre = "O+"
        perfil_imagen_link = None
        perfil_imagen_deletehash = None

    monkeypatch.setattr(modulo, "obtenerValoresUsuario", lambda req: UsuarioFake())
    monkeypatch.setattr(modulo, "verificarExistenciaUsuario", lambda d, t: False)
    monkeypatch.setattr(modulo, "verificarCorreo", lambda c: False)
    monkeypatch.setattr(modulo, "generarUsuarioImagen", lambda i, h: ("link", "hash"))
    monkeypatch.setattr(modulo, "registrarUsuario", lambda *args: None)
    monkeypatch.setattr(modulo, "generarUsuarioSesion", lambda *args: {"nombre": "Ana"})

    # ======================= ACT =======================
    resp = client.post("/registro", data={})

    # ====================== ASSERT =====================
    assert resp.status_code == 200
    assert b"registro" in resp.data.lower()


# =====================================================
# API 2 – GET responde correctamente (sin sesión)
# =====================================================
def test_api_get_registro(client):

    # ===================== ARRANGE =====================
    # No sesión activa

    # ======================= ACT =======================

    resp = client.get("/registro")

    # ====================== ASSERT =====================
    assert resp.status_code == 200


# =====================================================
# API 3 – Redirección si hay sesión activa
# =====================================================
def test_api_redireccion_con_sesion(client):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana"}

    # ======================= ACT =======================
    resp = client.get("/registro", follow_redirects=False)

    # ====================== ASSERT =====================
    assert resp.status_code in (301, 302)
    assert resp.headers.get("Location") is not None


# =====================================================
# API 4 – POST cuando usuario ya existe
# =====================================================
def test_api_post_usuario_existente(client, monkeypatch):
    import app as modulo

    # ===================== ARRANGE =====================
    class UsuarioFake:
        nombre = "Ana"
        contrasena = "123"
        correo = "ana@mail.com"
        numero_documento = "111"
        tipo_documento = "CC"
        donante = False
        admin = False
        enfermero = False
        puntos = 0
        total_donado = 0
        tipo_de_sangre = "O+"
        perfil_imagen_link = None
        perfil_imagen_deletehash = None

    monkeypatch.setattr(modulo, "obtenerValoresUsuario", lambda req: UsuarioFake())
    monkeypatch.setattr(modulo, "verificarExistenciaUsuario", lambda d, t: True)
    monkeypatch.setattr(modulo, "verificarCorreo", lambda c: False)

    # ======================= ACT =======================
    resp = client.post("/registro", data={})

    # ====================== ASSERT =====================
    assert resp.status_code == 200

    with client.session_transaction() as sess:
        assert sess.get("registarse_verificacion_resultado") is True


# =====================================================
# API 5 – POST cuando correo ya existe
# =====================================================
def test_api_post_correo_existente(client, monkeypatch):
    import app as modulo

    # ===================== ARRANGE =====================
    class UsuarioFake:
        nombre = "Ana"
        contrasena = "123"
        correo = "ana@mail.com"
        numero_documento = "111"
        tipo_documento = "CC"
        donante = False
        admin = False
        enfermero = False
        puntos = 0
        total_donado = 0
        tipo_de_sangre = "O+"
        perfil_imagen_link = None
        perfil_imagen_deletehash = None

    monkeypatch.setattr(modulo, "obtenerValoresUsuario", lambda req: UsuarioFake())
    monkeypatch.setattr(modulo, "verificarExistenciaUsuario", lambda d, t: False)
    monkeypatch.setattr(modulo, "verificarCorreo", lambda c: True)

    # ======================= ACT =======================
    resp = client.post("/registro", data={})

    # ====================== ASSERT =====================
    assert resp.status_code == 200

    with client.session_transaction() as sess:
        assert sess.get("correo_ya_existe") is True


# =====================================================
# API 6 – POST crea sesión correctamente
# =====================================================
def test_api_post_crea_sesion(client, monkeypatch):
    import app as modulo

    # ===================== ARRANGE =====================
    class UsuarioFake:
        nombre = "Ana"
        contrasena = "123"
        correo = "ana@mail.com"
        numero_documento = "111"
        tipo_documento = "CC"
        donante = False
        admin = False
        enfermero = False
        puntos = 0
        total_donado = 0
        tipo_de_sangre = "O+"
        perfil_imagen_link = None
        perfil_imagen_deletehash = None

    monkeypatch.setattr(modulo, "obtenerValoresUsuario", lambda req: UsuarioFake())
    monkeypatch.setattr(modulo, "verificarExistenciaUsuario", lambda d, t: False)
    monkeypatch.setattr(modulo, "verificarCorreo", lambda c: False)
    monkeypatch.setattr(modulo, "generarUsuarioImagen", lambda i, h: ("link", "hash"))
    monkeypatch.setattr(modulo, "registrarUsuario", lambda *args: None)
    monkeypatch.setattr(modulo, "generarUsuarioSesion", lambda *args: {"nombre": "Ana", "doc": "111"})

    # ======================= ACT =======================
    resp = client.post("/registro", data={})

    # ====================== ASSERT =====================
    assert resp.status_code == 200

    with client.session_transaction() as sess:
        assert sess.get("user_data") == {"nombre": "Ana", "doc": "111"}