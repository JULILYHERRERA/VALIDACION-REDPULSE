import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

# =====================================================
# PRUEBA 1 – Redirige si ya hay sesión
# =====================================================
def test_prueba1_redirige_si_ya_hay_sesion(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "test"}

    # ACT
    resp = client.get("/registro", follow_redirects=False)

    # ASSERT
    assert resp.status_code in (301, 302)
    assert resp.headers.get("Location") is not None

# =====================================================
# PRUEBA 2 – GET renderiza registro (Sin sesión)
# =====================================================
def test_prueba2_get_renderiza_registro(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess.clear()

    # ACT
    resp = client.get("/registro")

    # ASSERT
    assert resp.status_code == 200

# =====================================================
# PRUEBA 3 – Usuario ya existe -> STUB
# =====================================================
def test_prueba3_usuario_ya_existente(client, monkeypatch):
    import app as modulo

    # ARRANGE
    # DOBLE DE PRUEBA (STUB): Objeto fake que simula datos de formulario
    class UsuarioFake:
        nombre = "Ana"; contrasena = "123"; correo = "ana@mail.com"
        numero_documento = "111"; tipo_documento = "Cedula de Ciudadania"
        donante = False; admin = False; enfermero = False; puntos = 0
        total_donado = 0; tipo_de_sangre = "O+"; perfil_imagen_link = None
        perfil_imagen_deletehash = None

    # STUBS: Forzamos respuestas para simular colisión de documento
    monkeypatch.setattr(modulo, "obtenerValoresUsuario", lambda request: UsuarioFake())
    monkeypatch.setattr(modulo, "verificarExistenciaUsuario", lambda doc, tipo: True)
    monkeypatch.setattr(modulo, "verificarCorreo", lambda correo: False)

    # ACT
    resp = client.post("/registro", data={
        "numero_documento": "111",
        "tipo_documento": "Cedula de Ciudadania",
        "correo": "ana@mail.com",
        "contrasena": "123"
    })

    # ASSERT
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        # Verificamos que la bandera de error sea True (Existe)
        assert sess.get("registarse_verificacion_resultado") is True
        assert "user_data" not in sess

# =====================================================
# PRUEBA 4 – Correo ya existe -> STUB
# =====================================================
def test_prueba4_correo_ya_existente(client, monkeypatch):
    import app as modulo

    # ARRANGE
    # DOBLE DE PRUEBA (STUB): Objeto fake de usuario
    class UsuarioFake:
        nombre = "Ana"; contrasena = "123"; correo = "ana@mail.com"
        numero_documento = "111"; tipo_documento = "Cedula de Ciudadania"
        donante = False; admin = False; enfermero = False; puntos = 0
        total_donado = 0; tipo_de_sangre = "O+"; perfil_imagen_link = None
        perfil_imagen_deletehash = None

    # STUBS: El usuario no existe por documento, pero el correo SÍ está registrado
    monkeypatch.setattr(modulo, "obtenerValoresUsuario", lambda request: UsuarioFake())
    monkeypatch.setattr(modulo, "verificarExistenciaUsuario", lambda doc, tipo: False)
    monkeypatch.setattr(modulo, "verificarCorreo", lambda correo: True)

    # ACT
    resp = client.post("/registro", data={
        "numero_documento": "111",
        "tipo_documento": "Cedula de Ciudadania",
        "correo": "ana@mail.com",
        "contrasena": "123"
    })

    # ASSERT
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess.get("registarse_verificacion_resultado") is True
        assert "user_data" not in sess

# =====================================================
# PRUEBA 5 – Registro exitoso -> MOCK + STUB
# =====================================================
def test_prueba5_registro_exitoso(client, monkeypatch):
    import app as modulo

    # ARRANGE
    # DOBLE DE PRUEBA (STUB): Objeto fake de usuario nuevo
    class UsuarioFake:
        nombre = "Ana"; contrasena = "123"; correo = "ana@mail.com"
        numero_documento = "111"; tipo_documento = "Cedula de Ciudadania"
        donante = False; admin = False; enfermero = False; puntos = 0
        total_donado = 0; tipo_de_sangre = "O+"; perfil_imagen_link = None
        perfil_imagen_deletehash = None; codigo_recuperacion = None

    monkeypatch.setattr(modulo, "obtenerValoresUsuario", lambda request: UsuarioFake())

    # STUBS: Simulamos que todo está disponible (Usuario y Correo nuevos)
    monkeypatch.setattr(modulo, "verificarExistenciaUsuario", lambda doc, tipo: False)
    monkeypatch.setattr(modulo, "verificarCorreo", lambda correo: False)
    monkeypatch.setattr(modulo, "generarUsuarioImagen", lambda imagen, handler: ("link_img", "del_hash"))
    
    # DOBLE DE PRUEBA (MOCK): Simulamos las funciones de persistencia y sesión
    monkeypatch.setattr(modulo, "registrarUsuario", lambda *args, **kwargs: None)
    monkeypatch.setattr(modulo, "generarUsuarioSesion", lambda *args, **kwargs: {"nombre": "Ana", "doc": "111"})

    # ACT
    resp = client.post("/registro", data={
        "numero_documento": "111",
        "tipo_documento": "Cedula de Ciudadania",
        "correo": "ana@mail.com",
        "contrasena": "123"
    })

    # ASSERT
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        # Verificamos que la bandera de error sea False (No hubo error)
        assert sess.get("registarse_verificacion_resultado") is False
        assert sess.get("user_data") == {"nombre": "Ana", "doc": "111"}

# =====================================================
# PRUEBA 6 – Error en Imagen -> Stub + mocks
# =====================================================
def test_prueba6_registro_fallo_imagen(client, monkeypatch):
    import app as modulo

    # ARRANGE (STUB): Ahora incluimos TODOS los atributos que pide registrarUsuario
    class UsuarioFake:
        nombre = "Ana"
        contrasena = "123"
        correo = "ana@mail.com"
        numero_documento = "111"
        tipo_documento = "CC"
        # Agregamos los faltantes para que no de AttributeError
        donante = False 
        admin = False
        enfermero = False
        puntos = 0
        total_donado = 0
        tipo_de_sangre = "O+"
        perfil_imagen_link = None
        perfil_imagen_deletehash = None

    monkeypatch.setattr(modulo, "obtenerValoresUsuario", lambda request: UsuarioFake())
    monkeypatch.setattr(modulo, "verificarExistenciaUsuario", lambda doc, tipo: False)
    monkeypatch.setattr(modulo, "verificarCorreo", lambda correo: False)

    # Situación real: Imgur falla (devuelve None)
    monkeypatch.setattr(modulo, "generarUsuarioImagen", lambda imagen, handler: (None, None))
    
    # MOCKS: Para que no toque la base de datos real
    monkeypatch.setattr(modulo, "registrarUsuario", lambda *args: None)
    monkeypatch.setattr(modulo, "generarUsuarioSesion", lambda *args: {"nombre": "Ana"})

    # ACT
    resp = client.post("/registro", data={"numero_documento": "111"})

    # ASSERT
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess.get("user_data") is not None