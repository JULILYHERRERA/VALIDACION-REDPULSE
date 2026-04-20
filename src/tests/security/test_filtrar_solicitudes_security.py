import pytest
import sys
import os
from app import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# SEGURIDAD 1 – Intento de inyección SQL en filtrado
# =====================================================
def test_security_filtrar_solicitudes_inyeccion_sql(client):
    """Verifica que un intento de inyección SQL se maneje correctamente."""
    # El código valida contra un set de tipos válidos, así que debería ignorar esto
    resp = client.post("/filtrar_solicitudes", data={"tipo_sangre": "O+ OR 1=1"})
    assert resp.status_code == 200
    # No debería haber resultados porque no coincide con los tipos válidos

# =====================================================
# SEGURIDAD 2 – Campos vacíos o None
# =====================================================
def test_security_filtrar_solicitudes_campos_vacios(client):
    """Verifica que el filtrado con campos vacíos no rompa la aplicación."""
    resp = client.post("/filtrar_solicitudes", data={"tipo_sangre": ""})
    assert resp.status_code == 200

# =====================================================
# SEGURIDAD 3 – Tipo de dato inesperado (POST normal)
# =====================================================
def test_security_filtrar_solicitudes_tipo_dato_inesperado(client):
    """Verifica el manejo de tipos de datos no string."""
    # Flask form data siempre es string, pero simulamos el comportamiento
    resp = client.post("/filtrar_solicitudes", data={"tipo_sangre": None})
    assert resp.status_code == 200
