"""
Pruebas de rendimiento para el endpoint /actualizar_foto_perfil.
Requiere instalar pytest-benchmark
"""

import pytest
import io
import sys
import os
from assertpy import assert_that

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from app import app

@pytest.fixture
def performance_client(client, monkeypatch):
    """Configura el cliente con mocks para pruebas de rendimiento."""
    def mock_generarUsuarioImagen(imagen, handler):
        return "https://i.imgur.com/bench.jpg", "bench_hash"
    monkeypatch.setattr("app.generarUsuarioImagen", mock_generarUsuarioImagen)
    monkeypatch.setattr("app.actualizar_imagen_usuario", lambda doc, tip, link, delete: None)
    with client.session_transaction() as sess:
        sess["user_data"] = {
            "numero_documento": "12345678",
            "tipo_documento": "Cedula",
            "perfil_imagen_link": "https://default.jpg",
            "perfil_imagen_deletehash": None
        }
    return client

def test_actualizar_foto_perfil_rendimiento_single(performance_client, benchmark):
    """Mide el tiempo de una sola petición exitosa."""
    def hacer_peticion():
        data = {"foto": (io.BytesIO(b"fake image data"), "test.jpg")}
        return performance_client.post("/actualizar_foto_perfil", data=data, content_type="multipart/form-data")
    response = benchmark(hacer_peticion)
    assert_that(response.status_code).is_equal_to(200)

# La prueba concurrente se elimina porque no es trivial con Flask test_client.