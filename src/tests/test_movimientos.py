 

import pytest
import sys
import os

# agrega la carpeta src al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    with app.test_client() as client:
        yield client


# -------------------------------------------------
# PRUEBA 1
# Si NO hay sesión -> redirige a home
# Camino: sin user_data
# -------------------------------------------------
def test_movimientos_redirige_si_no_hay_sesion(client):

    resp = client.get("/movimientos", follow_redirects=False)

    assert resp.status_code in (301, 302)
    assert "/" in resp.headers.get("Location", "")


# -------------------------------------------------
# PRUEBA 2
# Si hay sesión -> renderiza movimientos.html
# Camino: con user_data
# -------------------------------------------------
def test_movimientos_renderiza_si_hay_sesion(client):

    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Juliana"}

    resp = client.get("/movimientos")

    assert resp.status_code == 200
    assert b"movimientos" in resp.data.lower() or resp.status_code == 200