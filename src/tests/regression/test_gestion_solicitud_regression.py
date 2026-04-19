import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# REGRESIÓN 1 – GET mantiene funcionamiento básico
# =====================================================
def test_regresion_get_funciona(client, monkeypatch):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    monkeypatch.setattr(app, "obtenerSolicitudesPendientes",
                        lambda: [{"id": 1, "tipo": "O+"}])

    # ======================= ACT =======================
    resp = client.get("/solicitudes_pendientes")

    # ====================== ASSERT =====================
    assert resp.status_code == 200


# =====================================================
# REGRESIÓN 2 – POST flujo completo estable
# =====================================================
def test_regresion_post_flujo_estable(client, monkeypatch):

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
        "id": 1,
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
# REGRESIÓN 3 – POST sigue funcionando múltiples veces
# =====================================================
def test_regresion_post_repetido(client, monkeypatch):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    monkeypatch.setattr(app, "actualizarEstadoRegistro", lambda *a: None)
    monkeypatch.setattr(app, "verificarNivelesDeSangre", lambda *a: None)
    monkeypatch.setattr(app, "obtenerSolicitudesPendientes", lambda: [])

    data = {
        "id": 2,
        "accion": "aprobado",
        "tipo_sangre": "A+"
    }

    # ======================= ACT =======================
    respuestas = [client.post("/solicitudes_pendientes", json=data) for _ in range(3)]

    # ====================== ASSERT =====================
    for resp in respuestas:
        assert resp.status_code == 200


# =====================================================
# REGRESIÓN 4 – GET no rompe sin datos
# =====================================================
def test_regresion_get_sin_datos(client, monkeypatch):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    monkeypatch.setattr(app, "obtenerSolicitudesPendientes", lambda: [])

    # ======================= ACT =======================
    resp = client.get("/solicitudes_pendientes")

    # ====================== ASSERT =====================
    assert resp.status_code == 200


# =====================================================
# REGRESIÓN 5 – Integración de funciones no se rompe
# =====================================================
def test_regresion_integracion_servicios(client, monkeypatch):

    # ===================== ARRANGE =====================
    with client.session_transaction() as sess:
        sess["user_data"] = {"admin": True}

    registro_args = []
    sangre_args = []

    def mock_update(id, accion):
        registro_args.append((id, accion))

    def mock_verificar(id, accion, tipo):
        sangre_args.append((id, accion, tipo))

    monkeypatch.setattr(app, "actualizarEstadoRegistro", mock_update)
    monkeypatch.setattr(app, "verificarNivelesDeSangre", mock_verificar)
    monkeypatch.setattr(app, "obtenerSolicitudesPendientes", lambda: [])

    data = {
        "id": 99,
        "accion": "aprobado",
        "tipo_sangre": "AB+"
    }

    # ======================= ACT =======================
    resp = client.post("/solicitudes_pendientes", json=data)

    # ====================== ASSERT =====================
    assert resp.status_code == 200
    assert registro_args == [(99, "aprobado")]
    assert sangre_args == [(99, "aprobado", "AB+")]