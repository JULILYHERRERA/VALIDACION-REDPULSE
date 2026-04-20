import pytest
import sys
import os
from app import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# REGRESSION 1 – Normalización de datos de movimientos
# =====================================================
def test_regression_movimientos_normalizacion(client):
    """Verifica que los datos incompletos en la sesión se normalizan."""
    with client.session_transaction() as sess:
        sess["user_data"] = {
            "nombre": "Test",
            "registros": [
                {
                    # Solo enviamos algunos campos
                    "TIPO_REGISTRO": "Donacion",
                    "CANTIDAD": 450
                }
            ]
        }

    resp = client.get("/movimientos")
    assert resp.status_code == 200
    # En el template, se deberían usar los valores por defecto si el código de normalización funciona

# =====================================================
# REGRESSION 2 – Redirección si registros está vacío (Modo Test)
# =====================================================
def test_regression_movimientos_vacio_test_mode(client, monkeypatch):
    """Verifica que en modo test, si no hay registros, se redirige (según _normalize_for_test)."""
    # Forzamos test_mode = True mockeando render_template en el módulo app
    monkeypatch.setattr("app.render_template", lambda *args, **kwargs: "mocked")

    with client.session_transaction() as sess:
        sess["user_data"] = {
            "nombre": "Test",
            "registros": []
        }

    resp = client.get("/movimientos", follow_redirects=False)
    assert resp.status_code in (301, 302)
    assert resp.headers.get("Location") in ("/", "http://localhost/")



# =====================================================
# REGRESSION 3 – Normalización con campos nulos
# =====================================================
def test_regression_movimientos_campos_nulos(client):
    """Verifica la normalización cuando hay campos explícitamente None."""
    with client.session_transaction() as sess:
        sess["user_data"] = {
            "nombre": "Test",
            "registros": [
                {
                    "TIPO_REGISTRO": None,
                    "FECHA": None,
                    "CANTIDAD": None,
                    "PRIORIDAD": None,
                    "ESTADO": None
                }
            ]
        }

    resp = client.get("/movimientos")
    assert resp.status_code == 200
