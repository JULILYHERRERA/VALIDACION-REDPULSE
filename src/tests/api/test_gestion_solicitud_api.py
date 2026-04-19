import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# API 1 – GET admin con datos
# =====================================================
def test_api_get_admin_con_datos(client, monkeypatch):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    solicitudes = [{"id": 1, "tipo": "O+"}, {"id": 2, "tipo": "A+"}]
    monkeypatch.setattr(app, "obtenerSolicitudesPendientes", lambda: solicitudes)

    # ======================= ACT =======================
    resp = client.get("/solicitudes_pendientes")

    # ====================== ASSERT =====================
    assert resp.status_code == 200
    assert resp.data is not None


# =====================================================
# API 2 – GET admin sin datos (lista vacía)
# =====================================================
def test_api_get_admin_sin_datos(client, monkeypatch):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    monkeypatch.setattr(app, "obtenerSolicitudesPendientes", lambda: [])

    # ======================= ACT =======================
    resp = client.get("/solicitudes_pendientes")

    # ====================== ASSERT =====================
    assert resp.status_code == 200


# =====================================================
# API 3 – POST flujo completo correcto
# =====================================================
def test_api_post_flujo_completo(client, monkeypatch):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    llamadas = {"update": 0, "verificar": 0}

    def mock_update(*args):
        llamadas["update"] += 1

    def mock_verificar(*args):
        llamadas["verificar"] += 1

    monkeypatch.setattr(app, "actualizarEstadoRegistro", mock_update)
    monkeypatch.setattr(app, "verificarNivelesDeSangre", mock_verificar)
    monkeypatch.setattr(app, "obtenerSolicitudesPendientes", lambda: [])

    data = {
        "id": 10,
        "accion": "aprobado",
        "tipo_sangre": "O+"
    }

    # ======================= ACT =======================
    resp = client.post("/solicitudes_pendientes", json=data)

    # ====================== ASSERT =====================
    assert resp.status_code == 200
    assert llamadas["update"] == 1
    assert llamadas["verificar"] == 1


# =====================================================
# API 4 – POST con acción diferente
# =====================================================
def test_api_post_accion_rechazado(client, monkeypatch):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    llamadas = {"update": 0}

    def mock_update(*args):
        llamadas["update"] += 1

    monkeypatch.setattr(app, "actualizarEstadoRegistro", mock_update)
    monkeypatch.setattr(app, "verificarNivelesDeSangre", lambda *a: None)
    monkeypatch.setattr(app, "obtenerSolicitudesPendientes", lambda: [])

    data = {
        "id": 5,
        "accion": "rechazado",
        "tipo_sangre": "A+"
    }

    # ======================= ACT =======================
    resp = client.post("/solicitudes_pendientes", json=data)

    # ====================== ASSERT =====================
    assert resp.status_code == 200
    assert llamadas["update"] == 1


# =====================================================
# API 5 – POST con JSON válido mínimo
# =====================================================
def test_api_post_json_minimo(client, monkeypatch):

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
    resp = client.post("/solicitudes_pendientes", json=data)

    # ====================== ASSERT =====================
    assert resp.status_code == 200
    assert resp.is_json or resp.data is not None


# =====================================================
# API 6 – POST mantiene respuesta estable múltiples veces
# =====================================================
def test_api_post_multiple_requests(client, monkeypatch):

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
    respuestas = [client.post("/solicitudes_pendientes", json=data) for _ in range(3)]

    # ====================== ASSERT =====================
    for resp in respuestas:
        assert resp.status_code == 200