import pytest
import sys
import os
from app import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# SEGURIDAD 1 – Acceso sin sesión
# =====================================================
def test_security_puntos_sin_sesion(client):
    """Verifica que el acceso sin sesión sea denegado."""
    resp = client.get("/puntos", follow_redirects=False)
    assert resp.status_code in (301, 302)

# =====================================================
# SEGURIDAD 2 – Puntos inválidos (Tipo de dato)
# =====================================================
def test_security_puntos_invalidos_tipo(client):
    """Verifica que si los puntos no son enteros, se maneje el error."""
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Test", "puntos": 100}

    resp = client.post("/puntos", json={"puntos_seleccionados": "NoSoyEntero"})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["success"] is False
    assert "inválidos" in data["error"].lower()

# =====================================================
# SEGURIDAD 3 – Puntos inválidos (None)
# =====================================================
def test_security_puntos_invalidos_none(client):
    """Verifica que si los puntos son None, se maneje el error."""
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Test", "puntos": 100}

    resp = client.post("/puntos", json={"puntos_seleccionados": None})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["success"] is False
    assert "inválidos" in data["error"].lower()
