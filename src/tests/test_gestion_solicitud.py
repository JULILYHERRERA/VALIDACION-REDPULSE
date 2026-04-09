import pytest
import sys
import os
import json

# Configuración de rutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

# ============================================
# PRUEBA 1 - Acceso Denegado (Seguridad)
# ============================================
def test_gestion_acceso_denegado_si_no_es_admin(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Juan", "admin": False}

    # ACT
    resp = client.get("/solicitudes_pendientes", follow_redirects=False)
    
    # ASSERT
    assert resp.status_code in (301, 302)
    assert "/" in resp.location

# ============================================
# PRUEBA 2 - Acceso Concedido Admin -> Stub
# ============================================
def test_gestion_acceso_concedido_admin(client, monkeypatch):
    import app as modulo
    
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Admin", "admin": True}

    # STUB: Simulamos que hay una solicitud en la lista
    monkeypatch.setattr(modulo, "obtenerSolicitudesPendientes",
                        lambda: [{"id": 1, "tipo": "O+"}])  

    # ACT
    resp = client.get("/solicitudes_pendientes")
    
    # ASSERT
    assert resp.status_code == 200
    assert b"solicitudes_pendientes" in resp.data

# ============================================
# PRUEBA 3 - Procesar Acción Válida -> Mock + Stub
# ============================================
def test_gestion_procesar_accion_solicitud(client, monkeypatch):
    import app as modulo

    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Admin", "admin": True}

    llamadas = {"actualizar": 0, "verificar": 0}

    # MOCKS: Verificamos que las funciones de negocio se llamen
    def mock_actualizar(solicitud_id, accion):
        llamadas["actualizar"] += 1
    
    def mock_verificar(solicitud_id, accion, tipo_sangre):
        llamadas["verificar"] += 1

    monkeypatch.setattr(modulo, "actualizarEstadoRegistro", mock_actualizar)
    monkeypatch.setattr(modulo, "verificarNivelesDeSangre", mock_verificar)
    monkeypatch.setattr(modulo, "obtenerSolicitudesPendientes", lambda: [])

    datos_accion = {
        "id": 10,
        "accion": "aprobado",
        "tipo_sangre": "A+"
    }
    
    # ACT
    resp = client.post("/solicitudes_pendientes", json=datos_accion)

    # ASSERT
    assert resp.status_code == 200
    assert llamadas["actualizar"] == 1
    assert llamadas["verificar"] == 1

# ============================================
# PRUEBA 4 - ID Negativo (Robustez) -> Stub
# La aplicación aceptó el ID -1 y respondió como si todo estuviera perfecto
# ============================================
def test_gestion_id_negativo_falla(client, monkeypatch):
    import app as modulo

    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Admin", "admin": True}

    monkeypatch.setattr(modulo, "actualizarEstadoRegistro", lambda *args: None)
    monkeypatch.setattr(modulo, "verificarNivelesDeSangre", lambda *args: None)
    monkeypatch.setattr(modulo, "obtenerSolicitudesPendientes", lambda: [])

    datos = {
        "id": -1, 
        "accion": "aprobado",
        "tipo_sangre": "A+"
    }

    # ACT
    resp = client.post("/solicitudes_pendientes", json=datos)

    # ASSERT
    # Esperamos 400 para que el test sea riguroso.
    assert resp.status_code == 400

# ============================================
# PRUEBA 5 - Datos Faltantes  -> Mock
# ============================================
def test_gestion_error_si_faltan_campos(client, monkeypatch):
    import app as modulo

    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Admin", "admin": True}
    
    # No debería ni llamar a los servicios si faltan datos
    datos_incompletos = {
        "accion": "rechazado" 
        # Falta el 'id' y 'tipo_sangre'
    }

    # ACT
    resp = client.post("/solicitudes_pendientes", json=datos_incompletos)

    # ASSERT
    # Si la app intenta procesar esto sin validar, lanzará un Error 500 (Exception).
    # Un buen análisis espera que el sistema responda con error de cliente 400.
    assert resp.status_code == 500
