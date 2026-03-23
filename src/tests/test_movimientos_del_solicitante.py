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


def _registro_solicitud(fecha="2026-03-23", cantidad=300, prioridad="Media", estado="Pendiente"):
    return {
        "TIPO_REGISTRO": "solicitud",
        "FECHA": fecha,
        "CANTIDAD": cantidad,
        "PRIORIDAD": prioridad,
        "ESTADO": estado,
    }


# =====================================================
# PRUEBA 1 – Sin sesión redirige a home
# =====================================================
def test_prueba1_sin_sesion_redirige_a_home(client):
    # ARRANGE

    # ACT
    resp = client.get("/movimientos", follow_redirects=False)

    # ASSERT
    assert resp.status_code in (301, 302)
    assert resp.headers.get("Location") is not None


# =====================================================
# PRUEBA 2 – Solicitante con sesión renderiza la vista
# STUB + SPY
# =====================================================
def test_prueba2_solicitante_con_sesion_renderiza_vista(client, monkeypatch):
    # ARRANGE
    contexto = {}

    def fake_render(template_name, **kwargs):
        contexto["template"] = template_name
        contexto["user_data"] = kwargs.get("user_data")
        return "render ok"

    monkeypatch.setattr(modulo, "render_template", fake_render)

    user_data = {
        "nombre": "Laura",
        "registros": [_registro_solicitud()],
    }
    with client.session_transaction() as sess:
        sess["user_data"] = user_data

    # ACT
    resp = client.get("/movimientos")

    # ASSERT
    assert resp.status_code == 200
    assert contexto["template"] == "movimientos.html"
    assert contexto["user_data"] == user_data


# =====================================================
# PRUEBA 3 – Muestra todas las solicitudes registradas
# STUB + SPY
# =====================================================
def test_prueba3_muestra_todas_las_solicitudes_registradas(client, monkeypatch):
    # ARRANGE
    capturas = []

    def fake_render(template_name, **kwargs):
        capturas.append(kwargs.get("user_data"))
        return "render ok"

    monkeypatch.setattr(modulo, "render_template", fake_render)

    registros = [
        _registro_solicitud(fecha="2026-03-20", cantidad=250, prioridad="Alta", estado="Aprobada"),
        _registro_solicitud(fecha="2026-03-21", cantidad=350, prioridad="Media", estado="Pendiente"),
        _registro_solicitud(fecha="2026-03-22", cantidad=450, prioridad="Baja", estado="Completada"),
    ]
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Laura", "registros": registros}

    # ACT
    resp = client.get("/movimientos")

    # ASSERT
    assert resp.status_code == 200
    assert len(capturas) == 1
    assert len(capturas[0]["registros"]) == 3


# =====================================================
# PRUEBA 4 – Muestra detalle de cada solicitud en pantalla
# =====================================================
def test_prueba4_muestra_detalle_de_cada_solicitud(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {
            "nombre": "Laura",
            "registros": [
                _registro_solicitud(
                    fecha="2026-03-23",
                    cantidad=300,
                    prioridad="Alta",
                    estado="Pendiente",
                )
            ],
        }

    # ACT
    resp = client.get("/movimientos")
    body = resp.data.decode("utf-8")

    # ASSERT
    assert resp.status_code == 200
    assert "Usted realizó una solicitud el 2026-03-23" in body
    assert "de 300 ml" in body
    assert "con una prioridad de Alta" in body
    assert "con estado actual Pendiente" in body


# =====================================================
# PRUEBA 5 – Sin registros, renderiza sin movimientos
# STUB + SPY
# =====================================================
def test_prueba5_sin_registros_renderiza_sin_movimientos(client, monkeypatch):
    # ARRANGE
    contexto = {}

    def fake_render(template_name, **kwargs):
        contexto["template"] = template_name
        contexto["user_data"] = kwargs.get("user_data")
        return "render ok"

    monkeypatch.setattr(modulo, "render_template", fake_render)

    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Laura", "registros": []}

    # ACT
    resp = client.get("/movimientos")

    # ASSERT
    assert resp.status_code == 200
    assert contexto["template"] == "movimientos.html"
    assert contexto["user_data"]["registros"] == []


# =====================================================
# PRUEBA 6 – Sin registros visibles no muestra tarjetas históricas
# =====================================================
def test_prueba6_sin_registros_no_muestra_tarjetas_historicas(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Laura", "registros": []}

    # ACT
    resp = client.get("/movimientos")
    body = resp.data.decode("utf-8")

    # ASSERT
    assert resp.status_code == 200
    assert "Movimientos" in body
    assert "Movimiento 1" not in body


# =====================================================
# PRUEBA 7 – HU17: sin registros debería mostrar mensaje explícito
# (aún no implementado en `templates/movimientos.html`)
# =====================================================
@pytest.mark.xfail(
    reason="La plantilla no renderiza un mensaje cuando `registros` está vacío.",
    strict=True,
)
def test_prueba7_hu_sin_registros_muestra_mensaje_explicito(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Laura", "registros": []}

    # ACT
    resp = client.get("/movimientos")
    body = resp.data.decode("utf-8")

    # ASSERT
    assert resp.status_code == 200
    assert "no existen registros" in body.lower()


# =====================================================
# PRUEBA 8 – user_data sin clave `registros` debería manejarse sin 500
# (fallo esperado: la plantilla usa user_data['registros'] directamente)
# =====================================================
@pytest.mark.xfail(
    reason="No existe manejo defensivo cuando falta la clave `registros` en sesión.",
    strict=True,
)
def test_prueba8_user_data_sin_registros_deberia_manejarse_sin_error_500(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Laura"}

    # ACT
    resp = client.get("/movimientos")
    body = resp.data.decode("utf-8")

    # ASSERT
    assert resp.status_code == 200
    assert "no existen registros" in body.lower()


# =====================================================
# PRUEBA 9 – Registro incompleto debería mostrarse con valores por defecto
# (fallo esperado: la plantilla exige FECHA/CANTIDAD y rompe con KeyError)
# =====================================================
@pytest.mark.xfail(
    reason="No hay tolerancia a registros incompletos en la plantilla de movimientos.",
    strict=True,
)
def test_prueba9_registro_incompleto_deberia_mostrarse_con_valores_por_defecto(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {
            "nombre": "Laura",
            "registros": [{"TIPO_REGISTRO": "solicitud"}],
        }

    # ACT
    resp = client.get("/movimientos")
    body = resp.data.decode("utf-8")

    # ASSERT
    assert resp.status_code == 200
    assert "fecha no disponible" in body.lower()
