import pytest
import io
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from app import app

def test_api_actualizar_foto_perfil_exitoso(client, monkeypatch):
    """Verifica respuesta JSON correcta en caso de éxito."""
    # Arrange
    mock_nuevo_link = "https://i.imgur.com/test.jpg"
    mock_nuevo_deletehash = "abc123"

    def mock_generarUsuarioImagen(imagen, handler):
        return mock_nuevo_link, mock_nuevo_deletehash
    monkeypatch.setattr("app.generarUsuarioImagen", mock_generarUsuarioImagen)

    def mock_actualizar_imagen(doc, tip, link, delete):
        pass  # Spy no necesario para API
    monkeypatch.setattr("app.actualizar_imagen_usuario", mock_actualizar_imagen)

    with client.session_transaction() as sess:
        sess["user_data"] = {
            "numero_documento": "12345678",
            "tipo_documento": "Cedula de Ciudadania",
            "perfil_imagen_link": "https://default.jpg",
            "perfil_imagen_deletehash": None
        }

    # Act
    data = {"foto": (io.BytesIO(b"fake image data"), "test.jpg")}
    response = client.post("/actualizar_foto_perfil", data=data, content_type="multipart/form-data")

    # Assert (API)
    assert response.status_code == 200
    assert "application/json" in response.content_type
    json_data = response.get_json()
    assert "success" in json_data
    assert "new_image_url" in json_data
    assert json_data["success"] is True
    assert json_data["new_image_url"] == mock_nuevo_link

def test_api_actualizar_foto_perfil_no_autorizado(client):
    """Verifica respuesta JSON para usuario sin sesión."""
    data = {"foto": (io.BytesIO(b"data"), "test.jpg")}
    response = client.post("/actualizar_foto_perfil", data=data, content_type="multipart/form-data")
    assert response.status_code == 401
    json_data = response.get_json()
    assert "success" in json_data
    assert "error" in json_data
    assert json_data["success"] is False
    assert json_data["error"] == "No autorizado"

def test_api_actualizar_foto_perfil_sin_archivo(client):
    """Verifica respuesta JSON cuando falta el archivo."""
    with client.session_transaction() as sess:
        sess["user_data"] = {"numero_documento": "123"}
    response = client.post("/actualizar_foto_perfil", data={})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["success"] is False
    assert json_data["error"] == "No se envió ninguna imagen"

def test_api_actualizar_foto_perfil_archivo_vacio(client):
    """Verifica respuesta JSON cuando el nombre del archivo está vacío."""
    with client.session_transaction() as sess:
        sess["user_data"] = {"numero_documento": "123"}
    data = {"foto": (io.BytesIO(b"data"), "")}
    response = client.post("/actualizar_foto_perfil", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["error"] == "Archivo vacío"

def test_api_actualizar_foto_perfil_error_imgur(client, monkeypatch):
    """Verifica respuesta JSON cuando Imgur falla."""
    import secret_config
    # Retornar exactamente DEFAULT_PROFILE_PICTURE
    def mock_generarUsuarioImagen(imagen, handler):
        return secret_config.DEFAULT_PROFILE_PICTURE, None
    monkeypatch.setattr("app.generarUsuarioImagen", mock_generarUsuarioImagen)
    # También mockear actualizar_imagen_usuario para que no interfiera (aunque no debería llamarse)
    monkeypatch.setattr("app.actualizar_imagen_usuario", lambda doc, tip, link, delete: None)
    
    with client.session_transaction() as sess:
        sess["user_data"] = {"numero_documento": "123"}
    data = {"foto": (io.BytesIO(b"data"), "test.jpg")}
    response = client.post("/actualizar_foto_perfil", data=data, content_type="multipart/form-data")
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data["success"] is False
    assert json_data["error"] == "Error al subir la imagen a Imgur"
