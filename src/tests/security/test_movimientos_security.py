import pytest
import sys
import os
from app import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# SEGURIDAD 1 – Acceso sin sesión
# =====================================================
def test_security_movimientos_sin_sesion(client):
    """Verifica que el acceso sin sesión sea denegado."""
    resp = client.get("/movimientos", follow_redirects=False)
    assert resp.status_code in (301, 302)

# =====================================================
# SEGURIDAD 2 – Datos de sesión corruptos (Tipo incorrecto)
# =====================================================
def test_security_movimientos_datos_corruptos_tipo(client, monkeypatch):
    """Verifica que si user_data no es un dict, se maneja correctamente."""
    monkeypatch.setattr("app.render_template", lambda *args, **kwargs: "mocked")

    with client.session_transaction() as sess:
        sess["user_data"] = "Not a dict"

    resp = client.get("/movimientos", follow_redirects=False)
    assert resp.status_code in (301, 302)

# =====================================================
# SEGURIDAD 3 – Datos de sesión corruptos (Registros no es lista)
# =====================================================
def test_security_movimientos_datos_corruptos_registros(client, monkeypatch):
    """Verifica que si registros no es una lista, se maneja correctamente."""
    monkeypatch.setattr("app.render_template", lambda *args, **kwargs: "mocked")

    with client.session_transaction() as sess:
        sess["user_data"] = {
            "nombre": "Test",
            "registros": "Not a list"
        }

    resp = client.get("/movimientos", follow_redirects=False)
    assert resp.status_code in (301, 302)

# =====================================================
# SEGURIDAD 4 – Registro individual corrupto
# =====================================================
def test_security_movimientos_registro_individual_corrupto(client, monkeypatch):
    """Verifica que si un registro no es un dict, se omite o maneja."""
    monkeypatch.setattr("app.render_template", lambda *args, **kwargs: "mocked")

    with client.session_transaction() as sess:
        sess["user_data"] = {
            "nombre": "Test",
            "registros": ["Not a dict"]
        }

    resp = client.get("/movimientos", follow_redirects=False)
    assert resp.status_code in (301, 302) # En modo test _normalize_for_test redirige si falla


