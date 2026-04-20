import pytest
import sys
import os
from app import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# API 1 – GET Agregar Donación (Enfermero autenticado)
# =====================================================
def test_api_agregar_donacion_get_enfermero(client):
    """Verifica que un enfermero con usuario objetivo accede a la vista."""
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Enfermero", "enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "123",
            "tipo_cedula_usuario": "Cedula"
        }

    resp = client.get("/agregar_donacion")
    assert resp.status_code == 200
    assert b"agregar" in resp.data.lower()

# =====================================================
# API 2 – GET Agregar Donación (No enfermero)
# =====================================================
def test_api_agregar_donacion_get_no_enfermero(client):
    """Verifica que un usuario no enfermero es redirigido."""
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Donante", "enfermero": False}

    resp = client.get("/agregar_donacion", follow_redirects=False)
    assert resp.status_code in (301, 302)

# =====================================================
# API 3 – POST Agregar Donación (Exitoso)
# =====================================================
def test_api_agregar_donacion_post_exitoso(client, monkeypatch):
    """Verifica que el registro de una donación funciona correctamente."""
    import app as modulo
    
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Enfermero", "enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "123",
            "tipo_cedula_usuario": "Cedula"
        }

    monkeypatch.setattr(modulo, "insertarDonacion", lambda doc, tip, fec, can: True)

    resp = client.post("/agregar_donacion", data={
        "cantidad_donada": "450",
        "fecha_donacion": "2024-01-01"
    })
    
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess.get("donacion_exitosa") is True

# =====================================================
# API 4 – POST Agregar Donación (Faltan campos)
# =====================================================
def test_api_agregar_donacion_post_faltante(client):
    """Verifica que el error cuando faltan campos se maneje en sesión."""
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Enfermero", "enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "123",
            "tipo_cedula_usuario": "Cedula"
        }

    resp = client.post("/agregar_donacion", data={
        "cantidad_donada": "",
        "fecha_donacion": ""
    })
    
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert "obligatorios" in sess.get("mensaje_validacion_donacion").lower()
