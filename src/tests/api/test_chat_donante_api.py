import pytest
import sys
import os
import app  

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# API 1 – GET renderiza correctamente
# =====================================================
def test_api_chatbot_get_ok(client):

    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    # ACT
    resp = client.get("/chatbot_donante")

    # ASSERT
    assert resp.status_code == 200
    assert b"DONANTE" in resp.data


# =====================================================
# API 2 – POST retorna JSON válido
# =====================================================
def test_api_chatbot_post_json(client, monkeypatch):

    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    monkeypatch.setattr(app, "generate_response",
                        lambda *args, **kwargs: "respuesta test")

    # ACT
    resp = client.post(
        "/chatbot_donante",
        json={"mensaje_ingresado": "Hola"},
        content_type="application/json"  # 🔥 clave
    )

    # ASSERT
    assert resp.status_code == 200
    assert resp.is_json
    assert resp.get_json()["respuesta"] == "respuesta test"


# =====================================================
# API 3 – POST maneja error de IA
# =====================================================
def test_api_chatbot_error_ia(client, monkeypatch):

    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    def fallo(*args, **kwargs):
        raise Exception("IA caída")

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
# API 4 – POST sin JSON
# =====================================================
def test_api_chatbot_sin_json(client):

    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    # ACT
    resp = client.post("/chatbot_donante")

    # ASSERT
    assert resp.status_code == 400


# =====================================================
# API 5 – POST mensaje vacío
# =====================================================
def test_api_chatbot_mensaje_vacio(client):

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
# API 6 – Redirección si no es donante
# =====================================================
def test_api_chatbot_redireccion_rol(client):

    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Luis", "donante": False}

    # ACT
    resp = client.get("/chatbot_donante", follow_redirects=False)

    # ASSERT
    assert resp.status_code in (301, 302)
    assert "/chatbot_solicitante" in resp.location


# =====================================================
# API 7 – POST con input malicioso
# =====================================================
def test_api_chatbot_input_malicioso(client, monkeypatch):

    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    monkeypatch.setattr(app, "generate_response",
                        lambda *args, **kwargs: "ok")

    # ACT
    resp = client.post(
        "/chatbot_donante",
        json={"mensaje_ingresado": "' OR 1=1 --"},
        content_type="application/json"
    )

    # ASSERT
    assert resp.status_code == 200
    assert resp.get_json()["respuesta"] == "ok"


# =====================================================
# API 8 – POST sin campo mensaje
# =====================================================
def test_api_chatbot_sin_campo_mensaje(client):

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
# API 9 – Estructura JSON
# =====================================================
def test_api_chatbot_estructura_json(client, monkeypatch):

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