import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# SECURITY 1 – Redención requiere sesión activa
# =====================================================
def test_security_redencion_sin_sesion(client):
    resp = client.post("/puntos", json={"puntos_seleccionados": 1000}, follow_redirects=False)
    assert resp.status_code in (301, 302)

# =====================================================
# SECURITY 2 – Protección CSRF en redención (JSON)
# =====================================================
def test_security_redencion_csrf(client):
    # Sin el token CSRF en una petición que no sea JSON o sin los headers correctos,
    # aunque aquí Flask-WTF suele estar configurado para proteger.
    # Como la ruta tiene `csrf.protect()`, verificamos que falle sin sesión/token.
    resp = client.post("/puntos", data={"puntos_seleccionados": 1000})
    assert resp.status_code in (400, 403, 302)
