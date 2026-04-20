import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# REGRESSION 1 – Movimientos no rompe con registros vacíos
# =====================================================
def test_regression_movimientos_vacios(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Laura", "registros": []}

    resp = client.get("/movimientos")
    assert resp.status_code == 200
    assert "no existen registros" in resp.data.decode("utf-8").lower()

# =====================================================
# REGRESSION 2 – Movimientos maneja registros incompletos
# =====================================================
def test_regression_movimientos_incompletos(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {
            "nombre": "Laura",
            "registros": [{"TIPO_REGISTRO": "solicitud"}]
        }

    resp = client.get("/movimientos")
    assert resp.status_code == 200
    assert b"fecha no disponible" in resp.data
