

import sys
from types import SimpleNamespace
import pytest
from unittest.mock import patch

# Mock de secret_config
sys.modules['secret_config'] = SimpleNamespace(
    DB_USER="test_user",
    DB_PASSWORD="test_password",
    DB_HOST="localhost",
    DB_NAME="test_db",
    DEFAULT_PROFILE_PICTURE="default.png",
    NOTIEMAIL="test@example.com",
    NOTI_APPCONTRA="testpass",
    ADMINEMAIL="admin@example.com",
    CHAT_BOT_KEY="test_chatbot_key",
    SECRET_KEY_FLASK="test_secret_key"
)

from src.app import app



@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Camino 1: Usuario NO ha iniciado sesión → redirige
def test_agregar_donacion_usuario_no_logueado(client):
    # Sesión vacía simula usuario no logueado
    with client.session_transaction() as sess:
        sess.clear()

    response = client.get('/agregar_donacion')
    # Se espera redirección a home
    assert response.status_code == 302
    assert '/home' in response.headers['Location']

# Camino 2: Usuario logueado → formulario GET
def test_agregar_donacion_get_usuario_logueado(client):
    with client.session_transaction() as sess:
        sess['user_data'] = {'enfermero': True}
        sess['enfermero_usuario_obtenido'] = {'cedula_usuario': '12345', 'tipo_cedula_usuario': 'CC'}

    response = client.get('/agregar_donacion')
    # Se espera que devuelva 200 y el template
    assert response.status_code == 200
    assert b'<form' in response.data  # Verifica que se renderice un formulario