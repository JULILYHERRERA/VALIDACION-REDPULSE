import sys
import os
import pytest

# Esto le dice a Python: "Sube un nivel y busca ahí las carpetas del proyecto"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import servicios.registro_servicio as modulo

# Clase base para simular el usuario de la BD
class UsuarioFake:
    def __init__(self, donante, puntos, total_donado):
        self.donante = donante
        self.puntos = puntos
        self.total_donado = total_donado
        self.tipo_de_sangre = "O+"

# ============================================
# PRUEBA 1: Usuario YA es donante
# ============================================
def test_insertar_donacion_usuario_ya_donante(monkeypatch):
    # ARRANGE
    puntos_iniciales = 1000
    usuario_fake = UsuarioFake(donante=True, puntos=puntos_iniciales, total_donado=500)

    monkeypatch.setattr(modulo, "obtenerUsuarioPorDocumento", lambda doc, tipo: usuario_fake)
    
    # Spy para verificar que NO se llame a actualizarEstadoDonante
    llamadas_estado = {"count": 0}
    def mock_estado(d, t): llamadas_estado["count"] += 1
    monkeypatch.setattr(modulo, "actualizarEstadoDonante", mock_estado)

    monkeypatch.setattr(modulo, "insertarRegistro", lambda r: None)
    monkeypatch.setattr(modulo, "actualizarCantidadDonada", lambda d, t, c: None)

    # ACT - Se quita puntos_asignados porque la función no lo recibe
    resultado = modulo.insertarDonacion("111", "CC", "2024-01-01", 450)

    # ASSERT
    assert resultado is True
    assert llamadas_estado["count"] == 0 


# ============================================
# PRUEBA 2: Usuario NO es donante (Primera vez)
# ============================================
def test_insertar_donacion_usuario_nuevo_donante(monkeypatch):
    # ARRANGE
    usuario_fake = UsuarioFake(donante=False, puntos=0, total_donado=0)

    monkeypatch.setattr(modulo, "obtenerUsuarioPorDocumento", lambda doc, tipo: usuario_fake)
    
    llamadas_estado = {"count": 0}
    def mock_estado(d, t): llamadas_estado["count"] += 1
    monkeypatch.setattr(modulo, "actualizarEstadoDonante", mock_estado)

    monkeypatch.setattr(modulo, "insertarRegistro", lambda r: None)
    monkeypatch.setattr(modulo, "actualizarCantidadDonada", lambda d, t, c: None)

    # ACT - Se quita puntos_asignados
    resultado = modulo.insertarDonacion("222", "CC", "2024-01-01", 450)

    # ASSERT
    assert resultado is True
    assert llamadas_estado["count"] == 1 


# ============================================
# PRUEBA 3: Puntos negativos
# ============================================
def test_puntos_son_negativos(monkeypatch):
    # ARRANGE
    usuario_fake = UsuarioFake(True, 1000, 500)
    monkeypatch.setattr(modulo, "obtenerUsuarioPorDocumento", lambda d, t: usuario_fake)
    monkeypatch.setattr(modulo, "insertarRegistro", lambda r: None)
    monkeypatch.setattr(modulo, "actualizarCantidadDonada", lambda d, t, c: None)

    # ACT
    resultado = modulo.insertarDonacion("111", "CC", "2024-01-01", -100)

    # ASSERT 
    assert resultado is False  


# ============================================
# PRUEBA 4: No numéros en puntos
# ============================================
def test_falla_si_cantidad_no_numerica(monkeypatch):
    # ARRANGE
    usuario_fake = UsuarioFake(True, 1000, 500)
    monkeypatch.setattr(modulo, "obtenerUsuarioPorDocumento", lambda d, t: usuario_fake)
    monkeypatch.setattr(modulo, "insertarRegistro", lambda r: None)
    monkeypatch.setattr(modulo, "actualizarCantidadDonada", lambda d, t, c: None)

    # ACT
    resultado = modulo.insertarDonacion("111", "CC", "2024-01-01", "abc")

    # ASSERT
    assert resultado is False   