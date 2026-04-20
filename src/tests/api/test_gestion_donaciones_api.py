import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# API 1 – POST agregar donación exitoso
# =====================================================
def test_api_post_agregar_donacion_exitosa(client, monkeypatch):
    with client.session_transaction() as sess:
        sess["user_data"] = {"enfermero": True}
        sess["enfermero_usuario_obtenido"] = {"cedula_usuario": "123", "tipo_cedula_usuario": "CC"}

    monkeypatch.setattr(app, "insertarDonacion", lambda *a: True)

    resp = client.post("/agregar_donacion", data={
        "cantidad_donada": "450",
        "fecha_donacion": "2026-03-23"
    })
    
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess["donacion_exitosa"] is True

# =====================================================
# API 2 – POST agregar donación inválida
# =====================================================
def test_api_post_agregar_donacion_invalida(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"enfermero": True}
        sess["enfermero_usuario_obtenido"] = {"cedula_usuario": "123"}

    resp = client.post("/agregar_donacion", data={
        "cantidad_donada": "abc",
        "fecha_donacion": "2026-03-23"
    })
    
    assert resp.status_code == 200
    assert "número válido" in resp.data.decode("utf-8").lower()
