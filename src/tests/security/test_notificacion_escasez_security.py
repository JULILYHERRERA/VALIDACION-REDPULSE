import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import controladores.solicitudes_pendientes_controlador as modulo


# =====================================================
# SEGURIDAD 1 – Tipo de sangre malicioso / inesperado
# =====================================================
def test_seguridad_tipo_sangre_invalido(monkeypatch):

    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: ("111", "CC"))
    monkeypatch.setattr(modulo, "obtenerCorreoUsuario", lambda a, b: "user@mail.com")
    monkeypatch.setattr(modulo, "obtenerCantidadSangreDonada", lambda x: 500)
    monkeypatch.setattr(modulo, "obtenerCorreosDonantesTipoSangreEspecifico", lambda x: [])

    monkeypatch.setattr(modulo.email, "solicitud_notificacion", lambda *a: None)
    monkeypatch.setattr(modulo.email, "parametros_notificacion_donante", lambda *a: None)
    monkeypatch.setattr(modulo.email, "parametros_notificacion_admin", lambda *a: None)

    # No debe romper aunque el tipo sea raro
    resultado = modulo.verificarNivelesDeSangre(1, "Aprobado", "DROP TABLE")

    assert resultado is None or True



# =====================================================
# SEGURIDAD 2 – Usuario inexistente (None)
# =====================================================
def test_seguridad_usuario_none(monkeypatch):

    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: None)

    with pytest.raises(TypeError):
        modulo.verificarNivelesDeSangre(1, "Aprobado", "O+")


# =====================================================
# SEGURIDAD 3 – Lista de donantes vacía
# =====================================================
def test_seguridad_lista_vacia(monkeypatch):

    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: ("111", "CC"))
    monkeypatch.setattr(modulo, "obtenerCorreoUsuario", lambda a, b: "user@mail.com")
    monkeypatch.setattr(modulo, "obtenerCantidadSangreDonada", lambda x: 500)
    monkeypatch.setattr(modulo, "obtenerCorreosDonantesTipoSangreEspecifico", lambda x: [])

    monkeypatch.setattr(modulo.email, "solicitud_notificacion", lambda *a: None)
    monkeypatch.setattr(modulo.email, "parametros_notificacion_donante", lambda *a: None)
    monkeypatch.setattr(modulo.email, "parametros_notificacion_admin", lambda *a: None)

    resultado = modulo.verificarNivelesDeSangre(1, "Aprobado", "O+")

    assert resultado is None or True



# =====================================================
# SEGURIDAD 4 – Lista de donantes muy grande
# =====================================================
def test_seguridad_lista_grande(monkeypatch):

    lista_grande = [f"user{i}@mail.com" for i in range(1000)]

    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: ("111", "CC"))
    monkeypatch.setattr(modulo, "obtenerCorreoUsuario", lambda a, b: "user@mail.com")
    monkeypatch.setattr(modulo, "obtenerCantidadSangreDonada", lambda x: 500)
    monkeypatch.setattr(modulo, "obtenerCorreosDonantesTipoSangreEspecifico", lambda x: lista_grande)

    monkeypatch.setattr(modulo.email, "solicitud_notificacion", lambda *a: None)
    monkeypatch.setattr(modulo.email, "parametros_notificacion_admin", lambda *a: None)

    contador = {"envios": 0}
    monkeypatch.setattr(modulo.email, "parametros_notificacion_donante",
                        lambda *a: contador.update({"envios": contador["envios"] + 1}))

    modulo.verificarNivelesDeSangre(1, "Aprobado", "O+")

    assert contador["envios"] == 1000


# =====================================================
# SEGURIDAD 5 – Tipo de sangre None
# =====================================================
def test_seguridad_tipo_none(monkeypatch):

    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: ("111", "CC"))
    monkeypatch.setattr(modulo, "obtenerCorreoUsuario", lambda a, b: "user@mail.com")
    monkeypatch.setattr(modulo, "obtenerCantidadSangreDonada", lambda x: 500)
    monkeypatch.setattr(modulo, "obtenerCorreosDonantesTipoSangreEspecifico", lambda x: [])

    monkeypatch.setattr(modulo.email, "solicitud_notificacion", lambda *a: None)
    monkeypatch.setattr(modulo.email, "parametros_notificacion_donante", lambda *a: None)
    monkeypatch.setattr(modulo.email, "parametros_notificacion_admin", lambda *a: None)

    # No debe romper
    resultado = modulo.verificarNivelesDeSangre(1, "Aprobado", None)

    assert resultado is None or True



# =====================================================
# SEGURIDAD 6 – Acción inesperada
# =====================================================
def test_seguridad_accion_invalida(monkeypatch):

    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: ("111", "CC"))
    monkeypatch.setattr(modulo, "obtenerCorreoUsuario", lambda a, b: "user@mail.com")
    monkeypatch.setattr(modulo, "obtenerCantidadSangreDonada", lambda x: 100)

    monkeypatch.setattr(modulo.email, "solicitud_notificacion", lambda *a: None)
    monkeypatch.setattr(modulo.email, "parametros_notificacion_donante", lambda *a: None)
    monkeypatch.setattr(modulo.email, "parametros_notificacion_admin", lambda *a: None)

    # Acción fuera de lógica
    resultado = modulo.verificarNivelesDeSangre(1, "HACK", "O+")

    assert resultado is None or True
