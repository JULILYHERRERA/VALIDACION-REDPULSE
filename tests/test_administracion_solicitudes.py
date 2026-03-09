import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from app import app


@pytest.fixture
def client():
    # Cliente de prueba que simula un usuario usando la web
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    with app.test_client() as client:
        yield client


# ============================================================
# CAMINO 1
# Usuario NO admin intenta entrar a la página
# El sistema lo bloquea y lo manda al home

def test_camino1_redirect_si_no_hay_sesion_o_no_admin(client):

    # Simulamos un usuario que NO es admin
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Juan", "admin": False}

    # El usuario intenta entrar a la página
    resp = client.get("/solicitudes_pendientes")

    # Verificamos que el sistema lo redirige
    assert resp.status_code in (301, 302)
    assert "/" in resp.location


# ============================================================
# CAMINO 2
# Usuario NO admin intenta enviar una acción (POST)
# Igual debe ser bloqueado

def test_camino2_redirect_si_no_admin_aun_si_intenta_post(client):

    # Simulamos usuario no admin
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Pedro", "admin": False}

    # Intenta enviar una acción
    resp = client.post(
        "/solicitudes_pendientes",
        json={"id": -1, "accion": "rechazado", "tipo_sangre": "O+"}
    )

    # El sistema debe bloquearlo igual
    assert resp.status_code in (301, 302)
    assert "/" in resp.location


# ============================================================
# CAMINO 3
# Admin entra a ver la página
# Solo muestra la tabla (no procesa nada)
def test_camino3_admin_get_renderiza_tabla(client, monkeypatch):

    import app as modulo

    # Simulamos que el usuario es admin
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Admin", "admin": True}

    # Simulamos datos de solicitudes
    monkeypatch.setattr(modulo, "obtenerSolicitudesPendientes",
                        lambda: [{"id": 1, "tipo": "O+"}])

    # El admin entra a la página
    resp = client.get("/solicitudes_pendientes")

    # Verificamos que la página carga bien
    assert resp.status_code == 200
    assert b"solicitudes_pendientes" in resp.data


# ============================================================
# CAMINO 4
# Admin envía una acción (aprobar o rechazar)

def test_camino4_admin_post_procesa_accion_y_renderiza(client, monkeypatch):

    import app as modulo

    # Simulamos usuario admin
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Admin", "admin": True}

    # Variables para comprobar que se ejecutan las funciones
    llamadas = {"actualizar": 0, "verificar": 0}

    # Función falsa que cuenta cuántas veces se llama
    def mock_actualizar(solicitud_id, accion):
        llamadas["actualizar"] += 1

    def mock_verificar(solicitud_id, accion, tipo_sangre):
        llamadas["verificar"] += 1

    # Reemplazamos las funciones reales por estas falsas
    monkeypatch.setattr(modulo, "actualizarEstadoRegistro", mock_actualizar)
    monkeypatch.setattr(modulo, "verificarNivelesDeSangre", mock_verificar)
    monkeypatch.setattr(modulo, "obtenerSolicitudesPendientes", lambda: [])

    # Simulamos que el admin aprueba una solicitud
    datos_accion = {
        "id": 10,
        "accion": "aprobado",
        "tipo_sangre": "A+"
    }

    resp = client.post("/solicitudes_pendientes", json=datos_accion)

    # Verificamos que se ejecutaron las funciones
    assert resp.status_code == 200
    assert llamadas["actualizar"] == 1
    assert llamadas["verificar"] == 1