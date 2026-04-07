import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as modulo
from app import app

# =====================================================
# PRUEBA 1 – Sin enfermero redirige
# =====================================================
def test_prueba1_sin_enfermero_redirige_a_home(client):
    # ARRANGE

    # ACT
    resp = client.get("/agregar_donacion", follow_redirects=False)

    # ASSERT
    assert resp.status_code in (301, 302)
    assert resp.headers.get("Location") is not None

# =====================================================
# PRUEBA 2 – GET reinicia bandera
# =====================================================
def test_prueba2_get_renderiza_y_reinicia_bandera(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Juliana", "enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "123",
            "tipo_cedula_usuario": "Cedula de Ciudadania"
        }
        sess["enfermero_usuario_verificacion"] = True

    # ACT
    resp = client.get("/agregar_donacion")

    # ASSERT
    assert resp.status_code == 200

    with client.session_transaction() as sess:
        assert sess["enfermero_usuario_verificacion"] is None

# =====================================================
# PRUEBA 3 – POST válido guarda resultado
# STUB + SPY
# =====================================================
def test_prueba3_post_valido_guarda_resultado(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_insertar(doc, tipo, fecha, cantidad):
        llamadas.append((doc, tipo, fecha, cantidad))
        return True

    monkeypatch.setattr(modulo, "insertarDonacion", fake_insertar)

    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Juliana", "enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "123",
            "tipo_cedula_usuario": "Cedula de Ciudadania"
        }

    # ACT
    resp = client.post("/agregar_donacion", data={
        "cantidad_donada": "500",
        "fecha_donacion": "2026-03-02"
    })

    # ASSERT
    assert resp.status_code == 200
    assert llamadas == [("123", "Cedula de Ciudadania", "2026-03-02", 500)]

    with client.session_transaction() as sess:
        assert sess["donacion_exitosa"] is True

# =====================================================
# PRUEBA 4 – POST sin cantidad no debería procesarse
# SPY (FALLA)
# =====================================================
def test_prueba4_post_sin_cantidad_no_deberia_procesarse(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_insertar(doc, tipo, fecha, cantidad):
        llamadas.append((doc, tipo, fecha, cantidad))
        return True

    monkeypatch.setattr(modulo, "insertarDonacion", fake_insertar)

    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Juliana", "enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "123",
            "tipo_cedula_usuario": "Cedula de Ciudadania"
        }

    # ACT
    resp = client.post("/agregar_donacion", data={
        "fecha_donacion": "2026-03-02"
    })

    # ASSERT
    assert resp.status_code == 200
    assert llamadas == []

# =====================================================
# PRUEBA 5 – POST sin usuario obtenido no debería procesarse
# SPY (FALLA)
# =====================================================
def test_prueba5_post_sin_usuario_obtenido_no_deberia_procesarse(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_insertar(doc, tipo, fecha, cantidad):
        llamadas.append((doc, tipo, fecha, cantidad))
        return True

    monkeypatch.setattr(modulo, "insertarDonacion", fake_insertar)

    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Juliana", "enfermero": True}

    # ACT
    resp = client.post("/agregar_donacion", data={
        "cantidad_donada": "500",
        "fecha_donacion": "2026-03-02"
    })

    # ASSERT
    assert resp.status_code == 200
    assert llamadas == []