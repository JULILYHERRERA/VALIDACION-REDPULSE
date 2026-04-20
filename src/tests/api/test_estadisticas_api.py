import pytest
import sys
import os
import app
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# API 1 – GET estadísticas admin
# =====================================================
def test_api_get_estadisticas_admin(client, monkeypatch):
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    monkeypatch.setattr(app, "obtenerDonacionesPorMes", lambda: {"Enero": 10})
    monkeypatch.setattr(app, "obtenerCantidadDeSangrePorTipo", lambda: {"O+": 5000})

    resp = client.get("/estadisticas")
    assert resp.status_code == 200
    assert b"Enero" in resp.data
    assert b"O+" in resp.data

# =====================================================
# API 2 – GET estadísticas sin permisos
# =====================================================
def test_api_get_estadisticas_no_admin(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": False}

    resp = client.get("/estadisticas", follow_redirects=False)
    assert resp.status_code in (301, 302)
