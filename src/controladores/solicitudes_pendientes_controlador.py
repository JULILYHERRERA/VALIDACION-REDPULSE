# Controla el flujo de donaciones dependiendo la cantidad de sangre que haya
import sys
sys.path.append("src")

# Base de datos
from servicios.BaseDeDatos.usuario_bd_servicio import obtenerUsuarioPorDocumento, obtenerCorreosDonantesTipoSangreEspecifico, obtenerCorreoUsuario
from servicios.BaseDeDatos.registro_bd_servicio import obtenerUsuarioPorRegistro, obtenerCantidadSangreDonada

# email
from servicios.notificaciones_servicio import Notificaciones, agregar_notificacion
email = Notificaciones()

CNT_SANGRE_MINIMA = 1000

def verificarNivelesDeSangre(solicitud_id, accion, tipo_sangre_solicitud):
    usuario_solicitud = obtenerUsuarioPorRegistro(solicitud_id)
    correo_usuario = obtenerCorreoUsuario(usuario_solicitud[0], usuario_solicitud[1])
    email.solicitud_notificacion(correo_usuario, accion)

    cnt_sangre_solicitud = obtenerCantidadSangreDonada(tipo_sangre_solicitud)
    
    if cnt_sangre_solicitud < CNT_SANGRE_MINIMA and accion == 'Aprobado':
        mensaje = f"Hay escasez de sangre {tipo_sangre_solicitud}. Revisar su correo para más detalles."
        correos_usuario = obtenerCorreosDonantesTipoSangreEspecifico(tipo_sangre_solicitud)

        for correo in correos_usuario:
            email.parametros_notificacion_donante(correo, tipo_sangre_solicitud)
            agregar_notificacion(correo,mensaje)
        email.parametros_notificacion_admin(tipo_sangre_solicitud)