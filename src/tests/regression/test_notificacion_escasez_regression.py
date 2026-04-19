import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import controladores.solicitudes_pendientes_controlador as modulo

# =====================================================
# REGRESIÓN 1 – No hay escasez (solo solicitante)
# =====================================================
def test_sin_escasez_solo_solicitante(monkeypatch):

    llamadas = {"solicitante": 0, "donante": 0, "admin": 0}

    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: ("111", "CC"))
    monkeypatch.setattr(modulo, "obtenerCorreoUsuario", lambda a, b: "user@mail.com")
    monkeypatch.setattr(modulo, "obtenerCantidadSangreDonada", lambda x: 2000)

    monkeypatch.setattr(modulo.email, "solicitud_notificacion",
                        lambda *a: llamadas.update({"solicitante": llamadas["solicitante"] + 1}))

    monkeypatch.setattr(modulo.email, "parametros_notificacion_donante",
                        lambda *a: llamadas.update({"donante": llamadas["donante"] + 1}))

    monkeypatch.setattr(modulo.email, "parametros_notificacion_admin",
                        lambda *a: llamadas.update({"admin": llamadas["admin"] + 1}))

    modulo.verificarNivelesDeSangre(1, "Aprobado", "O+")

    assert llamadas["solicitante"] == 1
    assert llamadas["donante"] == 0
    assert llamadas["admin"] == 0


# =====================================================
# REGRESIÓN 2 – Escasez con un donante
# =====================================================
def test_escasez_un_donante(monkeypatch):

    enviados = []

    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: ("111", "CC"))
    monkeypatch.setattr(modulo, "obtenerCorreoUsuario", lambda a, b: "user@mail.com")
    monkeypatch.setattr(modulo, "obtenerCantidadSangreDonada", lambda x: 500)
    monkeypatch.setattr(modulo, "obtenerCorreosDonantesTipoSangreEspecifico",
                        lambda x: ["donante@mail.com"])

    monkeypatch.setattr(modulo.email, "solicitud_notificacion", lambda *a: None)
    monkeypatch.setattr(modulo.email, "parametros_notificacion_admin", lambda *a: None)

    monkeypatch.setattr(modulo.email, "parametros_notificacion_donante",
                        lambda correo, tipo: enviados.append(correo))

    modulo.verificarNivelesDeSangre(1, "Aprobado", "O+")

    assert "donante@mail.com" in enviados


# =====================================================
# REGRESIÓN 3 – Escasez con múltiples donantes
# =====================================================
def test_escasez_varios_donantes(monkeypatch):

    lista = ["d1@mail.com", "d2@mail.com", "d3@mail.com"]
    enviados = []

    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: ("111", "CC"))
    monkeypatch.setattr(modulo, "obtenerCorreoUsuario", lambda a, b: "user@mail.com")
    monkeypatch.setattr(modulo, "obtenerCantidadSangreDonada", lambda x: 500)
    monkeypatch.setattr(modulo, "obtenerCorreosDonantesTipoSangreEspecifico",
                        lambda x: lista)

    monkeypatch.setattr(modulo.email, "solicitud_notificacion", lambda *a: None)
    monkeypatch.setattr(modulo.email, "parametros_notificacion_admin", lambda *a: None)

    monkeypatch.setattr(modulo.email, "parametros_notificacion_donante",
                        lambda correo, tipo: enviados.append(correo))

    modulo.verificarNivelesDeSangre(1, "Aprobado", "O+")

    assert len(enviados) == 3
    assert set(enviados) == set(lista)


# =====================================================
# REGRESIÓN 4 – Escasez sin donantes (solo admin)
# =====================================================
def test_escasez_sin_donantes(monkeypatch):

    admin_llamado = []

    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: ("111", "CC"))
    monkeypatch.setattr(modulo, "obtenerCorreoUsuario", lambda a, b: "user@mail.com")
    monkeypatch.setattr(modulo, "obtenerCantidadSangreDonada", lambda x: 500)
    monkeypatch.setattr(modulo, "obtenerCorreosDonantesTipoSangreEspecifico",
                        lambda x: [])

    monkeypatch.setattr(modulo.email, "solicitud_notificacion", lambda *a: None)
    monkeypatch.setattr(modulo.email, "parametros_notificacion_donante", lambda *a: None)

    monkeypatch.setattr(modulo.email, "parametros_notificacion_admin",
                        lambda tipo: admin_llamado.append(tipo))

    modulo.verificarNivelesDeSangre(1, "Aprobado", "O+")

    assert len(admin_llamado) == 1


# =====================================================
# REGRESIÓN 5 – Acción NO aprobada (no hay escasez lógica)
# =====================================================
def test_accion_no_aprobada(monkeypatch):

    llamadas = {"donante": 0, "admin": 0}

    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: ("111", "CC"))
    monkeypatch.setattr(modulo, "obtenerCorreoUsuario", lambda a, b: "user@mail.com")
    monkeypatch.setattr(modulo, "obtenerCantidadSangreDonada", lambda x: 100)

    monkeypatch.setattr(modulo.email, "solicitud_notificacion", lambda *a: None)

    monkeypatch.setattr(modulo.email, "parametros_notificacion_donante",
                        lambda *a: llamadas.update({"donante": llamadas["donante"] + 1}))

    monkeypatch.setattr(modulo.email, "parametros_notificacion_admin",
                        lambda *a: llamadas.update({"admin": llamadas["admin"] + 1}))

    modulo.verificarNivelesDeSangre(1, "Rechazado", "O+")

    assert llamadas["donante"] == 0
    assert llamadas["admin"] == 0


# =====================================================
# REGRESIÓN 6 – Límite exacto (1000 NO es escasez)
# =====================================================
def test_limite_exacto_no_escasez(monkeypatch):

    llamadas = {"donante": 0}

    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: ("111", "CC"))
    monkeypatch.setattr(modulo, "obtenerCorreoUsuario", lambda a, b: "user@mail.com")
    monkeypatch.setattr(modulo, "obtenerCantidadSangreDonada", lambda x: 1000)

    monkeypatch.setattr(modulo.email, "solicitud_notificacion", lambda *a: None)

    monkeypatch.setattr(modulo.email, "parametros_notificacion_donante",
                        lambda *a: llamadas.update({"donante": llamadas["donante"] + 1}))

    monkeypatch.setattr(modulo.email, "parametros_notificacion_admin", lambda *a: None)

    modulo.verificarNivelesDeSangre(1, "Aprobado", "O+")

    assert llamadas["donante"] == 0


# =====================================================
# REGRESIÓN 7 – Verifica guardado de notificación
# =====================================================
def test_guardado_notificacion(monkeypatch):

    guardadas = []

    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: ("111", "CC"))
    monkeypatch.setattr(modulo, "obtenerCorreoUsuario", lambda a, b: "user@mail.com")
    monkeypatch.setattr(modulo, "obtenerCantidadSangreDonada", lambda x: 500)
    monkeypatch.setattr(modulo, "obtenerCorreosDonantesTipoSangreEspecifico",
                        lambda x: ["d@mail.com"])

    monkeypatch.setattr(modulo.email, "solicitud_notificacion", lambda *a: None)
    monkeypatch.setattr(modulo.email, "parametros_notificacion_admin", lambda *a: None)
    monkeypatch.setattr(modulo.email, "parametros_notificacion_donante", lambda *a: None)

    monkeypatch.setattr(modulo, "agregar_notificacion",
                        lambda correo, msg: guardadas.append((correo, msg)))

    modulo.verificarNivelesDeSangre(1, "Aprobado", "O+")

    assert len(guardadas) == 1
    assert "O+" in guardadas[0][1]