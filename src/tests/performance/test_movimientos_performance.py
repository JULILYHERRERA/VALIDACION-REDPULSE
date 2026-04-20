import time
import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# PERFORMANCE 1 – Carga de historial grande
# =====================================================
def test_performance_carga_historial(client):
    registros = [{"TIPO_REGISTRO": "solicitud", "FECHA": "2026-03-23", "CANTIDAD": 300} for _ in range(100)]
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Laura", "registros": registros}

    start = time.time()
    resp = client.get("/movimientos")
    end = time.time()
    
    assert resp.status_code == 200
    assert (end - start) < 0.5  # Cargar 100 registros en menos de 0.5 segundos
