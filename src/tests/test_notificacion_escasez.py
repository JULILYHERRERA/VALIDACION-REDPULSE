import pytest
import sys
import os

# Agrega src al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# IMPORTA TU CONTROLADOR AQUÍ (CAMBIA EL NOMBRE SI ES NECESARIO)
import controladores.solicitudes_pendientes_controlador as modulo


# =====================================================
# PRUEBA 1
# No hay escasez -> solo notifica solicitante
# =====================================================
def test_notificaciones_sin_escasez(monkeypatch):

    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: ("111", "CC"))
    monkeypatch.setattr(modulo, "obtenerCorreoUsuario", lambda a, b: "user@mail.com")
    monkeypatch.setattr(modulo, "obtenerCantidadSangreDonada", lambda x: 2000)  # No escasez

    llamadas = {"solicitante": 0, "donante": 0, "admin": 0}

    monkeypatch.setattr(modulo.email, "solicitud_notificacion",
                        lambda *args: llamadas.update({"solicitante": llamadas["solicitante"] + 1}))

    monkeypatch.setattr(modulo.email, "parametros_notificacion_donante",
                        lambda *args: llamadas.update({"donante": llamadas["donante"] + 1}))

    monkeypatch.setattr(modulo.email, "parametros_notificacion_admin",
                        lambda *args: llamadas.update({"admin": llamadas["admin"] + 1}))

    modulo.verificarNivelesDeSangre(1, "Aprobado", "O+")

    assert llamadas["solicitante"] == 1
    assert llamadas["donante"] == 0
    assert llamadas["admin"] == 0


# =====================================================
# PRUEBA 2
# Escasez y un donante
# =====================================================
def test_notificaciones_escasez_un_donante(monkeypatch):

    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: ("111", "CC"))
    monkeypatch.setattr(modulo, "obtenerCorreoUsuario", lambda a, b: "user@mail.com")
    monkeypatch.setattr(modulo, "obtenerCantidadSangreDonada", lambda x: 500)  # Escasez
    monkeypatch.setattr(modulo, "obtenerCorreosDonantesTipoSangreEspecifico",
                        lambda x: ["donante1@mail.com"])

    llamadas = {"donante": 0, "admin": 0}

    monkeypatch.setattr(modulo.email, "solicitud_notificacion", lambda *args: None)

    monkeypatch.setattr(modulo.email, "parametros_notificacion_donante",
                        lambda *args: llamadas.update({"donante": llamadas["donante"] + 1}))

    monkeypatch.setattr(modulo.email, "parametros_notificacion_admin",
                        lambda *args: llamadas.update({"admin": llamadas["admin"] + 1}))

    modulo.verificarNivelesDeSangre(1, "Aprobado", "O+")

    assert llamadas["donante"] == 1
    assert llamadas["admin"] == 1


# =====================================================
# PRUEBA 3
# Escasez y varios donantes (bucle)
# =====================================================
def test_notificaciones_escasez_varios_donantes(monkeypatch):

    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: ("111", "CC"))
    monkeypatch.setattr(modulo, "obtenerCorreoUsuario", lambda a, b: "user@mail.com")
    monkeypatch.setattr(modulo, "obtenerCantidadSangreDonada", lambda x: 500)
    monkeypatch.setattr(modulo, "obtenerCorreosDonantesTipoSangreEspecifico",
                        lambda x: ["d1@mail.com", "d2@mail.com", "d3@mail.com"])

    llamadas = {"donante": 0}

    monkeypatch.setattr(modulo.email, "solicitud_notificacion", lambda *args: None)

    monkeypatch.setattr(modulo.email, "parametros_notificacion_donante",
                        lambda *args: llamadas.update({"donante": llamadas["donante"] + 1}))

    monkeypatch.setattr(modulo.email, "parametros_notificacion_admin", lambda *args: None)

    modulo.verificarNivelesDeSangre(1, "Aprobado", "O+")

    assert llamadas["donante"] == 3


# =====================================================
# PRUEBA 4
# Escasez pero no hay donantes
# =====================================================
def test_notificaciones_escasez_sin_donantes(monkeypatch):

    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: ("111", "CC"))
    monkeypatch.setattr(modulo, "obtenerCorreoUsuario", lambda a, b: "user@mail.com")
    monkeypatch.setattr(modulo, "obtenerCantidadSangreDonada", lambda x: 500)
    monkeypatch.setattr(modulo, "obtenerCorreosDonantesTipoSangreEspecifico",
                        lambda x: [])

    llamadas = {"admin": 0}

    monkeypatch.setattr(modulo.email, "solicitud_notificacion", lambda *args: None)
    monkeypatch.setattr(modulo.email, "parametros_notificacion_donante", lambda *args: None)

    monkeypatch.setattr(modulo.email, "parametros_notificacion_admin",
                        lambda *args: llamadas.update({"admin": llamadas["admin"] + 1}))

    modulo.verificarNivelesDeSangre(1, "Aprobado", "O+")

    assert llamadas["admin"] == 1