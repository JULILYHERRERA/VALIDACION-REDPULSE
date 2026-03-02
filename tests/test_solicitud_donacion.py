import sys
from unittest.mock import patch, MagicMock

# Por si usas secret_config en el proyecto
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


# 🔴 CASO 1: Usuario sin sesión
def test_solicitud_sin_sesion(client):
    response = client.get('/solicitud_donacion')

    assert response.status_code == 302
    assert '/home' in response.location


# 🟢 CASO 2: Usuario con sesión (GET)
def test_solicitud_con_sesion_get(client):
    with client.session_transaction() as sess:
        sess['user_data'] = {'nombre': 'Xime'}

    response = client.get('/solicitud_donacion')

    assert response.status_code == 200
    assert b"solicitud" in response.data


# 🔵 CASO 3: Usuario con sesión (POST)
@patch("src.registro_servicio.crearRegistro")  
def test_solicitud_con_sesion_post(mock_crearRegistro, client):

    mock_crearRegistro.return_value = True

    with client.session_transaction() as sess:
        sess['user_data'] = {'nombre': 'Xime'}

    response = client.post('/solicitud_donacion', data={
        'tipo_sangre': 'O+',
        'cantidad': '2'
    })

    assert response.status_code == 200
    mock_crearRegistro.assert_called_once()

    # Validar que guardó el resultado en sesión
    with client.session_transaction() as sess:
        assert sess['registro_creado'] == True