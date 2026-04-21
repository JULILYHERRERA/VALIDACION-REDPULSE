"""
HU29 – Estadísticas y reportes (ruta `/estadisticas` en app.py).

Incluye pruebas con dobles (stubs/spies) y un caso xfail que documenta
la ausencia de mensaje informativo cuando no hay datos en la plantilla actual.
"""
import json
import os
import sys

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as modulo
from app import app

def _sesion_admin():
    return {"nombre": "Admin", "admin": True, "enfermero": False}

# =====================================================
# PRUEBA 1 – Sin sesión redirige a home
# =====================================================
def test_prueba1_sin_sesion_redirige_a_home(client):
    # ARRANGE

    # ACT
    resp = client.get("/estadisticas", follow_redirects=False)

    # ASSERT
    assert resp.status_code in (301, 302)
    assert resp.headers.get("Location") is not None

# =====================================================
# PRUEBA 2 – Usuario sin rol administrador redirige
# =====================================================
def test_prueba2_usuario_sin_admin_redirige_a_home(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Laura", "admin": False, "enfermero": False}

    # ACT
    resp = client.get("/estadisticas", follow_redirects=False)

    # ASSERT
    assert resp.status_code in (301, 302)
    assert resp.headers.get("Location") is not None

# =====================================================
# PRUEBA 3 – Administrador accede al módulo y ve estructura de gráficos
# STUB
# =====================================================
def test_prueba3_admin_accede_modulo_muestra_graficos(client, monkeypatch):
    # ARRANGE
    monkeypatch.setattr(modulo, "obtenerDonacionesPorMes", lambda: {"Marzo": 12})
    monkeypatch.setattr(
        modulo, "obtenerCantidadDeSangrePorTipo", lambda: {"O+": 1500, "A+": 800}
    )
    with client.session_transaction() as sess:
        sess["user_data"] = _sesion_admin()

    # ACT
    resp = client.get("/estadisticas")
    body = resp.data.decode("utf-8")

    # ASSERT
    assert resp.status_code == 200
    assert "Donaciones por Mes" in body
    assert "Cantidad de Sangre por Tipo" in body
    assert "monthlyDonationsChart" in body
    assert "bloodTypeChart" in body
    assert "chart.js" in body.lower()

# =====================================================
# PRUEBA 4 – Se consultan servicios y se serializa JSON para la vista
# STUB + SPY
# =====================================================
def test_prueba4_consulta_servicios_y_pasa_json_a_render_template(client, monkeypatch):
    # ARRANGE
    donaciones = {"Enero": 5, "Febrero": 8}
    sangre = {"B+": 2000}

    llamadas_don = []
    llamadas_tipo = []

    def stub_donaciones():
        llamadas_don.append(True)
        return donaciones

    def stub_sangre():
        llamadas_tipo.append(True)
        return sangre

    captura_render = {}

    def fake_render(template_name, **kwargs):
        captura_render["template"] = template_name
        captura_render["donaciones_por_mes"] = kwargs.get("donaciones_por_mes")
        captura_render["sangre_por_tipo"] = kwargs.get("sangre_por_tipo")
        return "render ok"

    monkeypatch.setattr(modulo, "obtenerDonacionesPorMes", stub_donaciones)
    monkeypatch.setattr(modulo, "obtenerCantidadDeSangrePorTipo", stub_sangre)
    monkeypatch.setattr(modulo, "render_template", fake_render)

    with client.session_transaction() as sess:
        sess["user_data"] = _sesion_admin()

    # ACT
    resp = client.get("/estadisticas")

    # ASSERT
    assert resp.status_code == 200
    assert captura_render["template"] == "estadisticas.html"
    assert len(llamadas_don) == 1
    assert len(llamadas_tipo) == 1
    assert json.loads(captura_render["donaciones_por_mes"]) == donaciones
    assert json.loads(captura_render["sangre_por_tipo"]) == sangre

# =====================================================
# PRUEBA 5 – Con donaciones por mes el HTML incluye los datos serializados
# STUB
# =====================================================
def test_prueba5_reporte_mensual_refleja_datos_en_pagina(client, monkeypatch):
    # ARRANGE
    monkeypatch.setattr(modulo, "obtenerDonacionesPorMes", lambda: {"Marzo": 20})
    monkeypatch.setattr(modulo, "obtenerCantidadDeSangrePorTipo", lambda: {})
    with client.session_transaction() as sess:
        sess["user_data"] = _sesion_admin()

    # ACT
    resp = client.get("/estadisticas")
    body = resp.data.decode("utf-8")

    # ASSERT
    assert resp.status_code == 200
    assert '"Marzo"' in body or "'Marzo'" in body
    assert "20" in body

# =====================================================
# PRUEBA 6 – HU29: sin datos debería mostrar mensaje informativo
# =====================================================
def test_prueba6_sin_datos_muestra_mensaje_informativo(client, monkeypatch):
    # ARRANGE
    monkeypatch.setattr(modulo, "obtenerDonacionesPorMes", lambda: {})
    monkeypatch.setattr(modulo, "obtenerCantidadDeSangrePorTipo", lambda: {})
    with client.session_transaction() as sess:
        sess["user_data"] = _sesion_admin()

    # ACT
    resp = client.get("/estadisticas")
    body = resp.data.decode("utf-8")

    # ASSERT
    assert resp.status_code == 200
    assert "no hay datos" in body.lower()
