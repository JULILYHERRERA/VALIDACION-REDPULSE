import os
import sys

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import controladores.puntos_controlador as puntos_ctrl
import servicios.sesion_servicio as sesion_svc
from app import app

# Contrato de la ruta `puntos` (app.py): JSON con esta clave; respuesta `success` y `nuevos_puntos`.
JSON_REDIMIR_2000 = {"puntos_seleccionados": 2000}

# =====================================================
# PRUEBA 1 – Sin sesión redirige a home
# =====================================================
def test_prueba1_sin_sesion_redirige_a_home(client):
    resp = client.post("/puntos", json=JSON_REDIMIR_2000, follow_redirects=False)

    assert resp.status_code in (301, 302)
    assert resp.headers.get("Location") is not None

# =====================================================
# PRUEBA 2 – Donante con puntos suficientes: success True y saldo en JSON
# Stubs en el controlador (BD, correo, token); sesión real vía actualizarUsuarioSesion
# =====================================================
def test_prueba2_donante_con_puntos_suficientes_retorna_true(client, monkeypatch):
    monkeypatch.setattr(puntos_ctrl, "actualizarPuntos", lambda doc, tipo, pts: None)
    monkeypatch.setattr(
        puntos_ctrl.email,
        "redimir_puntos_notificacion",
        lambda correo, codigo: None,
    )
    monkeypatch.setattr(
        puntos_ctrl.secrets,
        "token_urlsafe",
        lambda n: "codigo-fake-123",
    )

    with client.session_transaction() as sess:
        sess["user_data"] = {
            "puntos": 5000,
            "numero_documento": "123456789",
            "tipo_documento": "CC",
            "correo": "donante@ejemplo.com",
        }

    resp = client.post("/puntos", json=JSON_REDIMIR_2000)

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["nuevos_puntos"] == 3000

# =====================================================
# PRUEBA 3 – Descuento reflejado en sesión (spy + delegación al servicio real)
# =====================================================
def test_prueba3_donante_con_puntos_suficientes_descuenta_puntos_en_sesion(
    client, monkeypatch
):
    llamadas_sesion = []
    _real_actualizar = sesion_svc.actualizarUsuarioSesion

    def spy_actualizar(campo, valor):
        llamadas_sesion.append((campo, valor))
        return _real_actualizar(campo, valor)

    monkeypatch.setattr(puntos_ctrl, "actualizarUsuarioSesion", spy_actualizar)
    monkeypatch.setattr(puntos_ctrl, "actualizarPuntos", lambda doc, tipo, pts: None)
    monkeypatch.setattr(
        puntos_ctrl.email,
        "redimir_puntos_notificacion",
        lambda correo, codigo: None,
    )
    monkeypatch.setattr(
        puntos_ctrl.secrets,
        "token_urlsafe",
        lambda n: "codigo-fake-123",
    )

    with client.session_transaction() as sess:
        sess["user_data"] = {
            "puntos": 5000,
            "numero_documento": "123456789",
            "tipo_documento": "CC",
            "correo": "donante@ejemplo.com",
        }

    client.post("/puntos", json=JSON_REDIMIR_2000)

    assert len(llamadas_sesion) == 1
    assert llamadas_sesion[0] == ("puntos", 3000)

# =====================================================
# PRUEBA 4 – Persistencia en BD invocada con documento y saldo final
# =====================================================
def test_prueba4_donante_con_puntos_suficientes_persiste_puntos_en_base_de_datos(
    client, monkeypatch
):
    llamadas_bd = []

    monkeypatch.setattr(
        puntos_ctrl,
        "actualizarPuntos",
        lambda doc, tipo, pts: llamadas_bd.append((doc, tipo, pts)),
    )
    monkeypatch.setattr(
        puntos_ctrl.email,
        "redimir_puntos_notificacion",
        lambda correo, codigo: None,
    )
    monkeypatch.setattr(
        puntos_ctrl.secrets,
        "token_urlsafe",
        lambda n: "codigo-fake-123",
    )

    with client.session_transaction() as sess:
        sess["user_data"] = {
            "puntos": 5000,
            "numero_documento": "123456789",
            "tipo_documento": "CC",
            "correo": "donante@ejemplo.com",
        }

    client.post("/puntos", json=JSON_REDIMIR_2000)

    assert len(llamadas_bd) == 1
    assert llamadas_bd[0] == ("123456789", "CC", 3000)

# =====================================================
# PRUEBA 5 – Notificación de redención al correo del donante
# =====================================================
def test_prueba5_donante_con_puntos_suficientes_recibe_notificacion_por_correo(
    client, monkeypatch
):
    llamadas_email = []

    monkeypatch.setattr(puntos_ctrl, "actualizarPuntos", lambda doc, tipo, pts: None)
    monkeypatch.setattr(
        puntos_ctrl.email,
        "redimir_puntos_notificacion",
        lambda correo, codigo: llamadas_email.append((correo, codigo)),
    )
    monkeypatch.setattr(
        puntos_ctrl.secrets,
        "token_urlsafe",
        lambda n: "codigo-fake-123",
    )

    with client.session_transaction() as sess:
        sess["user_data"] = {
            "puntos": 5000,
            "numero_documento": "123456789",
            "tipo_documento": "CC",
            "correo": "donante@ejemplo.com",
        }

    client.post("/puntos", json=JSON_REDIMIR_2000)

    assert len(llamadas_email) == 1
    assert llamadas_email[0] == ("donante@ejemplo.com", "codigo-fake-123")

# =====================================================
# PRUEBA 6 – Sin puntos suficientes: success False, saldo sin cambio en JSON
# =====================================================
def test_prueba6_donante_sin_puntos_suficientes_retorna_false(client, monkeypatch):
    monkeypatch.setattr(puntos_ctrl, "actualizarPuntos", lambda doc, tipo, pts: None)
    monkeypatch.setattr(
        puntos_ctrl.email,
        "redimir_puntos_notificacion",
        lambda correo, codigo: None,
    )

    with client.session_transaction() as sess:
        sess["user_data"] = {
            "puntos": 1000,
            "numero_documento": "123456789",
            "tipo_documento": "CC",
            "correo": "donante@ejemplo.com",
        }

    resp = client.post("/puntos", json=JSON_REDIMIR_2000)

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is False
    assert data["nuevos_puntos"] == 1000

# =====================================================
# PRUEBA 7 – Sin puntos suficientes: no sesión ni BD
# =====================================================
def test_prueba7_donante_sin_puntos_suficientes_no_modifica_sesion_ni_bd(
    client, monkeypatch
):
    llamadas_sesion = []
    llamadas_bd = []

    monkeypatch.setattr(
        puntos_ctrl,
        "actualizarUsuarioSesion",
        lambda campo, valor: llamadas_sesion.append((campo, valor)),
    )
    monkeypatch.setattr(
        puntos_ctrl,
        "actualizarPuntos",
        lambda doc, tipo, pts: llamadas_bd.append((doc, tipo, pts)),
    )
    monkeypatch.setattr(
        puntos_ctrl.email,
        "redimir_puntos_notificacion",
        lambda correo, codigo: None,
    )

    with client.session_transaction() as sess:
        sess["user_data"] = {
            "puntos": 1000,
            "numero_documento": "123456789",
            "tipo_documento": "CC",
            "correo": "donante@ejemplo.com",
        }

    client.post("/puntos", json=JSON_REDIMIR_2000)

    assert llamadas_sesion == []
    assert llamadas_bd == []

# =====================================================
# PRUEBA 8 – Sin puntos suficientes: no correo de redención
# =====================================================
def test_prueba8_donante_sin_puntos_suficientes_no_recibe_notificacion(
    client, monkeypatch
):
    llamadas_email = []

    monkeypatch.setattr(puntos_ctrl, "actualizarPuntos", lambda doc, tipo, pts: None)
    monkeypatch.setattr(
        puntos_ctrl.email,
        "redimir_puntos_notificacion",
        lambda correo, codigo: llamadas_email.append((correo, codigo)),
    )

    with client.session_transaction() as sess:
        sess["user_data"] = {
            "puntos": 1000,
            "numero_documento": "123456789",
            "tipo_documento": "CC",
            "correo": "donante@ejemplo.com",
        }

    client.post("/puntos", json=JSON_REDIMIR_2000)

    assert llamadas_email == []

# =====================================================
# PRUEBA 9 – Borde: saldo igual al costo → queda en 0
# =====================================================
def test_prueba9_donante_con_puntos_exactos_puede_redimir_y_queda_en_cero(
    client, monkeypatch
):
    llamadas_sesion = []
    _real_actualizar = sesion_svc.actualizarUsuarioSesion

    def spy_actualizar(campo, valor):
        llamadas_sesion.append((campo, valor))
        return _real_actualizar(campo, valor)

    monkeypatch.setattr(puntos_ctrl, "actualizarUsuarioSesion", spy_actualizar)
    monkeypatch.setattr(puntos_ctrl, "actualizarPuntos", lambda doc, tipo, pts: None)
    monkeypatch.setattr(
        puntos_ctrl.email,
        "redimir_puntos_notificacion",
        lambda correo, codigo: None,
    )
    monkeypatch.setattr(
        puntos_ctrl.secrets,
        "token_urlsafe",
        lambda n: "codigo-fake-123",
    )

    with client.session_transaction() as sess:
        sess["user_data"] = {
            "puntos": 2000,
            "numero_documento": "123456789",
            "tipo_documento": "CC",
            "correo": "donante@ejemplo.com",
        }

    resp = client.post("/puntos", json=JSON_REDIMIR_2000)

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["nuevos_puntos"] == 0
    assert llamadas_sesion[0] == ("puntos", 0)

# =====================================================
# PRUEBA 10 – POST sin clave `puntos_seleccionados` retorna 400
# =====================================================
def test_prueba10_post_json_sin_puntos_seleccionados_retorna_400(client):
    with client.session_transaction() as sess:
        sess["user_data"] = {
            "puntos": 5000,
            "numero_documento": "1",
            "tipo_documento": "CC",
            "correo": "a@b.c",
        }

    resp = client.post("/puntos", json={"puntos": 2000})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["success"] is False
    assert data["error"] == "Datos incompletos"
