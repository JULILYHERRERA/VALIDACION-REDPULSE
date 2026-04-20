import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# SECURITY 1 – Agregar donación requiere rol ENFERMERO
# =====================================================
def test_security_donacion_solo_enfermero(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"enfermero": False, "admin": True}
    
    resp = client.get("/agregar_donacion", follow_redirects=False)
    assert resp.status_code in (301, 302)

# =====================================================
# SECURITY 2 – Agregar donación requiere usuario verificado
# =====================================================
def test_security_donacion_usuario_no_verificado(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"enfermero": True}
        # Falta enfermero_usuario_obtenido
    
    resp = client.post("/agregar_donacion", data={"cantidad": 300}, follow_redirects=False)
    assert resp.status_code in (301, 302)
