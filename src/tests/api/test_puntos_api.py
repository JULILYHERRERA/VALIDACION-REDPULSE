import pytest
import sys
import os
from app import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# API 1 – GET Puntos autenticado
# =====================================================
def test_api_puntos_get_autenticado(client):
    """Verifica que un usuario autenticado puede acceder a la vista de puntos."""
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Test", "puntos": 100}

    resp = client.get("/puntos")
    assert resp.status_code == 200
    assert b"puntos" in resp.data.lower()

# =====================================================
# API 2 – GET Puntos no autenticado
# =====================================================
def test_api_puntos_get_no_autenticado(client):
    """Verifica que un usuario no autenticado es redirigido."""
    resp = client.get("/puntos", follow_redirects=False)
    assert resp.status_code in (301, 302)

# =====================================================
# API 3 – POST Puntos exitoso (JSON)
# =====================================================
def test_api_puntos_post_exitoso(client, monkeypatch):
    """Verifica que el canje de puntos funciona correctamente."""
    import app as modulo
    
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Test", "puntos": 100}

    monkeypatch.setattr(modulo, "procesar_puntos", lambda p: True)
    monkeypatch.setattr(modulo, "obtenerValorUsuarioSesion", lambda key: 50)

    resp = client.post("/puntos", json={"puntos_seleccionados": 50})
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["nuevos_puntos"] == 50

# =====================================================
# API 4 – POST Puntos datos incompletos
# =====================================================
def test_api_puntos_post_incompleto(client):
    """Verifica el error cuando no se envían los puntos seleccionados."""
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Test", "puntos": 100}

    resp = client.post("/puntos", json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["success"] is False
    assert "incompletos" in data["error"].lower()
