import pytest
import sys
import os

# agrega la carpeta src al path (igual que tus pruebas)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    with app.test_client() as client:
        yield client


# -----------------------------
# PRUEBA 1 (Camino 1):
# Usuario NO es solicitante (es donante) -> redirige a chatbot_donante
# Secuencia esperada: 1-2-3-9
# -----------------------------
def test_chatbot_solicitante_redirige_si_es_donante(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"donante": True}

    resp = client.get("/chatbot_solicitante", follow_redirects=False)

    assert resp.status_code in (301, 302)
    # No asumimos el path exacto, pero sí que redirige
    assert resp.headers.get("Location") is not None
    # Si quieres hacerlo más específico:
    # assert "chatbot_donante" in resp.headers.get("Location", "")


# -----------------------------
# PRUEBA 2 (Camino 2):
# Usuario solicitante y solo abre el chat (GET) -> renderiza chatbot.html
# Secuencia: 1-2-3-4-5-9
# -----------------------------
def test_chatbot_solicitante_get_renderiza_chat(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"donante": False, "nombre": "Juliana"}

    resp = client.get("/chatbot_solicitante")

    assert resp.status_code == 200
    # Validación suave: que retorne HTML
    assert b"html" in resp.data.lower() or b"chat" in resp.data.lower()


# -----------------------------
# PRUEBA 3 (Camino 3):
# Usuario solicitante envía mensaje (POST JSON) -> devuelve respuesta generada
# Secuencia: 1-2-3-4-6-7-8-9
# -----------------------------
def test_chatbot_solicitante_post_genera_respuesta(client, monkeypatch):
    import app as modulo

    with client.session_transaction() as sess:
        sess["user_data"] = {"donante": False, "nombre": "Juliana"}

    # Mock de generate_response para que sea unitario y no llame IA real
    def mock_generate_response(mensaje, user_data, rol_forzado=None):
        return f"RESPUESTA_MOCK: {mensaje} | rol={rol_forzado}"

    monkeypatch.setattr(modulo, "generate_response", mock_generate_response)

    resp = client.post(
        "/chatbot_solicitante",
        json={"mensaje_ingresado": "Hola"},
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert "respuesta" in data
    assert "RESPUESTA_MOCK: Hola" in data["respuesta"]
    assert "rol=SOLICITANTE" in data["respuesta"]




# Test de roburtez para verificar un bug real en el codigo
# sabemos que para verificar el usuario es solciitante , mira di donante es == True 
# pero si es None?

# -----------------------------
# PRUEBA EXTRA DE ROBUSTEZ:
# Si no hay user_data en sesión, el endpoint explota
# -----------------------------
def test_chatbot_solicitante_sin_sesion_explota(client):
    # No seteamos session["user_data"]
    resp = client.get("/chatbot_solicitante", follow_redirects=False)
    # Ahora debe redirigir a login
    assert resp.status_code == 302
    assert "/login" in resp.headers.get("Location", "")