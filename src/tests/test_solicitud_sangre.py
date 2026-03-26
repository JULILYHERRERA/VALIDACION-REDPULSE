import os
import sys
from datetime import datetime

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as modulo
from app import app

def _user_data_solicitante(registros=None):
    if registros is None:
        registros = []
    return {
        "nombre": "Laura",
        "puntos": 2000,
        "numero_documento": "987654321",
        "tipo_documento": "CC",
        "tipo_de_sangre": "O+",
        "registros": registros,
        "cnt_registros": len(registros),
    }

def _form_solicitud_valido():
    return {
        "cantidad_sangre_donada": "300",
        "razon": "Cirugía programada",
        "comentarios": "Paciente estable",
        "prioridad_solicitud": "2",
    }

# =====================================================
# PRUEBA 1 – Sin sesión redirige a home
# =====================================================
def test_prueba1_sin_sesion_redirige_a_home(client):
    # ACT
    resp = client.get("/solicitud_donacion", follow_redirects=False)

    # ASSERT
    assert resp.status_code in (301, 302)
    assert resp.headers.get("Location") is not None

# =====================================================
# PRUEBA 2 – Solicitante con sesión renderiza formulario
# =====================================================
def test_prueba2_solicitante_con_sesion_renderiza_formulario(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = _user_data_solicitante()

    # ACT
    resp = client.get("/solicitud_donacion")
    body = resp.data.decode("utf-8")

    # ASSERT
    assert resp.status_code == 200
    assert "Solicitud de Sangre" in body
    assert "cantidad_sangre_donada" in body

# =====================================================
# PRUEBA 3 – Registro exitoso setea bandera en sesión
# STUB + SPY
# =====================================================
def test_prueba3_registro_exitoso_setea_bandera_true(client, monkeypatch):
    # ARRANGE
    monkeypatch.setattr(modulo, "crearRegistro", lambda request_obj, user_data: True)
    with client.session_transaction() as sess:
        sess["user_data"] = _user_data_solicitante()

    # ACT
    resp = client.post("/solicitud_donacion", data=_form_solicitud_valido())

    # ASSERT
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess["registro_creado"] is True

# =====================================================
# PRUEBA 4 – Registro fallido setea bandera false
# =====================================================
def test_prueba4_registro_fallido_setea_bandera_false(client, monkeypatch):
    # ARRANGE
    monkeypatch.setattr(modulo, "crearRegistro", lambda request_obj, user_data: False)
    with client.session_transaction() as sess:
        sess["user_data"] = _user_data_solicitante()

    # ACT
    resp = client.post("/solicitud_donacion", data=_form_solicitud_valido())

    # ASSERT
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess["registro_creado"] is False

# =====================================================
# PRUEBA 5 – Campos obligatorios vacíos: debería mostrar validaciones
# =====================================================
def test_prueba5_campos_obligatorios_vacios_muestra_mensajes_de_validacion(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = _user_data_solicitante()

    # ACT
    resp = client.post(
        "/solicitud_donacion",
        data={
            "cantidad_sangre_donada": "",
            "razon": "",
            "comentarios": "sin datos",
            "prioridad_solicitud": "",
        },
    )
    body = resp.data.decode("utf-8")

    # ASSERT
    assert resp.status_code == 200
    assert "obligatorios" in body.lower()

# =====================================================
# PRUEBA 6 – Solicitud registrada aparece en historial
# STUB + SPY
# =====================================================
def test_prueba6_solicitud_registrada_aparece_en_historial(client, monkeypatch):
    # ARRANGE
    registro_nuevo = {
        "TIPO_REGISTRO": "Solicitud",
        "CANTIDAD": 300,
        "PRIORIDAD": 2,
        "ESTADO": "Pendiente",
        "FECHA": "23-03-2026",
    }

    def fake_crear_registro(request_obj, user_data):
        user_data["registros"].append(registro_nuevo)
        user_data["cnt_registros"] = len(user_data["registros"])
        return True

    monkeypatch.setattr(modulo, "crearRegistro", fake_crear_registro)

    with client.session_transaction() as sess:
        sess["user_data"] = _user_data_solicitante(registros=[])

    # ACT
    client.post("/solicitud_donacion", data=_form_solicitud_valido())
    resp_historial = client.get("/movimientos")
    body = resp_historial.data.decode("utf-8")

    # ASSERT
    assert resp_historial.status_code == 200
    assert "Usted realizó una Solicitud el 23-03-2026" in body
    assert "de 300 ml" in body

# =====================================================
# PRUEBA 7 – Campos obligatorios vacíos no debería intentar registrar
# =====================================================
def test_prueba7_campos_vacios_no_deberia_intentar_registrar(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_crear_registro(request_obj, user_data):
        llamadas.append(True)
        return False

    monkeypatch.setattr(modulo, "crearRegistro", fake_crear_registro)
    with client.session_transaction() as sess:
        sess["user_data"] = _user_data_solicitante()

    # ACT
    resp = client.post(
        "/solicitud_donacion",
        data={
            "cantidad_sangre_donada": "",
            "razon": "",
            "comentarios": "",
            "prioridad_solicitud": "",
        },
    )

    # ASSERT
    assert resp.status_code == 200
    assert llamadas == []

# =====================================================
# PRUEBA 8 – Error de validación debería dejar mensaje en sesión
# =====================================================
def test_prueba8_error_validacion_deberia_guardar_mensaje_en_sesion(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = _user_data_solicitante()

    # ACT
    client.post(
        "/solicitud_donacion",
        data={
            "cantidad_sangre_donada": "",
            "razon": "",
            "comentarios": "sin datos",
            "prioridad_solicitud": "",
        },
    )

    # ASSERT
    with client.session_transaction() as sess:
        assert "mensaje_validacion" in sess
