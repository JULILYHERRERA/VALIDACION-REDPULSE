import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# API 1 – POST solicitud exitosa
# =====================================================
def test_api_post_solicitud_exitosa(client, monkeypatch):
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Laura", "registros": []}

    monkeypatch.setattr(app, "crearRegistro", lambda r, u: True)

    resp = client.post("/solicitud_donacion", data={
        "cantidad_sangre_donada": "300",
        "razon": "Cirugia",
        "prioridad_solicitud": "Alta"
    })
    
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess["registro_creado"] is True

# =====================================================
# API 2 – POST solicitud campos incompletos
# =====================================================
def test_api_post_solicitud_incompleta(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Laura"}

    resp = client.post("/solicitud_donacion", data={
        "cantidad_sangre_donada": "",
        "razon": ""
    })
    
    assert resp.status_code == 200
    body = resp.data.decode("utf-8")
    assert "obligatorios" in body.lower()
