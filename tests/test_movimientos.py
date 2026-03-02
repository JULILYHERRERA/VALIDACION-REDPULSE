import sys
from unittest.mock import MagicMock


sys.modules['secret_config'] = MagicMock()

import pytest
from flask import session
from src.app import app   


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = "test_key"
    with app.test_client() as client:
        yield client


# 🟢 CASO 1: Usuario NO tiene sesión
def test_movimientos_sin_sesion(client):
    response = client.get('/movimientos')

    # Debe redirigir (código 302)
    assert response.status_code == 302
    assert '/home' in response.location


# 🔵 CASO 2: Usuario SÍ tiene sesión
def test_movimientos_con_sesion(client):
    with client.session_transaction() as sess:
        sess['user_data'] = {
            'nombre': 'Xime',
            'correo': 'test@mail.com'
        }

    response = client.get('/movimientos')

    # Debe mostrar la página
    assert response.status_code == 200
    assert b"movimientos" in response.data  # palabra esperada en el html