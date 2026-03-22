

import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    with app.test_client() as client:
        yield client


# PRUEBA 1
# Usuario sin sesión -> redirige a inicio
def test_puntos_redirige_si_no_hay_sesion(client):

    resp = client.get("/puntos", follow_redirects=False)

    assert resp.status_code in (301, 302)
    assert "/" in resp.headers.get("Location", "")


# PRUEBA 2
# Usuario con sesión -> renderiza vista puntos
def test_puntos_renderiza_si_hay_sesion(client):

    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Juliana", "puntos": 2000}

    resp = client.get("/puntos")

    assert resp.status_code == 200