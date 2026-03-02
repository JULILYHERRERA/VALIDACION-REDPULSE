import sys
import os

# Agrega la carpeta src al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import servicios.registro_servicio as modulo


# ============================================
# PRUEBA 1
# Usuario YA es donante → Solo suma puntos
# ============================================
def test_insertar_donacion_usuario_ya_donante(monkeypatch):

    # Usuario simulado
    class UsuarioFake:
        donante = True
        tipo_de_sangre = "O+"
        puntos = 1000
        total_donado = 500

    # Mock obtener usuario
    monkeypatch.setattr(modulo, "obtenerUsuarioPorDocumento",
                        lambda doc, tipo: UsuarioFake())

    # Mock actualizar estado (NO debería llamarse)
    llamadas_estado = {"count": 0}
    def mock_actualizarEstado(doc, tipo):
        llamadas_estado["count"] += 1

    monkeypatch.setattr(modulo, "actualizarEstadoDonante", mock_actualizarEstado)

    # Mock insertar registro
    monkeypatch.setattr(modulo, "insertarRegistro", lambda registro: None)

    # Mock actualizar puntos
    puntos_actualizados = {"valor": None}
    def mock_actualizarPuntos(doc, tipo, nuevos_puntos):
        puntos_actualizados["valor"] = nuevos_puntos

    monkeypatch.setattr(modulo, "actualizarPuntos", mock_actualizarPuntos)

    # Mock actualizar cantidad donada
    monkeypatch.setattr(modulo, "actualizarCantidadDonada",
                        lambda doc, tipo, cantidad: None)

    resultado = modulo.insertarDonacion("111", "CC", "2024-01-01", 200)

    assert resultado is True
    assert llamadas_estado["count"] == 0  # No cambia estado
    assert puntos_actualizados["valor"] == 3000  # 1000 + 2000


# ============================================
# PRUEBA 2
# Usuario NO es donante → Cambia estado y suma puntos
# ============================================
def test_insertar_donacion_usuario_no_donante(monkeypatch):

    # Usuario simulado
    class UsuarioFake:
        donante = False
        tipo_de_sangre = "A+"
        puntos = 500
        total_donado = 300

    monkeypatch.setattr(modulo, "obtenerUsuarioPorDocumento",
                        lambda doc, tipo: UsuarioFake())

    # Mock actualizar estado (SÍ debe llamarse)
    llamadas_estado = {"count": 0}
    def mock_actualizarEstado(doc, tipo):
        llamadas_estado["count"] += 1

    monkeypatch.setattr(modulo, "actualizarEstadoDonante", mock_actualizarEstado)

    monkeypatch.setattr(modulo, "insertarRegistro", lambda registro: None)

    puntos_actualizados = {"valor": None}
    def mock_actualizarPuntos(doc, tipo, nuevos_puntos):
        puntos_actualizados["valor"] = nuevos_puntos

    monkeypatch.setattr(modulo, "actualizarPuntos", mock_actualizarPuntos)

    monkeypatch.setattr(modulo, "actualizarCantidadDonada",
                        lambda doc, tipo, cantidad: None)

    resultado = modulo.insertarDonacion("222", "CC", "2024-01-01", 300)

    assert resultado is True
    assert llamadas_estado["count"] == 1  # Sí cambia estado
    assert puntos_actualizados["valor"] == 2500  # 500 + 2000