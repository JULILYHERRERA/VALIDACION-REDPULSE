import pytest
import sys
import os

# Configuración de rutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    with app.test_client() as client:
        yield client

# ============================================
# PRUEBA 1 – Camino 1: Usuario NO es donante
# ============================================
def test_chatbot_donante_redirige_si_no_es_donante(client):
    with client.session_transaction() as sess:
        # Simulamos usuario que NO es donante
        sess["user_data"] = {"nombre": "Luis", "donante": False}

    resp = client.get("/chatbot_donante", follow_redirects=False)

    # Debe redirigir al chatbot de solicitante (Nodo 3 -> 9)
    assert resp.status_code in (301, 302)
    assert "/chatbot_solicitante" in resp.location

# ============================================
# PRUEBA 2 – Camino 2: Usuario donante abre el chat (GET)
# ============================================
def test_chatbot_donante_render_get(client):
    with client.session_transaction() as sess:
        # Simulamos usuario que SÍ es donante
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    resp = client.get("/chatbot_donante")

    # Nodo 4 -> 5: Debe cargar la página con el rol "DONANTE"
    assert resp.status_code == 200
    assert b"DONANTE" in resp.data

# ============================================
# PRUEBA 3 – Camino 3: Usuario envía mensaje (POST)
# ============================================
def test_chatbot_donante_envia_mensaje_post(client, monkeypatch):
    import app as modulo

    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    # Mock de la función generadora de IA para no gastar tokens/API real
    def mock_generate(mensaje, user_data, rol_forzado):
        return "Respuesta simulada de IA para donantes"

    monkeypatch.setattr(modulo, "generate_response", mock_generate)

    # Nodo 6 -> 7 -> 8: Enviamos mensaje JSON
    resp = client.post("/chatbot_donante", 
                       json={"mensaje_ingresado": "Hola chatbot"})

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["respuesta"] == "Respuesta simulada de IA para donantes"