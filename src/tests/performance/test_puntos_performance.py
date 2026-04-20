import time
import pytest
import sys
import os
from app import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# PERFORMANCE 1 – Carga de la página de Puntos
# =====================================================
def test_performance_puntos_renderizado(client):
    """Verifica que la página de puntos carga rápidamente 10 veces."""
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Test", "puntos": 100}

    start = time.time()
    for _ in range(10):
        client.get("/puntos")
    end = time.time()
    
    assert (end - start) < 1.0  # Menos de 1 segundo para 10 cargas

# =====================================================
# PERFORMANCE 2 – Procesamiento de Puntos POST
# =====================================================
def test_performance_puntos_post(client, monkeypatch):
    """Verifica que el procesamiento de puntos (mocked) es rápido."""
    import app as modulo
    
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Test", "puntos": 100}

    monkeypatch.setattr(modulo, "procesar_puntos", lambda p: True)
    monkeypatch.setattr(modulo, "obtenerValorUsuarioSesion", lambda key: 50)

    start = time.time()
    for _ in range(10):
        client.post("/puntos", json={"puntos_seleccionados": 50})
    end = time.time()
    
    assert (end - start) < 1.0  # Menos de 1 segundo para 10 posts
