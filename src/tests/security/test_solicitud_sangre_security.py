import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# SECURITY 1 – Solicitud requiere sesión
# =====================================================
def test_security_solicitud_sin_sesion(client):
    resp = client.post("/solicitud_donacion", data={"cantidad": 300}, follow_redirects=False)
    assert resp.status_code in (301, 302)

# =====================================================
# SECURITY 2 – Prevención de Inyección (básico)
# =====================================================
def test_security_solicitud_inyeccion_tags(client, monkeypatch):
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Laura"}
    
    # El sistema debería manejar strings sin romperse
    monkeypatch.setattr(app, "crearRegistro", lambda r, u: True)
    
    resp = client.post("/solicitud_donacion", data={
        "cantidad_sangre_donada": "300",
        "razon": "<script>alert(1)</script>",
        "prioridad_solicitud": "Alta"
    })
    assert resp.status_code == 200
