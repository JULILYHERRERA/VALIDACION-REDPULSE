import pytest
import sys
import os
from app import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# API 1 – GET Movimientos autenticado
# =====================================================
def test_api_movimientos_get_autenticado(client):
    """Verifica que un usuario autenticado accede a movimientos."""
    with client.session_transaction() as sess:
        sess["user_data"] = {
            "nombre": "Test",
            "registros": [
                {
                    "TIPO_REGISTRO": "Donacion",
                    "FECHA": "2024-01-01",
                    "CANTIDAD": 450,
                    "PRIORIDAD": "Media",
                    "ESTADO": "Completada"
                }
            ]
        }

    resp = client.get("/movimientos")
    assert resp.status_code == 200
    assert b"historial" in resp.data.lower()

# =====================================================
# API 2 – GET Movimientos sin autenticación
# =====================================================
def test_api_movimientos_get_no_autenticado(client):
    """Verifica que un usuario no autenticado es redirigido."""
    resp = client.get("/movimientos", follow_redirects=False)
    assert resp.status_code in (301, 302)
    assert resp.headers.get("Location") in ("/", "http://localhost/")

# =====================================================
# API 3 – POST Movimientos autenticado
# =====================================================
def test_api_movimientos_post_autenticado(client):
    """Verifica que el POST también funciona cuando está autenticado."""
    with client.session_transaction() as sess:
        sess["user_data"] = {
            "nombre": "Test",
            "registros": [
                {
                    "TIPO_REGISTRO": "Donacion",
                    "FECHA": "2024-01-01",
                    "CANTIDAD": 450,
                    "PRIORIDAD": "Media",
                    "ESTADO": "Completada"
                }
            ]
        }

    resp = client.post("/movimientos")
    assert resp.status_code == 200
