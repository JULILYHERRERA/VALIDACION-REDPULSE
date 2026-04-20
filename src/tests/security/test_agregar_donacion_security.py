import pytest
import sys
import os
from app import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# SEGURIDAD 1 – Acceso sin ser enfermero
# =====================================================
def test_security_agregar_donacion_sin_enfermero(client):
    """Verifica que el acceso sin rol de enfermero sea denegado."""
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Donante", "enfermero": False}

    resp = client.get("/agregar_donacion", follow_redirects=False)
    assert resp.status_code in (301, 302)

# =====================================================
# SEGURIDAD 2 – Sin usuario objetivo seleccionado
# =====================================================
def test_security_agregar_donacion_sin_objetivo(client):
    """Verifica que si no hay usuario objetivo, se redirija a /enfermero."""
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Enfermero", "enfermero": True}
        # Sin sess["enfermero_usuario_obtenido"]

    resp = client.get("/agregar_donacion", follow_redirects=False)
    assert resp.status_code in (301, 302)
    assert "/enfermero" in resp.headers.get("Location", "")

# =====================================================
# SEGURIDAD 3 – Cantidad de sangre no numérica
# =====================================================
def test_security_agregar_donacion_cantidad_invalida(client):
    """Verifica que si la cantidad no es numérica, se maneje el error."""
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Enfermero", "enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "123",
            "tipo_cedula_usuario": "Cedula"
        }

    resp = client.post("/agregar_donacion", data={
        "cantidad_donada": "NoSoyNumero",
        "fecha_donacion": "2024-01-01"
    })
    
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert "número válido" in sess.get("mensaje_validacion_donacion").lower()
