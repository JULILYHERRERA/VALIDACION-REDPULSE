import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# API 1 – POST redimir puntos exitoso
# =====================================================

def test_api_redimir_puntos_exitoso(client, monkeypatch):
    with client.session_transaction() as sess:
        sess["user_data"] = {
            "puntos": 5000,
            "numero_documento": "123",
            "tipo_documento": "CC",
            "correo": "test@test.com"
        }

    monkeypatch.setattr(app, "actualizarPuntos", lambda *a: None)
    
    import controladores.puntos_controlador
    monkeypatch.setattr(controladores.puntos_controlador.email, "redimir_puntos_notificacion", lambda *a: None)

    resp = client.post("/puntos", json={"puntos_seleccionados": 1000})
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["nuevos_puntos"] == 4000

# =====================================================
# API 2 – POST redimir puntos insuficientes
# =====================================================
def test_api_redimir_puntos_insuficientes(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {
            "puntos": 500,
            "numero_documento": "123",
            "tipo_documento": "CC",
            "correo": "test@test.com"
        }

    resp = client.post("/puntos", json={"puntos_seleccionados": 1000})
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is False

# =====================================================
# API 3 – POST datos inválidos
# =====================================================
def test_api_redimir_puntos_invalidos(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"puntos": 5000}

    resp = client.post("/puntos", json={"puntos_seleccionados": "abc"})
    assert resp.status_code == 400
