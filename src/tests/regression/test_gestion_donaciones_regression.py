import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# REGRESSION 1 – Agregar donación valida tipo de dato
# =====================================================
def test_regression_donacion_tipo_dato(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"enfermero": True}
        sess["enfermero_usuario_obtenido"] = {"cedula_usuario": "123"}

    resp = client.post("/agregar_donacion", data={
        "cantidad_donada": "no-numero",
        "fecha_donacion": "2026-03-23"
    })
    
    assert "número válido" in resp.data.decode("utf-8").lower()

# =====================================================
# REGRESSION 2 – Limpia mensajes tras éxito
# =====================================================
def test_regression_donacion_limpia_mensajes(client, monkeypatch):
    with client.session_transaction() as sess:
        sess["user_data"] = {"enfermero": True}
        sess["enfermero_usuario_obtenido"] = {"cedula_usuario": "123", "tipo_cedula_usuario": "CC"}
        sess["mensaje_validacion_donacion"] = "Error previo"

    monkeypatch.setattr(app, "insertarDonacion", lambda *a: True)

    client.post("/agregar_donacion", data={
        "cantidad_donada": "450",
        "fecha_donacion": "2026-03-23"
    })
    
    with client.session_transaction() as sess:
        assert "mensaje_validacion_donacion" not in sess
