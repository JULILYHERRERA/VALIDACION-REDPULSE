import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# REGRESSION 1 – Validación de campos obligatorios
# =====================================================
def test_regression_solicitud_campos_obligatorios(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Laura"}

    resp = client.post("/solicitud_donacion", data={
        "cantidad_sangre_donada": "",
        "razon": "",
        "prioridad_solicitud": ""
    })
    
    assert b"obligatorios" in resp.data.lower()

# =====================================================
# REGRESSION 2 – Solicitud exitosa limpia mensajes de error
# =====================================================
def test_regression_solicitud_limpia_errores(client, monkeypatch):
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Laura", "registros": []}
        sess["mensaje_validacion"] = "Error previo"

    monkeypatch.setattr(app, "crearRegistro", lambda r, u: True)

    client.post("/solicitud_donacion", data={
        "cantidad_sangre_donada": "300",
        "razon": "Cirugia",
        "prioridad_solicitud": "Alta"
    })
    
    with client.session_transaction() as sess:
        assert "mensaje_validacion" not in sess
