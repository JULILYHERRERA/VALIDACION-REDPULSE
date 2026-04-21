import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as modulo
from app import app

# =====================================================
# PRUEBA 1 – Sin sesión redirige a login
# =====================================================
def test_prueba1_sin_sesion_redirige_a_login(client):
    # ARRANGE

    # ACT
    resp = client.get("/chatbot_solicitante", follow_redirects=False)

    # ASSERT
    assert resp.status_code in (301, 302)
    assert "/login" in resp.headers.get("Location", "")

# =====================================================
# PRUEBA 2 – Donante redirige a chatbot_donante
# =====================================================
def test_prueba2_donante_redirige_a_chatbot_donante(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"donante": True}

    # ACT
    resp = client.get("/chatbot_solicitante", follow_redirects=False)

    # ASSERT
    assert resp.status_code in (301, 302)
    assert resp.headers.get("Location") is not None

# =====================================================
# PRUEBA 3 – GET de solicitante renderiza chat
# STUB
# =====================================================
def test_prueba3_get_solicitante_renderiza_chat(client, monkeypatch):
    # ARRANGE
    contexto = {}

    def fake_render(template_name, **kwargs):
        contexto["template"] = template_name
        contexto["user_data"] = kwargs.get("user_data")
        contexto["rol_chat"] = kwargs.get("rol_chat")
        return "render ok"

    monkeypatch.setattr(modulo, "render_template", fake_render)

    with client.session_transaction() as sess:
        sess["user_data"] = {"donante": False, "nombre": "Juliana"}

    # ACT
    resp = client.get("/chatbot_solicitante")

    # ASSERT
    assert resp.status_code == 200
    assert contexto["template"] == "chatbot.html"
    assert contexto["rol_chat"] == "SOLICITANTE"
    assert contexto["user_data"]["nombre"] == "Juliana"

# =====================================================
# PRUEBA 4 – POST válido genera respuesta
# STUB + SPY
# =====================================================
def test_prueba4_post_valido_genera_respuesta(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_generate_response(mensaje, user_data, rol_forzado=None):
        llamadas.append((mensaje, user_data, rol_forzado))
        return "RESPUESTA_MOCK"

    monkeypatch.setattr(modulo, "generate_response", fake_generate_response)

    with client.session_transaction() as sess:
        sess["user_data"] = {"donante": False, "nombre": "Juliana"}

    # ACT
    resp = client.post(
        "/chatbot_solicitante",
        json={"mensaje_ingresado": "Hola"}
    )

    # ASSERT
    assert resp.status_code == 200
    assert resp.is_json
    assert llamadas[0][0] == "Hola"
    assert llamadas[0][2] == "SOLICITANTE"
    assert resp.get_json() == {"respuesta": "RESPUESTA_MOCK"}

# =====================================================
# PRUEBA 5 – POST sin JSON debería manejarse
# FALLA
# =====================================================
def test_prueba5_post_sin_json_deberia_manejarse(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"donante": False, "nombre": "Juliana"}

    # ACT
    resp = client.post("/chatbot_solicitante")

    # ASSERT
    assert resp.status_code == 200

# =====================================================
# PRUEBA 6 – POST sin mensaje no debería procesarse
# SPY (FALLA)
# =====================================================
def test_prueba6_post_sin_mensaje_no_deberia_procesarse(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_generate_response(mensaje, user_data, rol_forzado=None):
        llamadas.append((mensaje, user_data, rol_forzado))
        return "RESPUESTA_MOCK"

    monkeypatch.setattr(modulo, "generate_response", fake_generate_response)

    with client.session_transaction() as sess:
        sess["user_data"] = {"donante": False, "nombre": "Juliana"}

    # ACT
    resp = client.post(
        "/chatbot_solicitante",
        json={}
    )

    # ASSERT
    assert resp.status_code == 200
    assert llamadas == []