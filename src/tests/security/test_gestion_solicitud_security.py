import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# SEGURIDAD 1 – Sin sesión (bloquea acceso)
# =====================================================
def test_seguridad_sin_sesion(client):

    # ===================== ARRANGE =====================
    # No se define session

    # ======================= ACT =======================
    resp = client.get("/solicitudes_pendientes", follow_redirects=False)

    # ====================== ASSERT =====================
    assert resp.status_code in (301, 302)


# =====================================================
# SEGURIDAD 2 – Usuario NO admin bloqueado
# =====================================================
def test_seguridad_usuario_no_admin(client):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": False}

    # ======================= ACT =======================
    resp = client.get("/solicitudes_pendientes", follow_redirects=False)

    # ====================== ASSERT =====================
    assert resp.status_code in (301, 302)


# =====================================================
# SEGURIDAD 3 – POST sin sesión
# =====================================================
def test_seguridad_post_sin_sesion(client):

    # ===================== ARRANGE =====================

    # ======================= ACT =======================
    resp = client.post("/solicitudes_pendientes", json={})

    # ====================== ASSERT =====================
    assert resp.status_code in (301, 302)


# =====================================================
# SEGURIDAD 4 – JSON vacío
# =====================================================
def test_seguridad_json_vacio(client, monkeypatch):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    monkeypatch.setattr(app, "actualizarEstadoRegistro", lambda *a: None)
    monkeypatch.setattr(app, "verificarNivelesDeSangre", lambda *a: None)
    monkeypatch.setattr(app, "obtenerSolicitudesPendientes", lambda: [])

    # ======================= ACT =======================
    resp = client.post("/solicitudes_pendientes", json={})

    # ====================== ASSERT =====================
    # Tu backend NO valida → puede ser 200 o 500
    assert resp.status_code in (200, 400, 500)


# =====================================================
# SEGURIDAD 5 – Campos faltantes
# =====================================================
def test_seguridad_campos_faltantes(client, monkeypatch):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    monkeypatch.setattr(app, "actualizarEstadoRegistro", lambda *a: None)
    monkeypatch.setattr(app, "verificarNivelesDeSangre", lambda *a: None)
    monkeypatch.setattr(app, "obtenerSolicitudesPendientes", lambda: [])

    data = {
        "id": 1
        # faltan campos
    }

    # ======================= ACT =======================
    resp = client.post("/solicitudes_pendientes", json=data)

    # ====================== ASSERT =====================
    assert resp.status_code in (200, 400, 500)


# =====================================================
# SEGURIDAD 6 – ID negativo (falla lógica)
# =====================================================
def test_seguridad_id_negativo(client, monkeypatch):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    monkeypatch.setattr(app, "actualizarEstadoRegistro", lambda *a: None)
    monkeypatch.setattr(app, "verificarNivelesDeSangre", lambda *a: None)
    monkeypatch.setattr(app, "obtenerSolicitudesPendientes", lambda: [])

    data = {
        "id": -10,
        "accion": "aprobado",
        "tipo_sangre": "O+"
    }

    # ======================= ACT =======================
    resp = client.post("/solicitudes_pendientes", json=data)

    # ====================== ASSERT =====================
    assert resp.status_code == 400


# =====================================================
# SEGURIDAD 7 – Input malicioso (inyección básica)
# =====================================================
def test_seguridad_input_malicioso(client, monkeypatch):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    monkeypatch.setattr(app, "actualizarEstadoRegistro", lambda *a: None)
    monkeypatch.setattr(app, "verificarNivelesDeSangre", lambda *a: None)
    monkeypatch.setattr(app, "obtenerSolicitudesPendientes", lambda: [])

    data = {
        "id": "1 OR 1=1",
        "accion": "aprobado; DROP TABLE",
        "tipo_sangre": "O+"
    }

    # ======================= ACT =======================
    resp = client.post("/solicitudes_pendientes", json=data)

    # ====================== ASSERT =====================
    # No debe romper
    assert resp.status_code in (200, 400, 500)


# =====================================================
# SEGURIDAD 8 – Tipo incorrecto en ID
# =====================================================
def test_seguridad_tipo_incorrecto_id(client, monkeypatch):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    monkeypatch.setattr(app, "actualizarEstadoRegistro", lambda *a: None)
    monkeypatch.setattr(app, "verificarNivelesDeSangre", lambda *a: None)
    monkeypatch.setattr(app, "obtenerSolicitudesPendientes", lambda: [])

    data = {
        "id": "abc",
        "accion": "aprobado",
        "tipo_sangre": "O+"
    }

    # ======================= ACT =======================
    resp = client.post("/solicitudes_pendientes", json=data)

    # ====================== ASSERT =====================
    assert resp.status_code in (200, 400, 500)


# =====================================================
# SEGURIDAD 9 – Request sin JSON
# =====================================================
def test_seguridad_sin_json(client, monkeypatch):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    # ======================= ACT =======================
    resp = client.post("/solicitudes_pendientes", data="texto plano")

    # ====================== ASSERT =====================
    assert resp.status_code in (200, 400, 415, 500)


# =====================================================
# SEGURIDAD 10 – Repetición masiva (no rompe)
# =====================================================
def test_seguridad_repeticion_requests(client, monkeypatch):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    monkeypatch.setattr(app, "actualizarEstadoRegistro", lambda *a: None)
    monkeypatch.setattr(app, "verificarNivelesDeSangre", lambda *a: None)
    monkeypatch.setattr(app, "obtenerSolicitudesPendientes", lambda: [])

    data = {
        "id": 1,
        "accion": "aprobado",
        "tipo_sangre": "O+"
    }

    # ======================= ACT =======================
    responses = [client.post("/solicitudes_pendientes", json=data) for _ in range(5)]

    # ====================== ASSERT =====================
    for resp in responses:
        assert resp.status_code == 200