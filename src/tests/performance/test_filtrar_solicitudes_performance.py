import time
import pytest
import sys
import os
from app import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# PERFORMANCE 1 – Carga de la página de Filtrar Solicitudes
# =====================================================
def test_performance_filtrar_solicitudes_renderizado(client):
    """Verifica que la página de filtrado carga rápidamente 10 veces."""
    start = time.time()
    for _ in range(10):
        client.get("/filtrar_solicitudes")
    end = time.time()
    
    assert (end - start) < 1.0  # Menos de 1 segundo para 10 cargas

# =====================================================
# PERFORMANCE 2 – Procesamiento de Filtrado POST
# =====================================================
def test_performance_filtrar_solicitudes_post(client, monkeypatch):
    """Verifica que el filtrado (mocked) es rápido."""
    import app as modulo
    
    monkeypatch.setattr(modulo, "obtenerSolicitudesPendientesPorTipo", lambda t: [])

    start = time.time()
    for _ in range(10):
        client.post("/filtrar_solicitudes", data={"tipo_sangre": "O+"})
    end = time.time()
    
    assert (end - start) < 1.0  # Menos de 1 segundo para 10 posts
