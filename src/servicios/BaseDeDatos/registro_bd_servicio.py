# Controla las operaciones de almacenamiento de la clase registro

import sys
sys.path.append("src")

from datetime import datetime

# Importando librerias para la DB
import psycopg2
import secret_config

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
    Crea la tabla de registros, en caso de que no exista
    """    
    sql = ""
    with open("sql/crear_registro.sql","r") as f:
        sql = f.read()

    cursor = obtenerCursor()
    try:
        cursor.execute( sql )
        cursor.connection.commit()
    except:
        # SI LLEGA AQUI, ES PORQUE LA TABLA YA EXISTE
        cursor.connection.rollback()

def insertarEnTabla( registro ):
    """ Guarda un registro en la base de datos """

    cursor = obtenerCursor()

    try:
        # Todas las instrucciones se ejecutan a tavés de un cursor
        cursor.execute("""
        INSERT INTO registros (
            tipo_registro, tipo_sangre, cantidad, razon, comentarios, prioridad, estado, fecha, usuario_documento, usuario_tipo_documento
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            registro.tipo_registro, registro.tipo_sangre, registro.cantidad,
            registro.razon, registro.comentarios, registro.prioridad, registro.estado,
            registro.fecha, registro.usuario_documento, registro.usuario_tipo_documento
        ))

        # Las instrucciones DDL y DML no retornan resultados, por eso no necesitan fetchall()
        # pero si necesitan commit() para hacer los cambios persistentes

        cursor.connection.commit()
    except Exception as e:
        print(e)
        cursor.connection.rollback() 
        raise Exception("No fue posible insertar el registro." )
    
def actualizarEstadoRegistro( registro_id, estado ):
    """ Agrega una cantidad de puntos al usuario especificado """
    
    cursor = obtenerCursor()
    try:
        sql = f"UPDATE registros SET estado = '{estado}' WHERE id = '{registro_id}'"
        cursor.execute(sql)
        cursor.connection.commit()
    except Exception as e:
        cursor.connection.rollback()
        raise Exception("No fue posible actualizar el estado del registro: ") from e
    
def obtenerUsuarioRegistros( numero_documento , tipo_documento ):
    """ Obtiene todas los registros que sean solicitud y tengan estado pendiente """
    cursor = obtenerCursor()
    
    cursor.execute(f"""
    SELECT TIPO_REGISTRO, CANTIDAD, PRIORIDAD, ESTADO, FECHA, 
           USUARIO_DOCUMENTO, USUARIO_TIPO_DOCUMENTO
    FROM REGISTROS
    WHERE USUARIO_DOCUMENTO = '{numero_documento}'
      AND USUARIO_TIPO_DOCUMENTO = '{tipo_documento}'
    """)
    rows = cursor.fetchall()
    
    registros = [
        {
            "TIPO_REGISTRO": row[0],
            "CANTIDAD": row[1],
            "PRIORIDAD": row[2],
            "ESTADO": row[3],
            "FECHA": row[4].strftime("%d-%m-%Y"),
        }
        for row in rows
    ]
    
    return registros

def obtenerSolicitudesPendientes():
    """ Obtiene todas los registros que sean solicitud y tengan estado pendiente """
    cursor = obtenerCursor()
    
    cursor.execute("""
    SELECT u.nombre AS nombre_donante, 
           r.tipo_sangre, 
           r.cantidad, 
           r.fecha, 
           r.razon, 
           r.prioridad,
           r.id
    FROM REGISTROS r
    JOIN USUARIOS u 
    ON r.usuario_documento = u.numero_documento 
       AND r.usuario_tipo_documento = u.tipo_documento
    WHERE r.estado = 'Pendiente';
    """)
    registros = cursor.fetchall()

    solicitudes = []
    for registro in registros:
        solicitud = {
            "nombreDonante": registro[0],
            "tipoSangre": registro[1],
            "cantidad": registro[2],
            "fecha": registro[3].strftime("%d-%m-%Y"),
            "razon": registro[4],
            "prioridad": registro[5],
            "id": registro[6],
        }
        solicitudes.append(solicitud)

    return solicitudes

def obtenerDonacionesPorMes():
    """ Obtiene todas las donaciones realizadas en el mes """
    cursor = obtenerCursor()
    
    cursor.execute("""
    SELECT TO_CHAR(FECHA, 'Month') AS mes,
           COUNT(*) AS cantidad
    FROM REGISTROS
    WHERE TIPO_REGISTRO = 'Donacion'
    GROUP BY TO_CHAR(FECHA, 'Month'), DATE_PART('month', FECHA)
    ORDER BY DATE_PART('month', FECHA);
    """)
    row = cursor.fetchall()
    
    donaciones_por_mes = {mes.strip(): cantidad for mes, cantidad in row}
    donaciones_por_mes = traducirMesesAlEspañol(donaciones_por_mes)

    return donaciones_por_mes

def obtenerCantidadDeSangrePorTipo():
    """ Obtiene todas las donaciones realizadas en el mes """
    cursor = obtenerCursor()
    
    cursor.execute("""
    SELECT TIPO_SANGRE,
           SUM(CANTIDAD) AS cantidad_total
    FROM REGISTROS
    WHERE TIPO_REGISTRO = 'Donacion'
    GROUP BY TIPO_SANGRE;
    """)
    row = cursor.fetchall()
    
    sangre_por_tipo = {tipo_sangre: cantidad_total for tipo_sangre, cantidad_total in row}
    
    return sangre_por_tipo

# funcion para traducir los meses obtenidos del postgres

def traducirMesesAlEspañol(diccionario_meses):
    meses_en_espanol = {
        "January": "Enero",
        "February": "Febrero",
        "March": "Marzo",
        "April": "Abril",
        "May": "Mayo",
        "June": "Junio",
        "July": "Julio",
        "August": "Agosto",
        "September": "Septiembre",
        "October": "Octubre",
        "November": "Noviembre",
        "December": "Diciembre"
    }
    
    # Crear un nuevo diccionario con las claves traducidas
    diccionario_traducido = {meses_en_espanol[mes]: valor for mes, valor in diccionario_meses.items()}
    return diccionario_traducido

def obtenerUsuarioPorRegistro(registro_id):
    cursor = obtenerCursor()
    cursor.execute("SELECT usuario_documento, usuario_tipo_documento FROM registros WHERE id = %s", (registro_id,))
    resultado = cursor.fetchone()
    return resultado

def obtenerCantidadSangreDonada(tipo_sangre):
    """Obtiene la cantidad total de sangre donada para un tipo de sangre específico"""
    
    cursor = obtenerCursor()
    try:
        # Consulta SQL para sumar las cantidades de donaciones del tipo de sangre especificado
        sql = """
            SELECT COALESCE(SUM(cantidad), 0) 
            FROM registros 
            WHERE tipo_registro = 'Donacion' AND tipo_sangre = %s
        """
        cursor.execute(sql, (tipo_sangre,))
        
        # Obtener el resultado de la suma
        cantidad_total = cursor.fetchone()[0]
        
        return cantidad_total
    except Exception as e:
        raise Exception(f"No fue posible obtener la cantidad total de sangre donada para el tipo de sangre {tipo_sangre}") from e

