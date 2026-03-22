import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    with app.test_client() as client:
        yield client


# =====================================================
# PRUEBA 1 – Camino 1

def test_prueba1_redirige_si_ya_hay_sesion(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "test"}

    resp = client.get("/registro", follow_redirects=False)

    assert resp.status_code in (301, 302)
    assert resp.headers.get("Location") is not None


# =====================================================
# PRUEBA 2 – Camino 2
# GET sin sesión previa pero con posible limpieza de errores

def test_prueba2_get_renderiza_registro(client):
    with client.session_transaction() as sess:
        sess.clear()

    resp = client.get("/registro")

    assert resp.status_code == 200


# =====================================================
# PRUEBA 3 – Camino 3
# POST donde el usuario YA existe

def test_prueba3_usuario_ya_existente(client, monkeypatch):
    import app as modulo

    class UsuarioFake:
        nombre = "Ana"
        contrasena = "123"
        correo = "ana@mail.com"
        numero_documento = "111"
        tipo_documento = "Cedula de Ciudadania"
        donante = False
        admin = False
        enfermero = False
        puntos = 0
        total_donado = 0
        tipo_de_sangre = "O+"
        perfil_imagen_link = None
        perfil_imagen_deletehash = None

    monkeypatch.setattr(modulo, "obtenerValoresUsuario", lambda request: UsuarioFake())

    # Usuario ya existe
    monkeypatch.setattr(modulo, "verificarExistenciaUsuario", lambda doc, tipo: True)
    monkeypatch.setattr(modulo, "verificarCorreo", lambda correo: False)

    resp = client.post("/registro", data={
        "numero_documento": "111",
        "tipo_documento": "Cedula de Ciudadania",
        "correo": "ana@mail.com",
        "contrasena": "123"
    })

    assert resp.status_code == 200

    with client.session_transaction() as sess:
        assert sess.get("registarse_verificacion_resultado") is True
        assert "user_data" not in sess


# =====================================================
# PRUEBA 4 – Camino 4
# POST donde correo ya existe

def test_prueba4_correo_ya_existente(client, monkeypatch):
    import app as modulo

    class UsuarioFake:
        nombre = "Ana"
        contrasena = "123"
        correo = "ana@mail.com"
        numero_documento = "111"
        tipo_documento = "Cedula de Ciudadania"
        donante = False
        admin = False
        enfermero = False
        puntos = 0
        total_donado = 0
        tipo_de_sangre = "O+"
        perfil_imagen_link = None
        perfil_imagen_deletehash = None

    monkeypatch.setattr(modulo, "obtenerValoresUsuario", lambda request: UsuarioFake())

    # Usuario no existe pero correo sí
    monkeypatch.setattr(modulo, "verificarExistenciaUsuario", lambda doc, tipo: False)
    monkeypatch.setattr(modulo, "verificarCorreo", lambda correo: True)

    resp = client.post("/registro", data={
        "numero_documento": "111",
        "tipo_documento": "Cedula de Ciudadania",
        "correo": "ana@mail.com",
        "contrasena": "123"
    })

    assert resp.status_code == 200

    with client.session_transaction() as sess:
        assert sess.get("registarse_verificacion_resultado") is True
        assert "user_data" not in sess


# =====================================================
# PRUEBA 5 – Camino 5
# Usuario nuevo y correo nuevo

def test_prueba5_registro_exitoso(client, monkeypatch):
    import app as modulo

    class UsuarioFake:
        nombre = "Ana"
        contrasena = "123"
        correo = "ana@mail.com"
        numero_documento = "111"
        tipo_documento = "Cedula de Ciudadania"
        donante = False
        admin = False
        enfermero = False
        puntos = 0
        total_donado = 0
        tipo_de_sangre = "O+"
        perfil_imagen_link = None
        perfil_imagen_deletehash = None
        codigo_recuperacion = None

    monkeypatch.setattr(modulo, "obtenerValoresUsuario", lambda request: UsuarioFake())

    # No existe usuario ni correo
    monkeypatch.setattr(modulo, "verificarExistenciaUsuario", lambda doc, tipo: False)
    monkeypatch.setattr(modulo, "verificarCorreo", lambda correo: False)

    monkeypatch.setattr(modulo, "generarUsuarioImagen", lambda imagen, handler: ("link_img", "del_hash"))
    monkeypatch.setattr(modulo, "registrarUsuario", lambda *args, **kwargs: None)
    monkeypatch.setattr(modulo, "generarUsuarioSesion", lambda *args, **kwargs: {"nombre": "Ana", "doc": "111"})

    resp = client.post("/registro", data={
        "numero_documento": "111",
        "tipo_documento": "Cedula de Ciudadania",
        "correo": "ana@mail.com",
        "contrasena": "123"
    })

    assert resp.status_code == 200

    with client.session_transaction() as sess:
        assert sess.get("registarse_verificacion_resultado") is False
        assert sess.get("user_data") == {"nombre": "Ana", "doc": "111"}