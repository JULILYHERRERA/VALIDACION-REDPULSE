import time
import pytest
import sys
import os
from app import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# PERFORMANCE 1 – Renderizado de Movimientos
# =====================================================
def test_performance_movimientos_renderizado(client):
    """Verifica que la página de movimientos carga rápidamente 10 veces."""
    with client.session_transaction() as sess:
        sess["user_data"] = {
            "nombre": "Test",
            "registros": [
                {
                    "TIPO_REGISTRO": "Donacion",
                    "FECHA": "2024-01-01",
                    "CANTIDAD": 450,
                    "PRIORIDAD": "Media",
                    "ESTADO": "Completada"
                }
            ]
        }

    start = time.time()
    for _ in range(10):
        client.get("/movimientos")
    end = time.time()
    
    assert (end - start) < 1.0  # Menos de 1 segundo para 10 cargas
