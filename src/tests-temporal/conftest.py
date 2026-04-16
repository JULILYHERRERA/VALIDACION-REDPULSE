import os
import re
import sys

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app


def _extraer_csrf(html: bytes) -> str:
    patrones = [
        rb'<meta[^>]+name="csrf-token"[^>]+content="([^"]+)"',
        rb'<meta[^>]+content="([^"]+)"[^>]+name="csrf-token"',
        rb'name="csrf_token"[^>]+value="([^"]+)"',
        rb'value="([^"]+)"[^>]+name="csrf_token"',
    ]
    for patron in patrones:
        coincidencia = re.search(patron, html)
        if coincidencia:
            return coincidencia.group(1).decode("utf-8")
    return ""


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret"
    flask_app.config["WTF_CSRF_ENABLED"] = False

    with flask_app.test_client() as c:
        respuesta = c.get("/login")
        token = _extraer_csrf(respuesta.data)
        post_original = c.post

        def post_con_csrf(path, **kwargs):
            if "json" in kwargs:
                headers = dict(kwargs.pop("headers", None) or {})
                headers.setdefault("X-CSRFToken", token)
                kwargs["headers"] = headers
            elif "data" in kwargs and isinstance(kwargs["data"], dict):
                datos = dict(kwargs["data"])
                datos.setdefault("csrf_token", token)
                kwargs["data"] = datos
            return post_original(path, **kwargs)

        c.post = post_con_csrf
        yield c
