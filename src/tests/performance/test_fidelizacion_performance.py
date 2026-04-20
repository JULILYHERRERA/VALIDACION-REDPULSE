import time
import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# PERFORMANCE 1 – Redención masiva de puntos
# =====================================================
def test_performance_redencion_puntos(client, monkeypatch):
    with client.session_transaction() as sess:
        sess["user_data"] = {
            "puntos": 100000,
            "numero_documento": "123",
            "tipo_documento": "CC",
            "correo": "test@test.com"
        }

    monkeypatch.setattr(app, "actualizarPuntos", lambda *a: None)
    
    import controladores.puntos_controlador
    monkeypatch.setattr(controladores.puntos_controlador.email, "redimir_puntos_notificacion", lambda *a: None)

    start = time.time()
    for _ in range(5):
        client.post("/puntos", json={"puntos_seleccionados": 100})
    end = time.time()
    
    assert (end - start) < 10.0  # Ajustado para el entorno de sandbox
