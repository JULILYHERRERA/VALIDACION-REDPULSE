import secret_config

# Usuario.
from modelos.usuario import *

# Importando session
from flask import session

# Importando funcionalidad de registros db
from servicios.BaseDeDatos.registro_bd_servicio import obtenerUsuarioRegistros

# Importando la imagen por defecto del usuario.
url = secret_config.DEFAULT_PROFILE_PICTURE

# Funciones

def actualizarUsuarioSesion(clave, nuevo_valor, agregar_a_lista=False):
    user_data = session.get('user_data')

    # Si es una lista que queremos actualizar, agregar el nuevo valor
    if agregar_a_lista and isinstance(user_data.get(clave), list):
        user_data[clave].append(nuevo_valor)
    else:
        user_data[clave] = nuevo_valor

    session['user_data'] = user_data

def obtenerValorUsuarioSesion(clave):
    user_data = session.get('user_data')
    return user_data[clave]

def generarUsuarioSesion(nombre_completo: str, contrasena: str, codigo_recuperacion: str, correo: str, numero_documento: str, 
                donante: bool, admin: bool, enfermero: bool, puntos: int, total_donado: int, 
                tipo_de_sangre: TipoSangre, tipo_documento: TipoDocumento, perfil_imagen_link: str, 
                perfil_imagen_deletehash: str):
    
    registros = obtenerUsuarioRegistros( numero_documento , tipo_documento )

    return {
        'nombre': nombre_completo,
        'contrasena': contrasena,
        'codigo_recuperacion': codigo_recuperacion,
        'correo': correo,
        'numero_documento': numero_documento,
        'donante': donante,
        'admin': admin,
        'enfermero': enfermero,
        'puntos': puntos,
        'total_donado': total_donado,
        'tipo_de_sangre': tipo_de_sangre,
        'tipo_documento': tipo_documento,
        'perfil_imagen_link': perfil_imagen_link,
        'perfil_imagen_deletehash': perfil_imagen_deletehash,
        'registros': registros,
        'cnt_registros': len(registros)
        }

def generarUsuarioImagen(imagen, imgur_handler):
    if imagen and imagen.filename:
        try:
            image_data = imgur_handler.send_image(imagen)

            # Si no se pudo guardar, colocar la imagen por default
            if not image_data["success"]:
                return secret_config.DEFAULT_PROFILE_PICTURE, ""
            
            # Guardar la imagen exitosa
            perfil_imagen_link = image_data["data"]["link"]
            perfil_imagen_deletehash = image_data["data"]["deletehash"]

            return perfil_imagen_link, perfil_imagen_deletehash
        except:
            return None,None
         
    return secret_config.DEFAULT_PROFILE_PICTURE, ""