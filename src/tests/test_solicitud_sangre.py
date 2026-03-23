import os
import sys

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as modulo
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    with app.test_client() as client:
        yield client


def _user_data_solicitante(registros=None):
    return {
        "nombre": "Laura",
        "correo": "laura@mail.com",
        "numero_documento": "123456789",
        "tipo_documento": "CC",
        "tipo_de_sangre": "O+",
        "registros": registros if registros is not None else [],
        "cnt_registros": len(registros) if registros is not None else 0,
    }


def _form_solicitud_valido():
    return {
        "cantidad_sangre_donada": "300",
        "razon": "Cirugia programada",
        "comentarios": "Paciente en observacion",
        "prioridad_solicitud": "2",
    }


# =====================================================
# PRUEBA 1 – Sin sesión redirige a home
# =====================================================
def test_prueba1_sin_sesion_redirige_a_home(client):
    # ARRANGE

    # ACT
    resp = client.get("/solicitud_donacion", follow_redirects=False)

    # ASSERT
    assert resp.status_code in (301, 302)
    assert resp.headers.get("Location") is not None


# =====================================================
# PRUEBA 2 – Con sesión renderiza formulario de solicitud
# =====================================================
def test_prueba2_con_sesion_renderiza_formulario(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = _user_data_solicitante()

    # ACT
    resp = client.get("/solicitud_donacion")
    body = resp.data.decode("utf-8")

    # ASSERT
    assert resp.status_code == 200
    assert "Solicitud de Sangre" in body
    assert "Enviar Solicitud" in body


# =====================================================
# PRUEBA 3 – Formulario válido registra solicitud exitosamente
# STUB + SPY
# =====================================================
def test_prueba3_formulario_valido_registra_solicitud_exitosamente(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_crear_registro(request_obj, user_data):
        llamadas.append(
            {
                "cantidad": request_obj.form.get("cantidad_sangre_donada"),
                "razon": request_obj.form.get("razon"),
                "prioridad": request_obj.form.get("prioridad_solicitud"),
                "documento": user_data["numero_documento"],
            }
        )
        return True

    monkeypatch.setattr(modulo, "crearRegistro", fake_crear_registro)

    with client.session_transaction() as sess:
        sess["user_data"] = _user_data_solicitante()

    # ACT
    resp = client.post("/solicitud_donacion", data=_form_solicitud_valido())

    # ASSERT
    assert resp.status_code == 200
    assert len(llamadas) == 1
    assert llamadas[0]["cantidad"] == "300"
    assert llamadas[0]["razon"] == "Cirugia programada"
    assert llamadas[0]["prioridad"] == "2"

    with client.session_transaction() as sess:
        assert sess["registro_creado"] is True


# =====================================================
# PRUEBA 4 – Registro fallido deja bandera en False
# STUB
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
# (la validación actual es HTML required; backend aún no valida)
# =====================================================
@pytest.mark.xfail(
    reason="La ruta no valida campos obligatorios en backend ni muestra mensajes explícitos.",
    strict=True,
)
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
    assert "campo obligatorio" in body.lower()


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
# (fallo esperado: hoy sí invoca crearRegistro)
# STUB + SPY
# =====================================================
@pytest.mark.xfail(
    reason="La ruta llama crearRegistro sin validar campos vacíos en backend.",
    strict=True,
)
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
# (fallo esperado: hoy no existe este mensaje backend)
# =====================================================
@pytest.mark.xfail(
    reason="No se guarda mensaje de validación en sesión al fallar formulario.",
    strict=True,
)
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
