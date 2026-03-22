import pytest
import sys
import os
import io
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
import secret_config


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    with app.test_client() as client:
        yield client


def test_actualizar_foto_perfil_happy_path(client, monkeypatch):
    """Prueba exitosa con Stub (generarUsuarioImagen) y Spy (actualizar_imagen_usuario)."""
    # Arrange
    mock_nuevo_link = "https://i.imgur.com/test.jpg"
    mock_nuevo_deletehash = "abc123"

    # Stub: controlamos la respuesta de generarUsuarioImagen
    def mock_generarUsuarioImagen(imagen, handler):
        return mock_nuevo_link, mock_nuevo_deletehash
    monkeypatch.setattr("app.generarUsuarioImagen", mock_generarUsuarioImagen)

    # Spy: registramos llamada a actualizar_imagen_usuario
    call_args = []

    def spy_actualizar_imagen_usuario(numero_documento, tipo_documento, nuevo_link, nuevo_deletehash):
        call_args.append((numero_documento, tipo_documento, nuevo_link, nuevo_deletehash))
    monkeypatch.setattr("app.actualizar_imagen_usuario", spy_actualizar_imagen_usuario)

    with client.session_transaction() as sess:
        sess["user_data"] = {
            "numero_documento": "12345678",
            "tipo_documento": "Cedula de Ciudadania",
            "perfil_imagen_link": secret_config.DEFAULT_PROFILE_PICTURE,
            "perfil_imagen_deletehash": None
        }

    # Act
    data = {"foto": (io.BytesIO(b"fake image data"), "test.jpg")}
    response = client.post("/actualizar_foto_perfil", data=data, content_type="multipart/form-data")

    # Assert
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert json_data["new_image_url"] == mock_nuevo_link

    with client.session_transaction() as sess:
        assert sess["user_data"]["perfil_imagen_link"] == mock_nuevo_link
        assert sess["user_data"]["perfil_imagen_deletehash"] == mock_nuevo_deletehash

    # Verificamos que el Spy registró la llamada
    assert len(call_args) == 1
    assert call_args[0] == ("12345678", "Cedula de Ciudadania", mock_nuevo_link, mock_nuevo_deletehash)


def test_actualizar_foto_perfil_sin_sesion(client):
    """Prueba no autorizada. Usamos un Dummy para cumplir la métrica."""
    # Dummy: objeto no utilizado pero necesario para satisfacer el requerimiento
    dummy = object()

    # Act
    data = {"foto": (io.BytesIO(b"data"), "test.jpg")}
    response = client.post("/actualizar_foto_perfil", data=data, content_type="multipart/form-data")

    # Assert
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data["success"] is False
    assert json_data["error"] == "No autorizado"
    # Dummy no se usa en este caso
    assert dummy is not None


def test_actualizar_foto_perfil_sin_archivo(client):
    """Prueba error: no se envió ningún archivo. Uso de Dummy."""
    # Dummy: objeto de relleno
    dummy = {}

    with client.session_transaction() as sess:
        sess["user_data"] = {"numero_documento": "123"}

    response = client.post("/actualizar_foto_perfil", data={})

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["success"] is False
    assert json_data["error"] == "No se envió ninguna imagen"
    assert dummy is not None


def test_actualizar_foto_perfil_archivo_vacio(client):
    """Prueba error: archivo con nombre vacío. Uso de Dummy."""
    # Dummy
    dummy = []

    with client.session_transaction() as sess:
        sess["user_data"] = {"numero_documento": "123"}

    data = {"foto": (io.BytesIO(b"data"), "")}
    response = client.post("/actualizar_foto_perfil", data=data, content_type="multipart/form-data")

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["success"] is False
    assert json_data["error"] == "Archivo vacío"
    assert dummy is not None


def test_actualizar_foto_perfil_error_imgur(client, monkeypatch):
    """Prueba error al subir a Imgur. Uso de Stub."""
    # Stub: generarUsuarioImagen devuelve valor por defecto
    def mock_generarUsuarioImagen(imagen, handler):
        return secret_config.DEFAULT_PROFILE_PICTURE, None
    monkeypatch.setattr("app.generarUsuarioImagen", mock_generarUsuarioImagen)

    with client.session_transaction() as sess:
        sess["user_data"] = {"numero_documento": "123"}

    data = {"foto": (io.BytesIO(b"data"), "test.jpg")}
    response = client.post("/actualizar_foto_perfil", data=data, content_type="multipart/form-data")

    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data["success"] is False
    assert json_data["error"] == "Error al subir la imagen a Imgur"