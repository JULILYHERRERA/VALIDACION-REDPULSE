import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as modulo
from app import app

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
# PRUEBA 2 – Con sesión válida renderiza vista
# STUB
# =====================================================
def test_prueba2_con_sesion_valida_renderiza_vista(client, monkeypatch):
    # ARRANGE
    contexto = {}

    def fake_render(template_name, **kwargs):
        contexto["template"] = template_name
        contexto["user_data"] = kwargs.get("user_data")
        return "render ok"

    monkeypatch.setattr(modulo, "render_template", fake_render)

    user_data_valido = {
        "nombre": "Juliana",
        "registros": [
            {
                "TIPO_REGISTRO": "donacion",
                "FECHA": "2026-03-23",
                "CANTIDAD": 450,
                "PRIORIDAD": "Alta",
                "ESTADO": "Completada"
            }
        ]
    }

    with client.session_transaction() as sess:
        sess["user_data"] = user_data_valido

    # ACT
    resp = client.get("/movimientos")

    # ASSERT
    assert resp.status_code == 200
    assert contexto["template"] == "movimientos.html"
    assert contexto["user_data"] == user_data_valido

# =====================================================
# PRUEBA 3 – Con sesión válida entrega registros
# STUB + SPY
# =====================================================
def test_prueba3_con_sesion_valida_entrega_registros(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_render(template_name, **kwargs):
        llamadas.append(kwargs.get("user_data"))
        return "render ok"

    monkeypatch.setattr(modulo, "render_template", fake_render)

    user_data_valido = {
        "nombre": "Juliana",
        "registros": [
            {
                "TIPO_REGISTRO": "solicitud",
                "FECHA": "2026-03-23",
                "CANTIDAD": 300,
                "PRIORIDAD": "Media",
                "ESTADO": "Pendiente"
            }
        ]
    }

    with client.session_transaction() as sess:
        sess["user_data"] = user_data_valido

    # ACT
    resp = client.get("/movimientos")

    # ASSERT
    assert resp.status_code == 200
    assert len(llamadas) == 1
    assert llamadas[0]["registros"][0]["TIPO_REGISTRO"] == "solicitud"

# =====================================================
# PRUEBA 4 – user_data sin registros no debería renderizar
# STUB + SPY (FALLA)
# =====================================================
def test_prueba4_user_data_sin_registros_no_deberia_renderizar(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_render(template_name, **kwargs):
        llamadas.append(kwargs.get("user_data"))
        return "render ok"

    monkeypatch.setattr(modulo, "render_template", fake_render)

    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Juliana"}

    # ACT
    resp = client.get("/movimientos", follow_redirects=False)

    # ASSERT
    assert resp.status_code in (301, 302)
    assert llamadas == []

# =====================================================
# PRUEBA 5 – user_data como texto no debería renderizar
# STUB + SPY (FALLA)
# =====================================================
def test_prueba5_user_data_como_texto_no_deberia_renderizar(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_render(template_name, **kwargs):
        llamadas.append(kwargs.get("user_data"))
        return "render ok"

    monkeypatch.setattr(modulo, "render_template", fake_render)

    with client.session_transaction() as sess:
        sess["user_data"] = "dato_invalido"

    # ACT
    resp = client.get("/movimientos", follow_redirects=False)

    # ASSERT
    assert resp.status_code in (301, 302)
    assert llamadas == []

# =====================================================
# PRUEBA 6 – registros en None no debería renderizar
# STUB + SPY (FALLA)
# =====================================================
def test_prueba6_registros_en_none_no_deberia_renderizar(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_render(template_name, **kwargs):
        llamadas.append(kwargs.get("user_data"))
        return "render ok"

    monkeypatch.setattr(modulo, "render_template", fake_render)

    with client.session_transaction() as sess:
        sess["user_data"] = {
            "nombre": "Juliana",
            "registros": None
        }

    # ACT
    resp = client.get("/movimientos", follow_redirects=False)

    # ASSERT
    assert resp.status_code in (301, 302)
    assert llamadas == []

# =====================================================
# PRUEBA 7 – registros vacío no debería renderizar
# STUB + SPY (FALLA)
# =====================================================
def test_prueba7_registros_vacio_no_deberia_renderizar(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_render(template_name, **kwargs):
        llamadas.append(kwargs.get("user_data"))
        return "render ok"

    monkeypatch.setattr(modulo, "render_template", fake_render)

    with client.session_transaction() as sess:
        sess["user_data"] = {
            "nombre": "Juliana",
            "registros": []
        }

    # ACT
    resp = client.get("/movimientos", follow_redirects=False)

    # ASSERT
    assert resp.status_code in (301, 302)
    assert llamadas == []

# =====================================================
# PRUEBA 8 – registro incompleto no debería renderizar
# STUB + SPY (FALLA)
# =====================================================
def test_prueba8_registro_incompleto_no_deberia_renderizar(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_render(template_name, **kwargs):
        llamadas.append(kwargs.get("user_data"))
        return "render ok"

    monkeypatch.setattr(modulo, "render_template", fake_render)

    with client.session_transaction() as sess:
        sess["user_data"] = {
            "nombre": "Juliana",
            "registros": [
                {
                    "TIPO_REGISTRO": "donacion"
                }
            ]
        }

    # ACT
    resp = client.get("/movimientos", follow_redirects=False)

    # ASSERT
    assert resp.status_code in (301, 302)
    assert llamadas == []