import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# SECURITY 1 – Movimientos requiere sesión
# =====================================================
def test_security_movimientos_sin_sesion(client):
    resp = client.get("/movimientos", follow_redirects=False)
    assert resp.status_code in (301, 302)

# =====================================================
# SECURITY 2 – Acceso solo a registros propios (lógica de sesión)
# =====================================================
def test_security_movimientos_aislamiento(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Atacante", "registros": []}
    
    resp = client.get("/movimientos")
    assert resp.status_code == 200
    assert b"Movimientos" in resp.data
    assert b"Laura" not in resp.data
