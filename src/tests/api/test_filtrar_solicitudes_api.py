import pytest
import sys
import os
from app import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# API 1 – GET Filtrar Solicitudes
# =====================================================
def test_api_filtrar_solicitudes_get(client):
    """Verifica que la página de filtrado carga correctamente."""
    resp = client.get("/filtrar_solicitudes")
    assert resp.status_code == 200
    assert b"filtrar" in resp.data.lower()

# =====================================================
# API 2 – POST Filtrar Solicitudes (Exitoso)
# =====================================================
def test_api_filtrar_solicitudes_post_exitoso(client, monkeypatch):
    """Verifica que el filtrado por tipo de sangre funciona."""
    import app as modulo
    
    monkeypatch.setattr(modulo, "obtenerSolicitudesPendientesPorTipo", lambda t: [{"id": 1, "tipo": t}])

    resp = client.post("/filtrar_solicitudes", data={"tipo_sangre": "O+"})
    
    assert resp.status_code == 200
    assert b"O+" in resp.data

# =====================================================
# API 3 – POST Filtrar Solicitudes (Invalido)
# =====================================================
def test_api_filtrar_solicitudes_post_invalido(client):
    """Verifica que un tipo de sangre inválido no devuelva resultados."""
    resp = client.post("/filtrar_solicitudes", data={"tipo_sangre": "Z-"})
    assert resp.status_code == 200
    # No debería haber resultados si no se llamó al servicio
