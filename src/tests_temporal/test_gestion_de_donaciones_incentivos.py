import os
import sys

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as modulo
from app import app

def _sesion_enfermero_base():
    return {"nombre": "Sandra", "enfermero": True, "admin": False}

def _usuario_obtenido_base():
    return {"cedula_usuario": "123456789", "tipo_cedula_usuario": "Cedula de Ciudadania"}

# =====================================================
# PRUEBA 1 – Sin sesión debería redirigir
# =====================================================
def test_prueba1_sin_sesion_deberia_redirigir_a_home(client):
    # ARRANGE

    # ACT
    resp = client.get("/enfermero", follow_redirects=False)

    # ASSERT
    assert resp.status_code in (301, 302)
    assert resp.headers.get("Location") is not None

# =====================================================
# PRUEBA 2 – Usuario sin rol enfermero es redirigido
# =====================================================
def test_prueba2_usuario_sin_rol_enfermero_es_redirigido(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Laura", "enfermero": False, "admin": False}

    # ACT
    resp = client.get("/enfermero", follow_redirects=False)

    # ASSERT
    assert resp.status_code in (301, 302)
    assert resp.headers.get("Location") is not None

# =====================================================
# PRUEBA 3 – Enfermero logueado visualiza formulario principal
# =====================================================
def test_prueba3_enfermero_logueado_visualiza_formulario_principal(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = _sesion_enfermero_base()

    # ACT
    resp = client.get("/enfermero")
    body = resp.data.decode("utf-8")

    # ASSERT
    assert resp.status_code == 200
    assert "Ingrese Cédula del Donante" in body
    assert "Verificar Cédula" in body

# =====================================================
# PRUEBA 4 – Cédula válida: verifica, guarda sesión y habilita flujo
# STUB + SPY
# =====================================================
def test_prueba4_cedula_valida_verifica_y_guarda_usuario_objetivo(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_verificar_existencia(numero_documento, tipo_documento):
        llamadas.append((numero_documento, tipo_documento))
        return True

    monkeypatch.setattr(modulo, "verificarExistenciaUsuario", fake_verificar_existencia)

    with client.session_transaction() as sess:
        sess["user_data"] = _sesion_enfermero_base()

    # ACT
    resp = client.post(
        "/enfermero",
        data={"cedula": "123456789", "tipo_documento": "Cedula de Ciudadania"},
    )

    # ASSERT
    assert resp.status_code == 200
    assert llamadas == [("123456789", "Cedula de Ciudadania")]
    with client.session_transaction() as sess:
        assert sess["enfermero_usuario_verificacion"] is True
        assert sess["enfermero_usuario_obtenido"] == _usuario_obtenido_base()

# =====================================================
# PRUEBA 5 – Cédula inexistente: marca verificación en False
# STUB
# =====================================================
def test_prueba5_cedula_inexistente_marca_verificacion_false(client, monkeypatch):
    # ARRANGE
    monkeypatch.setattr(modulo, "verificarExistenciaUsuario", lambda doc, tipo: False)
    with client.session_transaction() as sess:
        sess["user_data"] = _sesion_enfermero_base()

    # ACT
    resp = client.post(
        "/enfermero",
        data={"cedula": "999", "tipo_documento": "Cedula de Ciudadania"},
    )

    # ASSERT
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess["enfermero_usuario_verificacion"] is False
        assert sess.get("enfermero_usuario_obtenido") in (None, {})

# =====================================================
# PRUEBA 6 – Con usuario verificado muestra formulario de donación
# =====================================================
def test_prueba6_con_usuario_verificado_muestra_formulario_de_donacion(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = _sesion_enfermero_base()
        sess["enfermero_usuario_obtenido"] = _usuario_obtenido_base()

    # ACT
    resp = client.get("/agregar_donacion")
    body = resp.data.decode("utf-8")

    # ASSERT
    assert resp.status_code == 200
    assert "Cantidad Donada (ml)" in body
    assert "Fecha de la Donación" in body
    assert "Asignación de Puntos" in body

# =====================================================
# PRUEBA 7 – Datos válidos registran donación y guardan estado exitoso
# STUB + SPY
# =====================================================
def test_prueba7_datos_validos_registran_donacion_y_guardan_estado(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_insertar(numero_documento, tipo_documento, fecha, cantidad):
        llamadas.append((numero_documento, tipo_documento, fecha, cantidad))
        return True

    monkeypatch.setattr(modulo, "insertarDonacion", fake_insertar)

    with client.session_transaction() as sess:
        sess["user_data"] = _sesion_enfermero_base()
        sess["enfermero_usuario_obtenido"] = _usuario_obtenido_base()

    # ACT
    resp = client.post(
        "/agregar_donacion",
        data={"cantidad_donada": "450", "fecha_donacion": "2026-03-23"},
    )

    # ASSERT
    assert resp.status_code == 200
    assert llamadas == [("123456789", "Cedula de Ciudadania", "2026-03-23", 450)]
    with client.session_transaction() as sess:
        assert sess["donacion_exitosa"] is True

# =====================================================
# PRUEBA 8 – Cantidad inválida debería mostrar validación
# =====================================================
def test_prueba8_cantidad_invalida_deberia_responder_validacion(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = _sesion_enfermero_base()
        sess["enfermero_usuario_obtenido"] = _usuario_obtenido_base()

    # ACT
    resp = client.post(
        "/agregar_donacion",
        data={"cantidad_donada": "abc", "fecha_donacion": "2026-03-23"},
    )
    body = resp.data.decode("utf-8")

    # ASSERT
    assert resp.status_code == 200
    assert "número válido" in body.lower()

# =====================================================
# PRUEBA 9 – Sin usuario verificado debería bloquear registro limpiamente
# =====================================================
def test_prueba9_sin_usuario_verificado_deberia_bloquear_registro_limpiamente(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = _sesion_enfermero_base()

    # ACT
    resp = client.post(
        "/agregar_donacion",
        data={"cantidad_donada": "300", "fecha_donacion": "2026-03-23"},
        follow_redirects=False,
    )

    # ASSERT
    assert resp.status_code in (301, 302, 400)

# =====================================================
# PRUEBA 10 – Campos vacíos no deberían consultar existencia en backend
# STUB + SPY
# =====================================================
def test_prueba10_campos_vacios_no_deberian_consultar_existencia(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_verificar_existencia(numero_documento, tipo_documento):
        llamadas.append((numero_documento, tipo_documento))
        return False

    monkeypatch.setattr(modulo, "verificarExistenciaUsuario", fake_verificar_existencia)
    with client.session_transaction() as sess:
        sess["user_data"] = _sesion_enfermero_base()

    # ACT
    resp = client.post(
        "/enfermero",
        data={"cedula": "", "tipo_documento": ""},
    )

    # ASSERT
    assert resp.status_code == 200
    assert llamadas == []
