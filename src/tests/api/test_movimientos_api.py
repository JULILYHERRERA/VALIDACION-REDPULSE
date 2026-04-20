import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# API 1 – GET movimientos con sesión
# =====================================================
def test_api_get_movimientos_con_sesion(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {
            "nombre": "Laura",
            "registros": [{"TIPO_REGISTRO": "solicitud", "FECHA": "2026-03-23", "CANTIDAD": 300}]
        }

    resp = client.get("/movimientos")
    assert resp.status_code == 200
    assert b"Movimiento 1" in resp.data

# =====================================================
# API 2 – GET movimientos sin sesión
# =====================================================
def test_api_get_movimientos_sin_sesion(client):
    resp = client.get("/movimientos", follow_redirects=False)
    assert resp.status_code in (301, 302)
