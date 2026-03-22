import pytest
import sys
import os

# Configuración de path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import controladores.solicitudes_pendientes_controlador as modulo
from servicios.notificaciones_servicio import notificaciones_data

# =====================================================
# PRUEBA 1: No hay escasez -> Solo notifica solicitante
# =====================================================
def test_notificaciones_sin_escasez(monkeypatch):
    # --- ARRANGE ---
    # Stubs para datos de usuario y stock alto (2000 = No escasez)
    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: ("111", "CC"))
    monkeypatch.setattr(modulo, "obtenerCorreoUsuario", lambda a, b: "user@mail.com")
    monkeypatch.setattr(modulo, "obtenerCantidadSangreDonada", lambda x: 2000)

    # Espía para contar llamadas
    llamadas = {"solicitante": 0, "donante": 0, "admin": 0}

    # Mock de los métodos de la clase Notificaciones (evita envío de email real)
    monkeypatch.setattr(modulo.email, "solicitud_notificacion",
                        lambda para_email, estado: llamadas.update({"solicitante": llamadas["solicitante"] + 1}))
    
    monkeypatch.setattr(modulo.email, "parametros_notificacion_donante",
                        lambda para_email, tipo: llamadas.update({"donante": llamadas["donante"] + 1}))

    monkeypatch.setattr(modulo.email, "parametros_notificacion_admin",
                        lambda tipo: llamadas.update({"admin": llamadas["admin"] + 1}))

    # --- ACT ---
    modulo.verificarNivelesDeSangre(1, "Aprobado", "O+")

    # --- ASSERT ---
    assert llamadas["solicitante"] == 1
    assert llamadas["donante"] == 0
    assert llamadas["admin"] == 0


# =====================================================
# PRUEBA 2: Escasez y un donante -> Verifica Email y Guardado en Memoria
# =====================================================
def test_notificaciones_escasez_un_donante(monkeypatch):
    # --- ARRANGE ---
    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: ("111", "CC"))
    monkeypatch.setattr(modulo, "obtenerCorreoUsuario", lambda a, b: "user@mail.com")
    monkeypatch.setattr(modulo, "obtenerCantidadSangreDonada", lambda x: 500) # Escasez
    monkeypatch.setattr(modulo, "obtenerCorreosDonantesTipoSangreEspecifico", lambda x: ["donante1@mail.com"])

    email_enviado_a_donante = []
    
    # Mock de la clase Notificaciones
    # Simulamos el comportamiento de 'parametros_notificacion_donante'
    def mock_donante(para_email, tipo_sangre):
        email_enviado_a_donante.append(para_email)
        # Importante: Aquí podrías también mockear 'agregar_notificacion' 
        # si quieres verificar la persistencia en notificaciones_data

    monkeypatch.setattr(modulo.email, "solicitud_notificacion", lambda *a: None)
    monkeypatch.setattr(modulo.email, "parametros_notificacion_donante", mock_donante)
    monkeypatch.setattr(modulo.email, "parametros_notificacion_admin", lambda *a: None)

    # --- ACT ---
    modulo.verificarNivelesDeSangre(1, "Aprobado", "O+")

    # --- ASSERT ---
    assert "donante1@mail.com" in email_enviado_a_donante


# =====================================================
# PRUEBA 3: Escasez y varios donantes (Bucle de notificaciones)
# =====================================================
def test_notificaciones_escasez_varios_donantes(monkeypatch):
    # --- ARRANGE ---
    donantes_lista = ["d1@mail.com", "d2@mail.com", "d3@mail.com"]
    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: ("111", "CC"))
    monkeypatch.setattr(modulo, "obtenerCorreoUsuario", lambda a, b: "user@mail.com")
    monkeypatch.setattr(modulo, "obtenerCantidadSangreDonada", lambda x: 500)
    monkeypatch.setattr(modulo, "obtenerCorreosDonantesTipoSangreEspecifico", lambda x: donantes_lista)

    donantes_notificados = []

    monkeypatch.setattr(modulo.email, "solicitud_notificacion", lambda *a: None)
    monkeypatch.setattr(modulo.email, "parametros_notificacion_admin", lambda *a: None)
    
    # Mock para capturar a quiénes se les intenta enviar notificación
    monkeypatch.setattr(modulo.email, "parametros_notificacion_donante", 
                        lambda email, tipo: donantes_notificados.append(email))

    # --- ACT ---
    modulo.verificarNivelesDeSangre(1, "Aprobado", "O+")

    # --- ASSERT ---
    assert len(donantes_notificados) == 3
    assert set(donantes_notificados) == set(donantes_lista)


# =====================================================
# PRUEBA 4: Escasez pero no hay donantes (Solo Admin)
# =====================================================
def test_notificaciones_escasez_sin_donantes(monkeypatch):
    # --- ARRANGE ---
    monkeypatch.setattr(modulo, "obtenerUsuarioPorRegistro", lambda x: ("111", "CC"))
    monkeypatch.setattr(modulo, "obtenerCorreoUsuario", lambda a, b: "user@mail.com")
    monkeypatch.setattr(modulo, "obtenerCantidadSangreDonada", lambda x: 500)
    monkeypatch.setattr(modulo, "obtenerCorreosDonantesTipoSangreEspecifico", lambda x: [])

    llamadas_admin = []

    monkeypatch.setattr(modulo.email, "solicitud_notificacion", lambda *a: None)
    monkeypatch.setattr(modulo.email, "parametros_notificacion_donante", lambda *a: None)
    monkeypatch.setattr(modulo.email, "parametros_notificacion_admin", 
                        lambda tipo: llamadas_admin.append(tipo))

    # --- ACT ---
    modulo.verificarNivelesDeSangre(1, "Aprobado", "O+")

    # --- ASSERT ---
    assert len(llamadas_admin) == 1
    assert "O+" in llamadas_admin[0]