# Controla las operaciones de almacenamiento de la clase usuario
import sys
sys.path.append("src")

# Importando el modelo
from modelos.usuario import Usuario

# Importando librerias para la DB
import psycopg2
import secret_config

# Encriptacion.
from werkzeug.security import generate_password_hash
import secrets

class ErrorNotFound( Exception ):
    """ Excepcion que indica que una row buscada no fue encontrada"""
    pass

def obtenerCursor() :
    """
    Crea la conexion a la base de datos y retorna un cursor para ejecutar instrucciones
    """
    DATABASE = secret_config.PGDATABASE
    USER = secret_config.PGUSER
    PASSWORD = secret_config.PGPASSWORD
    HOST = secret_config.PGHOST
    PORT = secret_config.PGPORT

    connection = psycopg2.connect( database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT )
    return connection.cursor()

def crearTabla():
    """
    Crea la tabla de usuarios, en caso de que no exista
    """    
    sql = ""
    with open("sql/crear_usuario.sql","r") as f:
        sql = f.read()

    cursor = obtenerCursor()
    try:
        cursor.execute( sql )
        cursor.connection.commit()
    except:
        # SI LLEGA AQUI, ES PORQUE LA TABLA YA EXISTE
        cursor.connection.rollback()

def insertarEnTabla( usuario ):
    """ Guarda un usuario en la base de datos """

    cursor = obtenerCursor()

    try:
        # Todas las instrucciones se ejecutan a tavés de un cursor
        cursor.execute(f"""
        insert into usuarios (
            nombre, contrasena, codigo_recuperacion, correo, numero_documento, donante, admin, enfermero, puntos, total_donado, tipo_de_sangre, tipo_documento, perfil_imagen_link, perfil_imagen_deletehash
        )
        values 
        (
            '{usuario.nombre}',  '{usuario.contrasena}', '{usuario.codigo_recuperacion}', '{usuario.correo}', '{usuario.numero_documento}', '{usuario.donante}', '{usuario.admin}', 
            '{usuario.enfermero}', '{usuario.puntos}', '{usuario.total_donado}', '{usuario.tipo_de_sangre}', '{usuario.tipo_documento}', '{usuario.perfil_imagen_link}', 
            '{usuario.perfil_imagen_deletehash}'
        );
                       """)

        # Las instrucciones DDL y DML no retornan resultados, por eso no necesitan fetchall()
        # pero si necesitan commit() para hacer los cambios persistentes

        cursor.connection.commit()
    except Exception as e:
        print(e)
        cursor.connection.rollback() 
        raise Exception("No fue posible insertar el usuario con el numero de documento y tipo de documento: ", usuario.numero_documento, usuario.tipo_documento)
    

def obtenerUsuarioPorDocumento( numero_documento, tipo_documento ):    
    """ Busca un usuario por el numero de documento y lo retornamos como objeto """

    cursor = obtenerCursor()
    cursor.execute(f"SELECT * from usuarios where numero_documento = '{numero_documento}' AND tipo_documento = '{tipo_documento}' ")
    row = cursor.fetchone()

    if row is None:
        raise ErrorNotFound("El usuario buscado, no fue encontrado. Numero documento y tipo de documento: ", numero_documento, tipo_documento)

    result = Usuario( row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13] )
    return result

def verificarExistenciaUsuario( numero_documento, tipo_documento ):
    """ Busca un usuario por el numero de documento y validamos si existe """

    cursor = obtenerCursor()
    cursor.execute(f"SELECT * from usuarios where numero_documento = '{numero_documento}' AND tipo_documento = '{tipo_documento}' ")
    row = cursor.fetchone()

    if row is None:
        return False
    return True

def verificarCorreo( correo ):
    """ Busca un usuario por el numero de documento y validamos si existe """

    cursor = obtenerCursor()
    cursor.execute(f"SELECT * from usuarios where CORREO = '{correo}' ")
    row = cursor.fetchone()

    if row is None:
        return False
    return True

def obtenerCodigoRecuperacion( correo ):
    """ Busca un usuario por el numero de documento y validamos si existe """

    cursor = obtenerCursor()
    cursor.execute(f"SELECT codigo_recuperacion from usuarios where CORREO = '{correo}' ")
    row = cursor.fetchone()

    return row[0]

def actualizarEstadoDonante( numero_documento, tipo_documento ):
    cursor = obtenerCursor()
    try:
        sql = f"UPDATE usuarios SET donante = TRUE WHERE numero_documento = '{numero_documento}' AND tipo_documento = '{tipo_documento}'"
        cursor.execute(sql)
        cursor.connection.commit()
    except Exception as e:
        cursor.connection.rollback()
        raise Exception("No fue posible actualizar el estado de donante para el usuario con el numero de documento: " + str(numero_documento)) from e

def actualizarPuntos( numero_documento, tipo_documento, cantidad_puntos ):
    """ Agrega una cantidad de puntos al usuario especificado """
    
    cursor = obtenerCursor()
    try:
        sql = f"UPDATE usuarios SET puntos = {cantidad_puntos} WHERE numero_documento = '{numero_documento}' AND tipo_documento = '{tipo_documento}'"
        cursor.execute(sql)
        cursor.connection.commit()
    except Exception as e:
        cursor.connection.rollback()
        raise Exception("No fue posible agregar puntos al usuario con el numero de documento: " + str(numero_documento)) from e
    
def actualizarCantidadDonada( numero_documento, tipo_documento, cantidad_donada ):
    """ Agrega una cantidad de puntos al usuario especificado """
    
    cursor = obtenerCursor()
    try:
        sql = f"UPDATE usuarios SET total_donado = {cantidad_donada} WHERE numero_documento = '{numero_documento}' AND tipo_documento = '{tipo_documento}'"
        cursor.execute(sql)
        cursor.connection.commit()
    except Exception as e:
        cursor.connection.rollback()
        raise Exception("No fue posible agregar puntos al usuario con el numero de documento: " + str(numero_documento)) from e

def actualizarContrasena(email, nueva_contrasena):
    """ Actualiza la contraseña del usuario en la base de datos usando su correo electrónico """
    
    cursor = obtenerCursor()
    try:
        contrasena_encriptada = generate_password_hash(nueva_contrasena, method='pbkdf2:sha256', salt_length=10)
        # Nuevo codigo de recuperacion
        codigo_recuperacion = secrets.token_urlsafe(16)

        sql = "UPDATE usuarios SET contrasena = %s, codigo_recuperacion = %s WHERE correo = %s"
        cursor.execute(sql, (contrasena_encriptada, codigo_recuperacion, email))

        cursor.connection.commit()
    except Exception as e:
        cursor.connection.rollback()
        raise Exception(f"No fue posible actualizar la contraseña para el usuario con el correo: {email}") from e

def obtenerCorreoUsuario(usuario_documento, usuario_tipo_documento):
    cursor = obtenerCursor()
    cursor.execute(
        "SELECT correo FROM usuarios WHERE tipo_documento = %s AND numero_documento = %s",
        (usuario_tipo_documento, usuario_documento)
    )
    res = cursor.fetchone()
    
    return res[0] if res else None

def obtenerCorreosDonantesTipoSangreEspecifico(tipo_sangre):
    """Obtiene todos los correos de los usuarios con un tipo de sangre específico"""
    
    cursor = obtenerCursor()
    try:
        # Consulta SQL para seleccionar los correos de usuarios con el tipo de sangre especificado y que sean donantes
        sql = """
            SELECT correo 
            FROM usuarios 
            WHERE tipo_de_sangre = %s AND donante = TRUE
        """
        cursor.execute(sql, (tipo_sangre,))
        
        # Obtener todos los correos
        correos = cursor.fetchall()
        
        # Extraer solo los correos de la tupla
        correos_lista = [row[0] for row in correos]
        
        return correos_lista
    except Exception as e:
        raise Exception(f"No fue posible obtener los correos para el tipo de sangre {tipo_sangre}") from e
