# Controla el flujo de donaciones dependiendo la cantidad de sangre que haya
import sys
sys.path.append("src")

# Base de datos
from servicios.BaseDeDatos.usuario_bd_servicio import *
from servicios.BaseDeDatos.registro_bd_servicio import *

#email
from servicios.notificaciones_servicio import *
email = Notificaciones()

CNT_SANGRE_MINIMA = 1000

def verificarNivelesDeSangre(solicitud_id, accion, tipo_sangre_solicitud):
    usuario_solicitud = obtenerUsuarioPorRegistro(solicitud_id)
    correo_usuario = obtenerCorreoUsuario(usuario_solicitud[0], usuario_solicitud[1])
    email.solicitud_notificacion(correo_usuario, accion)

    cnt_sangre_solicitud = obtenerCantidadSangreDonada(tipo_sangre_solicitud)

    if cnt_sangre_solicitud < CNT_SANGRE_MINIMA and accion == 'Aprobado':
        correos_usuario = obtenerCorreosDonantesTipoSangreEspecifico(tipo_sangre_solicitud)

        for correo in correos_usuario:
            email.parametros_notificacion_donante(correo, tipo_sangre_solicitud)

        email.parametros_notificacion_admin(tipo_sangre_solicitud)