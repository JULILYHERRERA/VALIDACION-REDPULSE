import time
import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# PERFORMANCE 1 – Cálculo de estadísticas
# =====================================================
def test_performance_calculo_estadisticas(client, monkeypatch):
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    monkeypatch.setattr(app, "obtenerDonacionesPorMes", lambda: {str(i): i for i in range(12)})
    monkeypatch.setattr(app, "obtenerCantidadDeSangrePorTipo", lambda: {str(i): i*100 for i in range(8)})

    start = time.time()
    for _ in range(10):
        client.get("/estadisticas")
    end = time.time()
    
    assert (end - start) < 1.0  # Cargar página de estadísticas 10 veces en menos de 1 segundo
