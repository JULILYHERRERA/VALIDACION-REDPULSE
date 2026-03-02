import pytest
import sys
import json
from unittest.mock import patch, MagicMock

sys.modules['secret_config'] = MagicMock()

from src.app import app  


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client


# ─────────────────────────────────────────────
# CAMINO 1: 1→2→3→4→5→9
# Usuario NO existe o NO es admin → Redirige a 'home'
# ─────────────────────────────────────────────

def test_sin_sesion_redirige_a_home(client):
    with client.session_transaction() as sess:
        sess.clear()

    response = client.get('/estadisticas')

    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_usuario_no_admin_redirige_a_home(client):
    with client.session_transaction() as sess:
        sess['user_data'] = {'nombre': 'Juan', 'admin': False}

    response = client.get('/estadisticas')

    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_usuario_sin_campo_admin_redirige_a_home(client):
    with client.session_transaction() as sess:
        sess['user_data'] = {'nombre': 'Juan'}

    response = client.get('/estadisticas')

    assert response.status_code == 302
    assert response.headers['Location'] == '/'


# ─────────────────────────────────────────────
# CAMINO 2: 1→2→3→4→6→7→8→9
# Usuario existe y ES admin → Obtiene datos y renderiza template
# ─────────────────────────────────────────────

@patch('app.obtenerCantidadDeSangrePorTipo')
@patch('app.obtenerDonacionesPorMes')
def test_admin_llama_funciones_y_renderiza_template(mock_donaciones, mock_sangre, client):
    mock_donaciones.return_value = [{'mes': 'Enero', 'total': 10}]
    mock_sangre.return_value = [{'tipo': 'A+', 'cantidad': 20}]

    with client.session_transaction() as sess:
        sess['user_data'] = {'nombre': 'Admin', 'admin': True}

    response = client.get('/estadisticas')

    assert response.status_code == 200
    mock_donaciones.assert_called_once()
    mock_sangre.assert_called_once()


@patch('app.obtenerCantidadDeSangrePorTipo')
@patch('app.obtenerDonacionesPorMes')
def test_admin_datos_serializados_en_json(mock_donaciones, mock_sangre, client):
    donaciones_mock = [{'mes': 'Marzo', 'total': 8}]
    sangre_mock = [{'tipo': 'B+', 'cantidad': 12}]
    mock_donaciones.return_value = donaciones_mock
    mock_sangre.return_value = sangre_mock

    with client.session_transaction() as sess:
        sess['user_data'] = {'nombre': 'Admin', 'admin': True}

    response = client.get('/estadisticas')
    html = response.data.decode('utf-8')

    assert response.status_code == 200
    assert json.dumps(donaciones_mock) in html
    assert json.dumps(sangre_mock) in html


@patch('app.obtenerCantidadDeSangrePorTipo')
@patch('app.obtenerDonacionesPorMes')
def test_admin_sin_datos_listas_vacias(mock_donaciones, mock_sangre, client):
    mock_donaciones.return_value = []
    mock_sangre.return_value = []

    with client.session_transaction() as sess:
        sess['user_data'] = {'nombre': 'Admin', 'admin': True}

    response = client.get('/estadisticas')
    html = response.data.decode('utf-8')

    assert response.status_code == 200
    assert json.dumps([]) in html