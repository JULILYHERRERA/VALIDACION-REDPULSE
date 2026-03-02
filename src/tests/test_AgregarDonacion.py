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
# Sin sesión o sin rol enfermero -> redirige a home
def test_agregar_donacion_redirige_si_no_es_enfermero(client):
    # Caso A: sin user_data
    resp = client.get("/agregar_donacion", follow_redirects=False)
    assert resp.status_code in (301, 302)
    assert "/" in resp.headers.get("Location", "")


# PRUEBA 2
# Con sesión enfermero + GET -> renderiza vista y reinicia verificación a None
def test_agregar_donacion_get_renderiza_y_reinicia_bandera(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Juliana", "enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "123",
            "tipo_cedula_usuario": "Cedula de Ciudadania"
        }
        sess["enfermero_usuario_verificacion"] = True  # para ver que lo reinicia

    resp = client.get("/agregar_donacion")
    assert resp.status_code == 200

    with client.session_transaction() as sess:
        assert sess["enfermero_usuario_verificacion"] is None


# PRUEBA 3
# Con sesión enfermero + POST -> inserta donación y guarda donacion_exitosa en sesión
def test_agregar_donacion_post_guarda_resultado(client, monkeypatch):
    import app as modulo

    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Juliana", "enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "123",
            "tipo_cedula_usuario": "Cedula de Ciudadania"
        }

    # Mock insertarDonacion para no tocar BD
    monkeypatch.setattr(modulo, "insertarDonacion", lambda doc, tipo, fecha, cantidad: True)

    resp = client.post("/agregar_donacion", data={
        "cantidad_donada": "500",
        "fecha_donacion": "2026-03-02"
    })

    assert resp.status_code == 200

    with client.session_transaction() as sess:
        assert sess["donacion_exitosa"] is True