import pytest
import sys
import os
from app import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# REGRESSION 1 – Flujo normal de canje
# =====================================================
def test_regression_puntos_canje_normal(client, monkeypatch):
    """Verifica que el flujo de canje de puntos se mantenga estable."""
    import app as modulo
    
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Test", "puntos": 100}

    # Mockeamos para que siempre sea exitoso y devuelva el valor esperado
    monkeypatch.setattr(modulo, "procesar_puntos", lambda p: True)
    monkeypatch.setattr(modulo, "obtenerValorUsuarioSesion", lambda key: 50)

    resp = client.post("/puntos", json={"puntos_seleccionados": 50})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["nuevos_puntos"] == 50

# =====================================================
# REGRESSION 2 – Persistencia de puntos en la sesión
# =====================================================
def test_regression_puntos_persistencia(client, monkeypatch):
    """Verifica que la sesión mantenga el estado correcto."""
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Test", "puntos": 100}

    resp = client.get("/puntos")
    assert resp.status_code == 200
    # Al ser GET, no debería haber cambiado nada
    with client.session_transaction() as sess:
        assert sess["user_data"]["puntos"] == 100
