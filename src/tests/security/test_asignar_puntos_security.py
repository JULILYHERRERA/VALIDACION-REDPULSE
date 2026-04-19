import pytest
import sys
import os
import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =====================================================
# SEGURIDAD 1 – Input no numérico 
# =====================================================
def test_seguridad_input_no_numerico(client):

    with client.session_transaction() as sess:
        sess["user_data"] = {"enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "111",
            "tipo_cedula_usuario": "CC"
        }

    with pytest.raises(ValueError):
        client.post("/asignar_puntos", data={"puntos": "abc"})


# =====================================================
# SEGURIDAD 2 – Puntos negativos (el sistema los permite)
# =====================================================
def test_seguridad_puntos_negativos(client, monkeypatch):

    class UsuarioFake:
        puntos = 100

    monkeypatch.setattr(app, "obtenerUsuarioPorDocumento",
                        lambda d, t: UsuarioFake())
    monkeypatch.setattr(app, "actualizarPuntos", lambda *a: None)

    with client.session_transaction() as sess:
        sess["user_data"] = {"enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "111",
            "tipo_cedula_usuario": "CC"
        }

    resp = client.post("/asignar_puntos", data={"puntos": "-50"})

    # ✔ El sistema lo permite → redirige
    assert resp.status_code in (301, 302)


# =====================================================
# SEGURIDAD 3 – Sin datos en sesión → DEBE FALLAR
# =====================================================
def test_seguridad_sin_datos_usuario(client):

    with client.session_transaction() as sess:
        sess["user_data"] = {"enfermero": True}
        # ❌ Falta enfermero_usuario_obtenido

    # 🔥 Va a romper porque hace ['cedula_usuario'] sobre None
    with pytest.raises(TypeError):
        client.post("/asignar_puntos", data={"puntos": "50"})


# =====================================================
# SEGURIDAD 4 – Puntos extremadamente grandes
# =====================================================
def test_seguridad_puntos_grandes(client, monkeypatch):

    class UsuarioFake:
        puntos = 100

    monkeypatch.setattr(app, "obtenerUsuarioPorDocumento",
                        lambda d, t: UsuarioFake())
    monkeypatch.setattr(app, "actualizarPuntos", lambda *a: None)

    with client.session_transaction() as sess:
        sess["user_data"] = {"enfermero": True}
        sess["enfermero_usuario_obtenido"] = {
            "cedula_usuario": "111",
            "tipo_cedula_usuario": "CC"
        }

    resp = client.post("/asignar_puntos", data={"puntos": "999999999"})

    assert resp.status_code in (301, 302)


# =====================================================
# SEGURIDAD 5 – Usuario no autenticado
# =====================================================
def test_seguridad_sin_autenticacion(client):

    resp = client.post("/asignar_puntos", data={"puntos": "50"}, follow_redirects=False)

    assert resp.status_code in (301, 302)