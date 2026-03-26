# Importar metodo para actualizar la sesion del usuario
from servicios.sesion_servicio import actualizarUsuarioSesion

# Importar el metodo para actualizar los puntos en la base de datos.
from servicios.BaseDeDatos.usuario_bd_servicio import actualizarPuntos

# Importando session
from flask import session

#Misc
import secrets

# email
from servicios.notificaciones_servicio import Notificaciones
email = Notificaciones()

def procesar_puntos(puntos_seleccionados: int):
    # Obtener datos y actualizar en la session y base de datos
    user_data = session.get('user_data')
    if not user_data:
        return False

    puntos_usuario = user_data.get('puntos', 0)
    numero_documento = user_data.get('numero_documento')
    tipo_de_documento = user_data.get('tipo_documento')
    correo_usuario = user_data.get('correo')

    if not all([numero_documento, tipo_de_documento, correo_usuario]):
        return False

    # Verificar si el usuario tiene suficientes puntos para realizar la compra
    puntos_restantes = (puntos_usuario - puntos_seleccionados)

    if puntos_restantes >= 0:
        actualizarUsuarioSesion('puntos', puntos_restantes)
        actualizarPuntos(numero_documento, tipo_de_documento, puntos_restantes)
        
        # Solo se genera código de redención si la actualización fue exitosa
        codigo_redencion = secrets.token_urlsafe(16)
        email.redimir_puntos_notificacion(correo_usuario, codigo_redencion)

        return True
    return False