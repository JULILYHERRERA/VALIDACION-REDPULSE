import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# REGRESIÓN 1 – GET funciona correctamente
# =====================================================
def test_regresion_get_render(client):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"enfermero": True}

    # ======================= ACT =======================
    resp = client.get("/asignar_puntos")

    # ====================== ASSERT =====================
    assert resp.status_code == 200


# =====================================================
# REGRESIÓN 2 – POST suma puntos correctamente
# =====================================================
def test_regresion_suma_puntos(client, monkeypatch):

    # ===================== ARRANGE =====================
    class UsuarioFake:
        puntos = 100

    monkeypatch.setattr(app, "obtenerUsuarioPorDocumento",
                        lambda d, t: UsuarioFake())

    resultado = {"nuevo": None}
    def mock_actualizar(doc, tipo, nuevos):
        resultado["nuevo"] = nuevos

    monkeypatch.setattr(app, "actualizarPuntos", mock_actualizar)

    with client.session_transaction() as sess:
        sess["user_data"] = {"enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "111",
            "tipo_cedula_usuario": "CC"
        }

    # ======================= ACT =======================
    resp = client.post("/asignar_puntos", data={"puntos": "50"})

    # ====================== ASSERT =====================
    assert resp.status_code in (301, 302)
    assert resultado["nuevo"] == 150


# =====================================================
# REGRESIÓN 3 – POST redirige correctamente
# =====================================================
def test_regresion_redireccion(client, monkeypatch):

    # ===================== ARRANGE =====================
    class UsuarioFake:
        puntos = 100

    monkeypatch.setattr(app, "obtenerUsuarioPorDocumento",
                        lambda d, t: UsuarioFake())
    monkeypatch.setattr(app, "actualizarPuntos", lambda *a: None)

    with client.session_transaction() as sess:
        sess["user_data"] = {"enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "111",
            "tipo_cedula_usuario": "CC"
        }

    # ======================= ACT =======================
    resp = client.post("/asignar_puntos", data={"puntos": "10"}, follow_redirects=False)

    # ====================== ASSERT =====================
    assert resp.status_code in (301, 302)
    assert resp.headers.get("Location") is not None


# =====================================================
# REGRESIÓN 4 – POST sin puntos mantiene render
# =====================================================
def test_regresion_post_sin_puntos(client):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "111",
            "tipo_cedula_usuario": "CC"
        }

    # ======================= ACT =======================
    resp = client.post("/asignar_puntos", data={})

    # ====================== ASSERT =====================
    assert resp.status_code == 200


# =====================================================
# REGRESIÓN 5 – Mantiene comportamiento con puntos = 0
# =====================================================
def test_regresion_puntos_cero(client, monkeypatch):

    # ===================== ARRANGE =====================
    class UsuarioFake:
        puntos = 100

    monkeypatch.setattr(app, "obtenerUsuarioPorDocumento",
                        lambda d, t: UsuarioFake())

    resultado = {"nuevo": None}
    def mock_actualizar(doc, tipo, nuevos):
        resultado["nuevo"] = nuevos

    monkeypatch.setattr(app, "actualizarPuntos", mock_actualizar)

    with client.session_transaction() as sess:
        sess["user_data"] = {"enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "111",
            "tipo_cedula_usuario": "CC"
        }

    # ======================= ACT =======================
    resp = client.post("/asignar_puntos", data={"puntos": "0"})

    # ====================== ASSERT =====================
    assert resp.status_code in (301, 302)
    assert resultado["nuevo"] == 100