import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# SEGURIDAD 1 – Redirige si no es donante
# =====================================================
def test_seguridad_rol_incorrecto(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Luis", "donante": False}

    # ACT
    resp = client.get("/chatbot_donante", follow_redirects=False)

    # ASSERT
    assert resp.status_code in (301, 302)
    assert "/chatbot_solicitante" in resp.location


# =====================================================
# SEGURIDAD 2 – Mensaje vacío bloqueado
# =====================================================
def test_seguridad_mensaje_vacio(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    # ACT
    resp = client.post("/chatbot_donante",
                       json={"mensaje_ingresado": ""})

    # ASSERT
    assert resp.status_code == 400


# =====================================================
# SEGURIDAD 3 – Sin JSON no rompe
# =====================================================
def test_seguridad_sin_json(client):
    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    # ACT
    resp = client.post("/chatbot_donante")

    # ASSERT
    assert resp.status_code == 400


# =====================================================
# SEGURIDAD 4 – Inyección simple (no rompe)
# =====================================================
def test_seguridad_inyeccion_input(client, monkeypatch):
    import app as modulo

    # ARRANGE
    with client.session_transaction() as sess:
        sess["user_data"] = {"nombre": "Ana", "donante": True}

    monkeypatch.setattr(modulo, "generate_response",
                        lambda *args: "ok")

    # ACT
    resp = client.post("/chatbot_donante",
                       json={"mensaje_ingresado": "' OR 1=1 --"})

    # ASSERT
    assert resp.status_code == 200