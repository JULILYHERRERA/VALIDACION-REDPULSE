import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# API 1 – GET sin sesión → redirige
# =====================================================
def test_api_sin_sesion(client):

    resp = client.get("/asignar_puntos", follow_redirects=False)

    assert resp.status_code in (301, 302)


# =====================================================
# API 2 – GET con rol incorrecto → redirige
# =====================================================
def test_api_no_enfermero(client):

    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "enfermero": False}

    resp = client.get("/asignar_puntos", follow_redirects=False)

    assert resp.status_code in (301, 302)


# =====================================================
# API 3 – GET correcto → renderiza
# =====================================================
def test_api_get_render(client):

    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "enfermero": True}

    resp = client.get("/asignar_puntos")

    assert resp.status_code == 200


# =====================================================
# API 4 – POST exitoso
# =====================================================
def test_api_post_exitoso(client, monkeypatch):

    class UsuarioFake:
        puntos = 100

    monkeypatch.setattr(app, "obtenerUsuarioPorDocumento",
                        lambda d, t: UsuarioFake())

    llamadas = {"update": 0}
    def mock_update(d, t, p):
        llamadas["update"] += 1

    monkeypatch.setattr(app, "actualizarPuntos", mock_update)

    with client.session_transaction() as sess:
        sess["user_data"] = {"enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "111",
            "tipo_cedula_usuario": "CC"
        }

    resp = client.post("/asignar_puntos", data={"puntos": "50"})

    assert resp.status_code in (301, 302)
    assert llamadas["update"] == 1


# =====================================================
# API 5 – POST sin puntos
# =====================================================
def test_api_post_sin_puntos(client):

    with client.session_transaction() as sess:
        sess["user_data"] = {"enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "111",
            "tipo_cedula_usuario": "CC"
        }

    resp = client.post("/asignar_puntos", data={})

    assert resp.status_code == 200