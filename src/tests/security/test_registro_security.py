import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# SEGURIDAD 1 – Campos vacíos no rompen
# =====================================================
def test_seguridad_campos_vacios(client, monkeypatch):
    import app as modulo

    # ===================== ARRANGE =====================
    class UsuarioFake:
        nombre = ""
        apellido = ""
        contrasena = ""
        correo = ""
        numero_documento = ""
        tipo_documento = "CC"
        tipo_de_sangre = "O+"
        donante = False
        admin = False
        enfermero = False
        puntos = 0
        total_donado = 0
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


# =====================================================
# SEGURIDAD 2 – Inyección básica
# =====================================================
def test_seguridad_inyeccion_basica(client, monkeypatch):
    import app as modulo

    # ===================== ARRANGE =====================
    class UsuarioFake:
        nombre = "Ana"
        apellido = "Test"
        contrasena = "123"
        correo = "test@test.com"
        numero_documento = "111 OR 1=1"
        tipo_documento = "CC"
        tipo_de_sangre = "O+"
        donante = False
        admin = False
        enfermero = False
        puntos = 0
        total_donado = 0
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


# =====================================================
# SEGURIDAD 3 – Redirige si ya hay sesión
# =====================================================
def test_seguridad_redireccion_con_sesion(client):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Viejo"}

    # ======================= ACT =======================
    resp = client.post("/registro", data={}, follow_redirects=False)

    # ====================== ASSERT =====================
    assert resp.status_code in (301, 302)


# =====================================================
# SEGURIDAD 4 – Manejo de fallo de imagen
# =====================================================
def test_seguridad_imagen_none(client, monkeypatch):
    import app as modulo

    # ===================== ARRANGE =====================
    class UsuarioFake:
        nombre = "Ana"
        apellido = "Test"
        contrasena = "123"
        correo = "ana@mail.com"
        numero_documento = "111"
        tipo_documento = "CC"
        tipo_de_sangre = "O+"
        donante = False
        admin = False
        enfermero = False
        puntos = 0
        total_donado = 0
        perfil_imagen_link = None
        perfil_imagen_deletehash = None

    monkeypatch.setattr(modulo, "obtenerValoresUsuario", lambda req: UsuarioFake())
    monkeypatch.setattr(modulo, "verificarExistenciaUsuario", lambda d, t: False)
    monkeypatch.setattr(modulo, "verificarCorreo", lambda c: False)

    # Simula fallo de imagen (Imgur)
    monkeypatch.setattr(modulo, "generarUsuarioImagen", lambda i, h: (None, None))
    monkeypatch.setattr(modulo, "registrarUsuario", lambda *args: None)
    monkeypatch.setattr(modulo, "generarUsuarioSesion", lambda *args: {"nombre": "Ana"})

    # ======================= ACT =======================
    resp = client.post("/registro", data={})

    # ====================== ASSERT =====================
    assert resp.status_code == 200

    with client.session_transaction() as sess:
        assert sess.get("user_data") is not None


# =====================================================
# SEGURIDAD 5 – No crea sesión si usuario ya existe
# =====================================================
def test_seguridad_no_crea_sesion_si_existe(client, monkeypatch):
    import app as modulo

    # ===================== ARRANGE =====================
    class UsuarioFake:
        nombre = "Ana"
        apellido = "Test"
        contrasena = "123"
        correo = "ana@mail.com"
        numero_documento = "111"
        tipo_documento = "CC"
        tipo_de_sangre = "O+"
        donante = False
        admin = False
        enfermero = False
        puntos = 0
        total_donado = 0
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
        assert "user_data" not in sess