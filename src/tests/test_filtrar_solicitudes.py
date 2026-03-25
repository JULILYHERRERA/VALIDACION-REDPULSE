import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app as modulo
from app import app

# =====================================================
# PRUEBA 1 – GET carga la vista
# =====================================================
def test_prueba1_get_renderiza_filtrar_solicitudes(client):
    # ARRANGE

    # ACT
    resp = client.get("/filtrar_solicitudes")

    # ASSERT
    assert resp.status_code == 200

# =====================================================
# PRUEBA 2 – GET muestra mensaje vacío
# =====================================================
def test_prueba2_get_muestra_mensaje_vacio(client):
    # ARRANGE

    # ACT
    resp = client.get("/filtrar_solicitudes")

    # ASSERT
    assert resp.status_code == 200
    assert b"No hay solicitudes para el tipo de sangre seleccionado." in resp.data

# =====================================================
# PRUEBA 3 – POST válido retorna datos
# STUB + SPY
# =====================================================
def test_prueba3_post_tipo_valido_consulta_servicio(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_obtener(tipo_sangre):
        llamadas.append(tipo_sangre)
        return [{
            "nombreDonante": "Ana",
            "tipoSangre": "O+",
            "cantidad": 450,
            "fecha": "2026-03-23",
            "razon": "Cirugia",
            "prioridad": "Alta"
        }]

    monkeypatch.setattr(modulo, "obtenerSolicitudesPendientesPorTipo", fake_obtener)

    # ACT
    resp = client.post("/filtrar_solicitudes", data={"tipo_sangre": "O+"})

    # ASSERT
    assert resp.status_code == 200
    assert llamadas == ["O+"]
    assert b"Ana" in resp.data

# =====================================================
# PRUEBA 4 – POST válido sin resultados
# STUB
# =====================================================
def test_prueba4_post_tipo_valido_sin_resultados(client, monkeypatch):
    # ARRANGE
    monkeypatch.setattr(modulo, "obtenerSolicitudesPendientesPorTipo", lambda x: [])

    # ACT
    resp = client.post("/filtrar_solicitudes", data={"tipo_sangre": "AB-"})

    # ASSERT
    assert resp.status_code == 200
    assert b"No hay solicitudes para el tipo de sangre seleccionado." in resp.data

# =====================================================
# PRUEBA 5 – POST sin dato no debería consultar
# SPY (FALLA)
# =====================================================
def test_prueba5_post_sin_tipo_sangre_no_deberia_consultar_servicio(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_obtener(tipo_sangre):
        llamadas.append(tipo_sangre)
        return []

    monkeypatch.setattr(modulo, "obtenerSolicitudesPendientesPorTipo", fake_obtener)

    # ACT
    resp = client.post("/filtrar_solicitudes", data={})

    # ASSERT
    assert resp.status_code == 200
    assert llamadas == []

# =====================================================
# PRUEBA 6 – POST vacío no debería consultar
# SPY (FALLA)
# =====================================================
def test_prueba6_post_tipo_vacio_no_deberia_consultar_servicio(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_obtener(tipo_sangre):
        llamadas.append(tipo_sangre)
        return []

    monkeypatch.setattr(modulo, "obtenerSolicitudesPendientesPorTipo", fake_obtener)

    # ACT
    resp = client.post("/filtrar_solicitudes", data={"tipo_sangre": ""})

    # ASSERT
    assert resp.status_code == 200
    assert llamadas == []

# =====================================================
# PRUEBA 7 – POST con espacios no debería consultar
# SPY (FALLA)
# =====================================================
def test_prueba7_post_tipo_con_espacios_no_deberia_consultar_servicio(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_obtener(tipo_sangre):
        llamadas.append(tipo_sangre)
        return []

    monkeypatch.setattr(modulo, "obtenerSolicitudesPendientesPorTipo", fake_obtener)

    # ACT
    resp = client.post("/filtrar_solicitudes", data={"tipo_sangre": "   "})

    # ASSERT
    assert resp.status_code == 200
    assert llamadas == []

# =====================================================
# PRUEBA 8 – POST inválido no debería consultar
# SPY (FALLA)
# =====================================================
def test_prueba8_post_tipo_invalido_no_deberia_consultar_servicio(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_obtener(tipo_sangre):
        llamadas.append(tipo_sangre)
        return []

    monkeypatch.setattr(modulo, "obtenerSolicitudesPendientesPorTipo", fake_obtener)

    # ACT
    resp = client.post("/filtrar_solicitudes", data={"tipo_sangre": "XYZ"})

    # ASSERT
    assert resp.status_code == 200
    assert llamadas == []

# =====================================================
# PRUEBA 9 – POST debería normalizar valor
# SPY (FALLA)
# =====================================================
def test_prueba9_post_deberia_normalizar_tipo_sangre_minusculas(client, monkeypatch):
    # ARRANGE
    llamadas = []

    def fake_obtener(tipo_sangre):
        llamadas.append(tipo_sangre)
        return []

    monkeypatch.setattr(modulo, "obtenerSolicitudesPendientesPorTipo", fake_obtener)

    # ACT
    resp = client.post("/filtrar_solicitudes", data={"tipo_sangre": "o+"})

    # ASSERT
    assert resp.status_code == 200
    assert llamadas == ["O+"]