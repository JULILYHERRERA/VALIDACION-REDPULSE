import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# REGRESSION 1 – Redención no permite puntos negativos
# =====================================================
def test_regression_no_puntos_negativos(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"puntos": 500}

    resp = client.post("/puntos", json={"puntos_seleccionados": 1000})
    data = resp.get_json()
    assert data["success"] is False
    assert sess["user_data"]["puntos"] == 500

# =====================================================
# REGRESSION 2 – Redención exitosa actualiza sesión
# =====================================================
def test_regression_actualiza_sesion_tras_redencion(client, monkeypatch):
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

    client.post("/puntos", json={"puntos_seleccionados": 1000})
    
    with client.session_transaction() as sess:
        assert sess["user_data"]["puntos"] == 4000
