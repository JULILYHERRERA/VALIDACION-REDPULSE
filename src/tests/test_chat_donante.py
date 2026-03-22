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

# ============================================
# PRUEBA 1 – Redirección por Rol Incorrecto -> Stub
# ============================================
def test_chatbot_donante_redirige_si_no_es_donante(client):
    # ARRANGE
    with client.session_transaction() as sess:
        # Simulamos usuario que intenta entrar al chat de donantes siendo solicitante
        sess["user_data"] = {"nombre": "Luis", "donante": False}

    # ACT
    resp = client.get("/chatbot_donante", follow_redirects=False)

    # ASSERT
    # Verificamos que el sistema proteja el acceso (Nodo 3 -> 9)
    assert resp.status_code in (301, 302)
    assert "/chatbot_solicitante" in resp.location


# ============================================
# PRUEBA 2 – Acceso Correcto (GET)  -> Stub
# ============================================
def test_chatbot_donante_render_get(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    # ACT
    resp = client.get("/chatbot_donante")

    # ASSERT
    # Nodo 4 -> 5: Verificamos renderizado correcto
    assert resp.status_code == 200
    assert b"DONANTE" in resp.data


# ============================================
# PRUEBA 3 – Envío de Mensaje Exitoso -> MOCK
# ============================================
def test_chatbot_donante_envia_mensaje_post(client, monkeypatch):
    import app as modulo

    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}


    def mock_generate(mensaje, user_data, rol_forzado):
        return "Respuesta simulada de IA para donantes"

    monkeypatch.setattr(modulo, "generate_response", mock_generate)

    # ACT
    resp = client.post("/chatbot_donante", 
                       json={"mensaje_ingresado": "Hola chatbot"})

    # ASSERT
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["respuesta"] == "Respuesta simulada de IA para donantes"

# ============================================
# PRUEBA 4 – Mensaje vacio -> Stub
#chatbot no está validando si el mensaje tiene contenido
# ============================================
def test_chatbot_mensaje_vacio(client, monkeypatch):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}
    
    # ACT: Enviamos un string vacío
    resp = client.post("/chatbot_donante", json={"mensaje_ingresado": ""})
    
    # ASSERT: 
    assert resp.status_code == 400

# ============================================
# PRUEBA 5 – Error en la API de IA -> Mock
# ============================================
def test_chatbot_error_ia(client, monkeypatch):
    import app as modulo
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    # CORRECCIÓN: Agregamos **kwargs para capturar 'rol_forzado'
    def mock_fallo(*args, **kwargs):
        raise Exception("Servicio de IA no disponible")
    
    monkeypatch.setattr(modulo, "generate_response", mock_fallo)

    # ACT
    resp = client.post("/chatbot_donante", json={"mensaje_ingresado": "Hola"})

    # ASSERT
    assert resp.status_code == 200
    assert "Lo siento, tengo problemas técnicos" in resp.get_json()["respuesta"]