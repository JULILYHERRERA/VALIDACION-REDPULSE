import pytest
import sys
import os
from app import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# REGRESSION 1 – Flujo normal de filtrado
# =====================================================
def test_regression_filtrar_solicitudes_flujo_normal(client, monkeypatch):
    """Verifica que el flujo de filtrado se mantenga estable."""
    import app as modulo
    
    # Mock de respuesta del servicio
    monkeypatch.setattr(modulo, "obtenerSolicitudesPendientesPorTipo", lambda t: [{"id": 1, "tipo": t}])

    resp = client.post("/filtrar_solicitudes", data={"tipo_sangre": "A+"})
    assert resp.status_code == 200
    assert b"A+" in resp.data

# =====================================================
# REGRESSION 2 – Normalización de tipos de sangre (Minúsculas)
# =====================================================
def test_regression_filtrar_solicitudes_normalizacion(client, monkeypatch):
    """Verifica que los tipos de sangre se normalicen a mayúsculas."""
    import app as modulo
    
    monkeypatch.setattr(modulo, "obtenerSolicitudesPendientesPorTipo", lambda t: [{"id": 1, "tipo": t}])

    resp = client.post("/filtrar_solicitudes", data={"tipo_sangre": "o-"})
    assert resp.status_code == 200
    assert b"O-" in resp.data
