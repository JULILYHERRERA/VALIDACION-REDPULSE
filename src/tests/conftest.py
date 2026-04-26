"""
conftest.py – Fixtures compartidos para toda la suite de pruebas.

El fixture `client` provee un cliente HTTP de Flask que:
  1. Inicializa la sesión haciendo un GET a /login (ruta pública) para que
     Flask-WTF genere y almacene el token CSRF en la sesión.
  2. Extrae el token del HTML renderizado (meta tag o campo oculto).
  3. Envuelve client.post() para inyectar automáticamente el token en:
       - Peticiones de formulario: campo oculto `csrf_token` en `data`.
       - Peticiones JSON: cabecera `X-CSRFToken`.

De este modo CSRF permanece activo durante las pruebas y SonarQube
no reporta el Security Hotspot de "CSRF protection disabled".
"""

import re
import sys
import os

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app


# ---------------------------------------------------------------------------
# Utilidad interna
# ---------------------------------------------------------------------------

def _extraer_csrf(html: bytes) -> str:
    """Extrae el token CSRF del HTML de respuesta.

    Busca las dos variantes más habituales:
      <meta name="csrf-token" content="TOKEN">
      <input type="hidden" name="csrf_token" value="TOKEN">
    """
    patrones = [
        rb'<meta[^>]+name="csrf-token"[^>]+content="([^"]+)"',
        rb'<meta[^>]+content="([^"]+)"[^>]+name="csrf-token"',
        rb'name="csrf_token"[^>]+value="([^"]+)"',
        rb'value="([^"]+)"[^>]+name="csrf_token"',
    ]
    for patron in patrones:
        m = re.search(patron, html)
        if m:
            return m.group(1).decode("utf-8")
    return ""


# ---------------------------------------------------------------------------
# Fixture principal
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Cliente Flask con inyección automática del token CSRF en POST."""

    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret"

    with flask_app.test_client() as c:
        # GET a ruta pública → Flask-WTF crea y guarda el token en sesión.
        resp = c.get("/login")
        token = _extraer_csrf(resp.data)

        # Envolvemos client.post para inyectar el token automáticamente.
        _post_original = c.post

        def post_con_csrf(path, **kwargs):
            headers = dict(kwargs.pop("headers", None) or {})

            if "json" in kwargs:
                headers.setdefault("X-CSRFToken", token)

            elif "data" in kwargs:
                if isinstance(kwargs["data"], dict):
                    datos = dict(kwargs["data"])
                    datos.setdefault("csrf_token", token)
                    kwargs["data"] = datos

            else:
                headers.setdefault("X-CSRFToken", token)
                
            kwargs["headers"] = headers

            return _post_original(path, **kwargs)
        
        c.post = post_con_csrf
        yield c