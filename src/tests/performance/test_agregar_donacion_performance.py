import time
import pytest
import sys
import os
from app import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# PERFORMANCE 1 – Carga de la página de Agregar Donación
# =====================================================
def test_performance_agregar_donacion_renderizado(client):
    """Verifica que la página de agregar donación carga rápidamente 10 veces."""
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Enfermero", "enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "123",
            "tipo_cedula_usuario": "Cedula"
        }

    start = time.time()
    for _ in range(10):
        client.get("/agregar_donacion")
    end = time.time()
    
    assert (end - start) < 1.0  # Menos de 1 segundo para 10 cargas

# =====================================================
# PERFORMANCE 2 – Procesamiento de Agregar Donación POST
# =====================================================
def test_performance_agregar_donacion_post(client, monkeypatch):
    """Verifica que el procesamiento de agregar donación (mocked) es rápido."""
    import app as modulo
    
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Enfermero", "enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "123",
            "tipo_cedula_usuario": "Cedula"
        }

    monkeypatch.setattr(modulo, "insertarDonacion", lambda doc, tip, fec, can: True)

    start = time.time()
    for _ in range(10):
        client.post("/agregar_donacion", data={
            "cantidad_donada": "450",
            "fecha_donacion": "2024-01-01"
        })
    end = time.time()
    
    assert (end - start) < 1.0  # Menos de 1 segundo para 10 posts
