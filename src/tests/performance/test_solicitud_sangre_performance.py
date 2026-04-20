import time
import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# PERFORMANCE 1 – Creación de solicitudes masivas
# =====================================================
def test_performance_creacion_solicitudes(client, monkeypatch):
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Laura", "registros": []}

    monkeypatch.setattr(app, "crearRegistro", lambda r, u: True)

    start = time.time()
    for _ in range(5):
        client.post("/solicitud_donacion", data={
            "cantidad_sangre_donada": "300",
            "razon": "Cirugia",
            "prioridad_solicitud": "Alta"
        })
    end = time.time()
    
    assert (end - start) < 10.0
