import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as modulo
from app import app

# =====================================================
# PRUEBA 1 – Sin sesión redirige
# =====================================================
def test_prueba1_sin_sesion_redirige_a_home(client):
    # ARRANGE

    # ACT
    resp = client.get("/puntos", follow_redirects=False)

    # ASSERT
    assert resp.status_code in (301, 302)
    assert resp.headers.get("Location") is not None

# =====================================================
# PRUEBA 2 – Con sesión renderiza vista
# STUB
# =====================================================
def test_prueba2_con_sesion_renderiza_vista(client, monkeypatch):
    # ARRANGE
    contexto = {}

    def fake_render(template_name, **kwargs):
        contexto["template"] = template_name
        contexto["user_data"] = kwargs.get("user_data")
        return "render ok"

    monkeypatch.setattr(modulo, "render_template", fake_render)

    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Juliana", "puntos": 2000}

    # ACT
    resp = client.get("/puntos")

    # ASSERT
    assert resp.status_code == 200
    assert contexto["template"] == "puntos.html"
    assert contexto["user_data"]["puntos"] == 2000

# =====================================================
# PRUEBA 3 – POST válido procesa puntos
# STUB + SPY
# =====================================================
def test_prueba3_post_valido_procesa_puntos(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_procesar(puntos):
        llamadas.append(puntos)
        return True

    monkeypatch.setattr(modulo, "procesar_puntos", fake_procesar)
    monkeypatch.setattr(modulo, "obtenerValorUsuarioSesion", lambda clave: 1500)

    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Juliana", "puntos": 2000}

    # ACT
    resp = client.post("/puntos", json={"puntos_seleccionados": "4000"})

    # ASSERT
    assert resp.status_code == 200
    assert resp.is_json
    assert llamadas == [4000]
    assert resp.get_json() == {"success": True, "nuevos_puntos": 1500}

# =====================================================
# PRUEBA 4 – POST sin JSON debería manejarse
# FALLA
# =====================================================
def test_prueba4_post_sin_json_deberia_manejarse(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Juliana", "puntos": 2000}

    # ACT
    resp = client.post("/puntos")

    # ASSERT
    assert resp.status_code == 400

# =====================================================
# PRUEBA 5 – POST inválido no debería procesarse
# SPY (FALLA)
# =====================================================
def test_prueba5_post_valor_invalido_no_deberia_procesarse(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_procesar(puntos):
        llamadas.append(puntos)
        return False

    monkeypatch.setattr(modulo, "procesar_puntos", fake_procesar)
    monkeypatch.setattr(modulo, "obtenerValorUsuarioSesion", lambda clave: 2000)

    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Juliana", "puntos": 2000}

    # ACT
    resp = client.post("/puntos", json={"puntos_seleccionados": "hola"})

    # ASSERT
    assert resp.status_code == 400
    assert llamadas == []