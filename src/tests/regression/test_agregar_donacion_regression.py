import pytest
import sys
import os
from app import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# REGRESSION 1 – Flujo normal de agregar donación
# =====================================================
def test_regression_agregar_donacion_flujo_normal(client, monkeypatch):
    """Verifica que el flujo de agregar donación se mantenga estable."""
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
# REGRESSION 2 – Limpieza de mensajes de validación
# =====================================================
def test_regression_agregar_donacion_limpieza_mensajes(client, monkeypatch):
    """Verifica que los mensajes de validación se limpien al tener éxito."""
    import app as modulo
    
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Enfermero", "enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "123",
            "tipo_cedula_usuario": "Cedula"
        }
        sess["mensaje_validacion_donacion"] = "Mensaje previo"

    monkeypatch.setattr(modulo, "insertarDonacion", lambda doc, tip, fec, can: True)

    client.post("/agregar_donacion", data={
        "cantidad_donada": "450",
        "fecha_donacion": "2024-01-01"
    })
    
    with client.session_transaction() as sess:
        assert sess.get("mensaje_validacion_donacion") is None
