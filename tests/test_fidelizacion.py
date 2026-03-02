import pytest
import sys
from unittest.mock import patch, MagicMock 
from flask import Flask, session

sys.modules['secret_config'] = MagicMock()

from flask import Flask, session
# Import correcto
from src.controladores.puntos_controlador import procesarPuntos


@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "test_key"
    return app


# 🟢 CASO 1: Tiene puntos suficientes
def test_procesar_puntos_con_suficientes_puntos(app):
    with app.test_request_context():

        session['user_data'] = {
            'puntos': 5000,
            'numero_documento': '123',
            'tipo_documento': 'CC',
            'correo': 'test@mail.com'
        }

        with patch("src.controladores.puntos_controlador.actualizarUsuarioSesion") as mock_sesion, \
             patch("src.controladores.puntos_controlador.actualizarPuntos") as mock_bd, \
             patch("src.controladores.puntos_controlador.email.redimir_puntos_notificacion") as mock_email, \
             patch("src.controladores.puntos_controlador.secrets.token_urlsafe") as mock_token:

            mock_token.return_value = "codigo_test"

            resultado = procesarPuntos(2000)

            assert resultado is True
            mock_sesion.assert_called_once_with('puntos', 3000)
            mock_bd.assert_called_once_with('123', 'CC', 3000)
            mock_email.assert_called_once()


# 🔴 CASO 2: No tiene puntos suficientes
def test_procesar_puntos_sin_puntos_suficientes(app):
    with app.test_request_context():

        session['user_data'] = {
            'puntos': 1000,
            'numero_documento': '123',
            'tipo_documento': 'CC',
            'correo': 'test@mail.com'
        }

        with patch("src.controladores.puntos_controlador.actualizarUsuarioSesion") as mock_sesion, \
             patch("src.controladores.puntos_controlador.actualizarPuntos") as mock_bd, \
             patch("src.controladores.puntos_controlador.email.redimir_puntos_notificacion") as mock_email:

            resultado = procesarPuntos(2000)

            assert resultado is False
            mock_sesion.assert_not_called()
            mock_bd.assert_not_called()
            mock_email.assert_not_called()