import time
import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# PERFORMANCE 1 – Inserción de donaciones masivas
# =====================================================
def test_performance_insercion_donaciones(client, monkeypatch):
    with client.session_transaction() as sess:
        sess["user_data"] = {"enfermero": True}
        sess["enfermero_usuario_obtenido"] = {"cedula_usuario": "123", "tipo_cedula_usuario": "CC"}

    monkeypatch.setattr(app, "insertarDonacion", lambda *a: True)

    start = time.time()
    for _ in range(5):
        client.post("/agregar_donacion", data={
            "cantidad_donada": "450",
            "fecha_donacion": "2026-03-23"
        })
    end = time.time()
    
    assert (end - start) < 10.0
