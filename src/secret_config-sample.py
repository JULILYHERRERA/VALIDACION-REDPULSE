"""

Datos secretos que no deben publicarse en el repo

Diligencie estos datos y guarde este archivo como SecretConfig.py
para poder ejecutar la aplicación

"""
# Parametros para conexion con la BD (Base de Datos)
PGDATABASE = "ESCRIBA EL NOMBRE DE LA BASE DE DATOS"
PGUSER = "ESCRIBA EL USUARIO DE LA DB"
PGPASSWORD = "ESCRIBA LA CONSTRASEÑA"
PGHOST = "ESCRIBA LA DIRECCION DNS O DIRECCION IP DEL SERVIDOR"
PGPORT = 5432 # POR DEFECTO ES 5432, PERO PUEDE CAMBIAR EN SU DB

# Token para bot de notificaciones.
NOTIEMAIL = "CORREO DEL BOT"
NOTICONTRA = "CONTRASEÑA CORREO BOT"

# Secret key para el apartado web (Flask)

SECRET_KEY_FLASK = "CONTRASEÑA ESPECIAL DEL FLASK"

# Key para ChatGpt Api

CHAT_BOT_KEY = "TOKEN PARA EL API DE GPT"

# Correo destinado del administrador
ADMINEMAIL = "CORREO DEL ADMINISTRADOR O EMPRESA"

# Imagen de perfil por defecto para cada usuario
DEFAULT_PROFILE_PICTURE = "IMAGEN POR DEFECTO PARA TODOS LOS USUARIOS"

# Keys para Imgur
IMGUR_CLIENT_ID = "CLIENT ID IMGUR"
IMGUR_CLIENT_SECRET = "CLIENT SECRET IMGUR"
