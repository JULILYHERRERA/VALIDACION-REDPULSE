import pytest
import sys
import os

# Configuración de rutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    with app.test_client() as client:
        yield client

# ============================================
# PRUEBA 1 - Camino 1: Usuario no es Admin
# ============================================
def test_gestion_acceso_denegado_si_no_es_admin(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Juan", "admin": False} # No es admin

    resp = client.get("/solicitudes_pendientes", follow_redirects=False)
    
    # Debe redirigir al home (Bloqueo de seguridad)
    assert resp.status_code in (301, 302)
    assert "/" in resp.location

# ============================================
# PRUEBA 2 - Camino 2: Admin entra a ver la tabla
# ============================================
def test_gestion_acceso_concedido_admin(client, monkeypatch):
    import app as modulo
    
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Admin", "admin": True}

    # Simulamos que hay solicitudes en la base de datos
    monkeypatch.setattr(modulo, "obtenerSolicitudesPendientes", lambda: [{"id": 1, "tipo": "O+"}])

    resp = client.get("/solicitudes_pendientes")
    
    assert resp.status_code == 200
    # Debe salir la tabla de solicitudes
    assert b"solicitudes_pendientes" in resp.data

# ============================================
# PRUEBA 3 - Camino 3: Procesa Aprobación/Rechazo
# ============================================
def test_gestion_procesar_accion_solicitud(client, monkeypatch):
    import app as modulo

    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Admin", "admin": True}

    # Mocks para las funciones de actualización
    llamadas = {"actualizar": 0, "verificar": 0}

    def mock_actualizar(solicitud_id, accion):
        llamadas["actualizar"] += 1
    
    def mock_verificar(solicitud_id, accion, tipo_sangre):
        llamadas["verificar"] += 1

    monkeypatch.setattr(modulo, "actualizarEstadoRegistro", mock_actualizar)
    monkeypatch.setattr(modulo, "verificarNivelesDeSangre", mock_verificar)
    monkeypatch.setattr(modulo, "obtenerSolicitudesPendientes", lambda: [])

    # Enviamos la acción vía POST (JSON)
    datos_accion = {
        "id": 10,
        "accion": "aprobado",
        "tipo_sangre": "A+"
    }
    
    resp = client.post("/solicitudes_pendientes", json=datos_accion)

    assert resp.status_code == 200
    # Verificamos que se ejecutaron las acciones de cambio de estado y stock
    assert llamadas["actualizar"] == 1
    assert llamadas["verificar"] == 1