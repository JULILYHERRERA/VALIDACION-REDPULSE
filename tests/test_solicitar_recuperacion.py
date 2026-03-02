import pytest
import sys
import os

# Ruta absoluta al directorio raíz del proyecto
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Agrega src al path
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from app import app

#fixture -> configuración previa que necesitan las pruebas 
# activa el modo testing de flask
#Crea un cliente que simula peticiones HTTP
#Permite hacer .get() y .post() sin levantar el servidor
@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"  # necesario para sesiones
    with app.test_client() as client:
        yield client

#prueba 1 rederizacion a vista 
def test_get_renderiza_vista(client):
    resp = client.get("/solicitar_recuperacion")
    assert resp.status_code == 200


#prueba 2 si ya hay sesión redirige
def test_redirige_si_ya_hay_sesion(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "test"}

    resp = client.get("/solicitar_recuperacion", follow_redirects=False)
    assert resp.status_code in (301, 302)

#prueba 3 POST con correo NO registrado (mock)
def test_post_correo_no_registrado(client, monkeypatch):
    import app as modulo  # el módulo real donde está la función

    monkeypatch.setattr(modulo, "verificarCorreo", lambda email: False)

    resp = client.post("/solicitar_recuperacion", data={"correo": "no@existe.com"})
    assert resp.status_code == 200

    with client.session_transaction() as sess:
        assert sess["correo_valido_resultado"] is False


#prueba 4 POST con correo registrado
def test_post_correo_registrado_envia_codigo(client, monkeypatch):
    import app as modulo

    monkeypatch.setattr(modulo, "verificarCorreo", lambda email: True)
    monkeypatch.setattr(modulo, "obtenerCodigoRecuperacion", lambda email: "ABC123")

    llamadas = {"count": 0, "args": None}

    def mock_enviar(email, codigo):
        llamadas["count"] += 1
        llamadas["args"] = (email, codigo)

    monkeypatch.setattr(modulo.email, "recuperar_contra_notificacion", mock_enviar)

    correo = "si@existe.com"
    resp = client.post("/solicitar_recuperacion", data={"correo": correo})
    assert resp.status_code == 200

    with client.session_transaction() as sess:
        assert sess["correo_valido_resultado"] is True
        assert sess["correo_recuperacion"] == "ABC123"
        assert sess["correo_recuperacion_asociado"] == correo

    assert llamadas["count"] == 1
    assert llamadas["args"] == (correo, "ABC123")