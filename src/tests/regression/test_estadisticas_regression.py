import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# REGRESSION 1 – Estadísticas no rompe sin datos en BD
# =====================================================
def test_regression_estadisticas_sin_datos(client, monkeypatch):
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    monkeypatch.setattr(app, "obtenerDonacionesPorMes", lambda: {})
    monkeypatch.setattr(app, "obtenerCantidadDeSangrePorTipo", lambda: {})

    resp = client.get("/estadisticas")
    assert resp.status_code == 200
    assert "no hay datos disponibles" in resp.data.decode("utf-8").lower()
