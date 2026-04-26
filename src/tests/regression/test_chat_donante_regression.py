import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# REGRESIÓN 1 – Flujo correcto completo
# =====================================================
def test_regresion_flujo_exitoso(client, monkeypatch):

    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    monkeypatch.setattr(app, "generate_response",
                        lambda *args, **kwargs: "ok")

    # ACT
    resp = client.post(
        "/chatbot_donante",
        json={"mensaje_ingresado": "Hola"},
        content_type="application/json"
    )

    # ASSERT
    assert resp.status_code == 200
    assert resp.is_json
    assert resp.get_json()["respuesta"] == "ok"


# =====================================================
# REGRESIÓN 2 – GET renderiza correctamente
# =====================================================
def test_regresion_get_render(client):

    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    # ACT
    resp = client.get("/chatbot_donante")

    # ASSERT
    assert resp.status_code == 200
    assert b"DONANTE" in resp.data


# =====================================================
# REGRESIÓN 3 – Redirección por rol incorrecto
# =====================================================
def test_regresion_redireccion_por_rol(client):

    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Luis", "donante": False}

    # ACT
    resp = client.get("/chatbot_donante", follow_redirects=False)

    # ASSERT
    assert resp.status_code in (301, 302)
    assert "/chatbot_solicitante" in resp.location


# =====================================================
# REGRESIÓN 4 – Mensaje vacío
# =====================================================
def test_regresion_mensaje_vacio(client):

    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    # ACT
    resp = client.post(
        "/chatbot_donante",
        json={"mensaje_ingresado": ""},
        content_type="application/json"
    )

    # ASSERT
    assert resp.status_code == 400


# =====================================================
# REGRESIÓN 5 – Sin JSON en POST
# =====================================================
def test_regresion_post_sin_json(client):

    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    # ACT
    resp = client.post("/chatbot_donante")

    # ASSERT
    assert resp.status_code == 400


# =====================================================
# REGRESIÓN 6 – Sin campo mensaje
# =====================================================
def test_regresion_sin_campo_mensaje(client):

    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    # ACT
    resp = client.post(
        "/chatbot_donante",
        json={},
        content_type="application/json"
    )

    # ASSERT
    assert resp.status_code == 400


# =====================================================
# REGRESIÓN 7 – Error de IA controlado
# =====================================================
def test_regresion_error_ia_controlado(client, monkeypatch):

    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    def fallo(*args, **kwargs):
        raise RuntimeError("IA caída")

    monkeypatch.setattr(app, "generate_response", fallo)


    # ACT
    resp = client.post(
        "/chatbot_donante",
        json={"mensaje_ingresado": "Hola"},
        content_type="application/json"
    )

    # ASSERT
    assert resp.status_code == 200
    assert "problemas técnicos" in resp.get_json()["respuesta"]


# =====================================================
# REGRESIÓN 8 – Mantiene estructura JSON
# =====================================================
def test_regresion_estructura_json(client, monkeypatch):

    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    monkeypatch.setattr(app, "generate_response",
                        lambda *args, **kwargs: "respuesta test")

    # ACT
    resp = client.post(
        "/chatbot_donante",
        json={"mensaje_ingresado": "Hola"},
        content_type="application/json"
    )

    data = resp.get_json()

    # ASSERT
    assert isinstance(data, dict)
    assert "respuesta" in data


# =====================================================
# REGRESIÓN 9 – Múltiples llamadas consistentes
# =====================================================
def test_regresion_consistencia(client, monkeypatch):

    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    monkeypatch.setattr(app, "generate_response",
                        lambda *args, **kwargs: "ok")

    # ACT + ASSERT
    for _ in range(10):
        resp = client.post(
            "/chatbot_donante",
            json={"mensaje_ingresado": "Hola"},
            content_type="application/json"
        )
        assert resp.status_code == 200
        assert resp.get_json()["respuesta"] == "ok"