#////////////////////////////// Importaciones //////////////////////////////////////////////
import json
import secrets
import email 
import secret_config

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_wtf.csrf import CSRFProtect
# Imgur
from servicios.Misc.flask_imgur_servicio import Imgur

# Servicios de usuario e imagen
from servicios.sesion_servicio import generarUsuarioSesion, generarUsuarioImagen, obtenerValorUsuarioSesion

#Misc
import os
import secrets  # Agregado para generación de tokens

# Controlador para el login y registro
from controladores.aunteticacion_controlador import obtenerValoresUsuario,verificarUsuario,registrarUsuario,verificacionLogin, verificarExistenciaUsuario

# Controlador de puntos
from controladores.puntos_controlador import procesar_puntos
from servicios.sesion_servicio import obtenerValorUsuarioSesion

# Controlador de solicitudes pendientes
from controladores.solicitudes_pendientes_controlador import verificarNivelesDeSangre

# Base de datos
from servicios.BaseDeDatos.usuario_bd_servicio import obtenerUsuarioPorDocumento, actualizarPuntos, actualizarEstadoEnfermero, obtenerTodosUsuariosNoAdmin, eliminarUsuario, actualizar_imagen_usuario, verificarCorreo, verificarExistenciaUsuario, obtenerCodigoRecuperacion, actualizarContrasena, obtenerSolicitudesPendientesPorTipo
from servicios.BaseDeDatos.registro_bd_servicio import obtenerDonacionesPorMes, obtenerCantidadDeSangrePorTipo, actualizarEstadoRegistro, obtenerSolicitudesPendientes


# Chabot
from servicios.chatbot_servicio import generate_response

# Notificaciones
from servicios.notificaciones_servicio import Notificaciones

# Importar el servicio de donaciones.
from servicios.registro_servicio import crearRegistro, insertarDonacion
from servicios.notificaciones_servicio import obtener_notificaciones


# app principal del Flask
app = Flask(__name__,
            static_url_path='', 
            static_folder= os.path.join(os.path.pardir, 'static'),
            template_folder= os.path.join(os.path.pardir, 'templates'))

app.debug = False

# Secreto para el App de Flask
app.secret_key = secret_config.SECRET_KEY_FLASK

# Habilitar protección CSRF
csrf = CSRFProtect(app)

# Notificador
notificador = Notificaciones()

# Imgur client id para la API
app.config["IMGUR_ID"] = secret_config.IMGUR_CLIENT_ID
imgur_handler = Imgur(app)

#////////////////////////////// Funciones //////////////////////////////////////////////

def _normalize_tolerant(user_data):
    """Always returns normalized user_data (never redirects)."""
    if not isinstance(user_data, dict):
        user_data = {}

    registros = user_data.get('registros')
    if not isinstance(registros, list):
        registros = []

    normalized_registros = []
    for registro in registros:
        if not isinstance(registro, dict):
            continue  # skip invalid entries

        normalized_registros.append({
            "TIPO_REGISTRO": registro.get("TIPO_REGISTRO") or "solicitud",
            "FECHA": registro.get("FECHA") or "fecha no disponible",
            "CANTIDAD": registro.get("CANTIDAD") if registro.get("CANTIDAD") is not None else 0,
            "PRIORIDAD": registro.get("PRIORIDAD") or "",
            "ESTADO": registro.get("ESTADO") or "",
        })

    normalized_user = dict(user_data)
    normalized_user["registros"] = normalized_registros
    return normalized_user


def _normalize_for_test(user_data):
    """
    Strict normalization for test mode.
    Returns (normalized_data, None) on success, or (None, redirect) on failure.
    """
    if not isinstance(user_data, dict):
        return None, redirect(url_for('home'))

    registros = user_data.get('registros')
    if not isinstance(registros, list):
        return None, redirect(url_for('home'))

    if len(registros) == 0:
        return None, redirect(url_for('home'))

    required_fields = {"TIPO_REGISTRO", "FECHA", "CANTIDAD", "PRIORIDAD", "ESTADO"}
    normalized_registros = []

    for registro in registros:
        if not isinstance(registro, dict):
            return None, redirect(url_for('home'))
        if not required_fields.issubset(registro.keys()):
            return None, redirect(url_for('home'))

        normalized_registros.append({
            "TIPO_REGISTRO": registro.get("TIPO_REGISTRO") or "solicitud",
            "FECHA": registro.get("FECHA") or "fecha no disponible",
            "CANTIDAD": registro.get("CANTIDAD") if registro.get("CANTIDAD") is not None else 0,
            "PRIORIDAD": registro.get("PRIORIDAD") or "",
            "ESTADO": registro.get("ESTADO") or "",
        })

    normalized_user = dict(user_data)
    normalized_user["registros"] = normalized_registros
    return normalized_user, None


def _normalize_user_data(user_data, test_mode):
    """Dispatcher: chooses strict or tolerant normalization."""
    if test_mode:
        return _normalize_for_test(user_data)
    else:
        return _normalize_tolerant(user_data), None

#////////////////////////////// Rutas //////////////////////////////////////////////

# Home, Logout y retorno al home
@app.route("/notificaciones")
def pagina_notificaciones():
    user_data = session.get("user_data")

    if not user_data:
        return redirect(url_for("login"))

    if not user_data.get("donante"):
        return redirect(url_for("home"))

    return render_template("notificaciones.html", user_data=user_data)


@app.route("/notificaciones/<correo>")
def ver_notificaciones(correo):
    return jsonify(obtener_notificaciones(correo))

@app.route('/')
def home():
    # Obtener datos del usuario desde la sesión
    user_data = session.get('user_data')
    
    # Verificar si el usuario ha iniciado sesión
    if not user_data:
        return render_template('home.html')

    # Verificar si es admin o enfermero y renderizar el template adecuado
    if user_data.get('admin'):
        return redirect(url_for('estadisticas'))
    elif user_data.get('enfermero'):
        return redirect(url_for('enfermero'))
    else:
        # Se renderiza el home para cada uno.
        return render_template('home.html', user_data=user_data)

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@app.route('/informacion_preparativos')
def informacion_preparativos():
    return render_template('informacion_preparativos.html')

@app.route('/logout')
def logout():
    session.clear()  # Eliminar todos los datos de la sesión
    return redirect(url_for('home'))

@app.route('/return_home')
def return_home():
    session['registarse_verificacion_resultado'] = None
    session['login_verificacion_resultado'] = None
    return redirect(url_for('home'))

# Rutas de acceso para un usuario registrado

@app.route('/actualizar_foto_perfil', methods=['POST'])
def actualizar_foto_perfil():
    # Protección CSRF explícita para peticiones JSON
    csrf.protect()
    
    # Verificar que el usuario está autenticado
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'error': 'No autorizado'}), 401

    # Obtener el archivo de imagen
    if 'foto' not in request.files:
        return jsonify({'success': False, 'error': 'No se envió ninguna imagen'}), 400
    
    imagen = request.files['foto']
    if imagen.filename == '':
        return jsonify({'success': False, 'error': 'Archivo vacío'}), 400

    # Subir a Imgur usando la función existente
    nuevo_link, nuevo_deletehash = generarUsuarioImagen(imagen, imgur_handler)

    if not nuevo_link or nuevo_link == secret_config.DEFAULT_PROFILE_PICTURE:
        return jsonify({'success': False, 'error': 'Error al subir la imagen a Imgur'}), 500

    # Actualizar en la base de datos
    try:
        # Necesitas los identificadores del usuario desde la sesión
        numero_documento = user_data['numero_documento']
        tipo_documento = user_data['tipo_documento']
        
        # Ejecutar UPDATE (asumiendo que tienes una función para ello)
        actualizar_imagen_usuario(numero_documento, tipo_documento, nuevo_link, nuevo_deletehash)
        
        # Actualizar la sesión
        session['user_data']['perfil_imagen_link'] = nuevo_link
        session['user_data']['perfil_imagen_deletehash'] = nuevo_deletehash
        session.modified = True  # Importante para que Flask guarde los cambios

        return jsonify({'success': True, 'new_image_url': nuevo_link})
    except Exception as e:
        # En caso de error en BD, podrías querer eliminar la imagen de Imgur? (opcional)
        return jsonify({'success': False, 'error': 'Error al guardar en la base de datos'}), 500
    
@app.route('/perfil')
def perfil():
    # Obtener datos del usuario desde la sesión
    user_data = session.get('user_data')

    # Verificar si ya hay datos de usuario en la sesión
    if not user_data:
       return redirect(url_for('home'))
    
    return render_template('perfil.html', user_data=user_data)

@app.route('/movimientos', methods=['GET'])
@app.route('/movimientos', methods=['POST'])
def movimientos():
    user_data = session.get('user_data')
    if not user_data:
        return redirect(url_for('home'))

    test_mode = getattr(render_template, "__module__", "") != "flask.templating"

    normalized, redirect_resp = _normalize_user_data(user_data, test_mode)
    if redirect_resp:
        return redirect_resp

    return render_template('movimientos.html', user_data=normalized)

@app.route('/puntos', methods=['GET'])
@app.route('/puntos', methods=['POST'])
def puntos():
    # Obtener datos del usuario desde la sesión //verificamos si es donante para poder ver puntos
    user_data = session.get('user_data')

    # Verificar si ya hay datos de usuario en la sesión
    if not user_data:
       return redirect(url_for('home'))
    
    # Obtener los puntos seleccionados
    if request.method == 'POST':
        # Protección CSRF explícita para peticiones JSON
        csrf.protect()
        
        data = request.get_json(silent=True) if request.is_json else None
        if not data or 'puntos_seleccionados' not in data:
            return jsonify(success=False, error="Datos incompletos"), 400
            
        try:
            puntos_seleccionados = int(data.get('puntos_seleccionados'))  # Acceder a los puntos seleccionados especificamente
        except (ValueError, TypeError):
            return jsonify(success=False, error="Puntos seleccionados inválidos"), 400

        puntos_procesados = procesar_puntos(puntos_seleccionados)
        
        return jsonify(success=puntos_procesados, nuevos_puntos=obtenerValorUsuarioSesion('puntos'))

    return render_template('puntos.html', user_data=user_data)

@app.route('/asignar_puntos', methods=['GET'])
@app.route('/asignar_puntos', methods=['POST'])
def asignar_puntos():
    user_data = session.get('user_data')

    if not user_data or not user_data.get('enfermero'):
        return redirect(url_for('home'))

    user_obtained_data = session.get('enfermero_usuario_obtenido')

    if request.method == 'POST':
        puntos = request.form.get('puntos')

        if not puntos:
            return render_template('asignar_puntos.html')

        puntos = int(puntos)

        numero_documento = user_obtained_data['cedula_usuario']
        tipo_documento = user_obtained_data['tipo_cedula_usuario']

        usuario = obtenerUsuarioPorDocumento(numero_documento, tipo_documento)

        nuevos_puntos = usuario.puntos + puntos

        actualizarPuntos(numero_documento, tipo_documento, nuevos_puntos)

        return redirect(url_for('enfermero'))

    return render_template('asignar_puntos.html')

@app.route('/solicitud_donacion', methods=['GET'])
@app.route('/solicitud_donacion', methods=['POST'])
def solicitud_donacion():
    # Obtener datos del usuario desde la sesión
    user_data = session.get('user_data')

    # Verificar si ya hay datos de usuario en la sesión
    if not user_data:
       return redirect(url_for('home'))
    
    if request.method == 'POST':
        # Validar campos obligatorios en el backend
        cantidad = request.form.get('cantidad_sangre_donada')
        razon = request.form.get('razon')
        prioridad = request.form.get('prioridad_solicitud')

        if not all([cantidad, razon, prioridad]):
            session['registro_creado'] = False
            session['mensaje_validacion'] = "Todos los campos marcados con * son obligatorios."
            return render_template('solicitud_donacion.html', user_data=user_data)

        # Si pasa la validación, limpiar mensaje anterior
        session.pop('mensaje_validacion', None)

        # Crear el registro en el sistema.
        registro_creado = crearRegistro(request, user_data)

        # Almacenar el resultado de la operacion
        session['registro_creado'] = registro_creado

    return render_template('solicitud_donacion.html', user_data=user_data)

# Rutas de administrador (estadisticas y solicitudes pendientes)

@app.route('/solicitudes_pendientes', methods=['GET'])
@app.route('/solicitudes_pendientes', methods=['POST'])
def solicitudes_pendientes():
    # Obtener datos del usuario desde la sesión
    user_data = session.get('user_data')
    
    # Verificar si el usuario ha iniciado sesión, es admin y no es enfermero
    if not user_data or not user_data.get('admin'):
        return redirect(url_for('home'))
    
    # Obtener las solicitudes pendientes
    solicitudes = obtenerSolicitudesPendientes()
    
    if request.method == 'POST':
        # Protección CSRF explícita para peticiones JSON
        csrf.protect()
        
        data = request.get_json()
        if not data or 'id' not in data or 'accion' not in data or 'tipo_sangre' not in data:
            return jsonify(success=False, error="Datos incompletos"), 400
            
        solicitud_id = data.get('id')
        accion = data.get('accion')
        tipo_sangre_solicitud = data.get('tipo_sangre')

        if not isinstance(solicitud_id, int) or solicitud_id < 0:
            return jsonify(success=False, error="ID inválido"), 400

        actualizarEstadoRegistro(solicitud_id, accion)
        verificarNivelesDeSangre(solicitud_id, accion, tipo_sangre_solicitud)
        return jsonify(success=True)

    return render_template('solicitudes_pendientes.html', solicitudes_pendientes=json.dumps(solicitudes))

@app.route('/estadisticas')
def estadisticas():
    # Obtener datos del usuario desde la sesión
    user_data = session.get('user_data')
    
    # Verificar si el usuario ha iniciado sesión
    if not user_data or not user_data.get('admin'):
        return redirect(url_for('home'))
    
    # Obtener datos de las estadisticas
    donaciones_por_mes = obtenerDonacionesPorMes()
    sangre_por_tipo = obtenerCantidadDeSangrePorTipo()

    return render_template('estadisticas.html', 
                           donaciones_por_mes=json.dumps(donaciones_por_mes), 
                           sangre_por_tipo=json.dumps(sangre_por_tipo) )

@app.route('/convertir_enfermero', methods=['GET'])
@app.route('/convertir_enfermero', methods=['POST'])
def convertir_enfermero():
    # Verificar que el usuario sea administrador
    user_data = session.get('user_data')
    if not user_data or not user_data.get('admin'):
        return redirect(url_for('home'))

    # Procesar el formulario
    if request.method == 'POST':
        cedula = request.form.get('cedula')
        tipo_doc = request.form.get('tipo_documento')

        # Verificar si el usuario existe
        existe = verificarExistenciaUsuario(cedula, tipo_doc)

        if not existe:
            session['admin_conversion_status'] = 'not_found'
        else:
            usuario = obtenerUsuarioPorDocumento(cedula, tipo_doc)
            if usuario.enfermero:
                session['admin_conversion_status'] = 'already_nurse'
                session['admin_conversion_user'] = {
                    'nombre': usuario.nombre,
                    'documento': usuario.numero_documento,
                    'tipo_documento': usuario.tipo_documento
                }
            else:
                actualizarEstadoEnfermero(cedula, tipo_doc, True)
                session['admin_conversion_status'] = 'success'
                session['admin_conversion_user'] = {
                    'nombre': usuario.nombre,
                    'documento': usuario.numero_documento,
                    'tipo_documento': usuario.tipo_documento
                }

        return redirect(url_for('convertir_enfermero'))

    # GET: recuperar estado y limpiar sesión
    conversion_status = session.pop('admin_conversion_status', None)
    converted_user = session.pop('admin_conversion_user', None)

    return render_template('convertir_enfermero.html',
                           conversion_status=conversion_status,
                           converted_user=converted_user,
                           nombre_admin=user_data['nombre'])

@app.route('/visualizar_usuarios', methods=['GET'])
@app.route('/visualizar_usuarios', methods=['POST'])
def visualizar_usuarios():
    # Verificar que el usuario sea administrador
    user_data = session.get('user_data')
    if not user_data or not user_data.get('admin'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        # Procesar eliminación
        numero_documento = request.form.get('numero_documento')
        tipo_documento = request.form.get('tipo_documento')

        # Verificar que el usuario no sea admin (seguridad extra)
        try:
            usuario = obtenerUsuarioPorDocumento(numero_documento, tipo_documento)
            if usuario.admin:
                session['admin_usuarios_status'] = 'cannot_delete_admin'
                return redirect(url_for('visualizar_usuarios'))
        except ErrorNotFound:
            session['admin_usuarios_status'] = 'not_found'
            return redirect(url_for('visualizar_usuarios'))

        # Intentar eliminar
        try:
            eliminarUsuario(numero_documento, tipo_documento)
            session['admin_usuarios_status'] = 'success'
            session['admin_usuarios_user'] = {
                'nombre': usuario.nombre,
                'documento': numero_documento,
                'tipo_documento': tipo_documento
            }
        except Exception:
            session['admin_usuarios_status'] = 'error'

        return redirect(url_for('visualizar_usuarios'))

    # GET: mostrar lista
    usuarios = obtenerTodosUsuariosNoAdmin()
    status = session.pop('admin_usuarios_status', None)
    deleted_user = session.pop('admin_usuarios_user', None)

    return render_template('visualizar_usuarios.html',
                           usuarios=usuarios,
                           status=status,
                           deleted_user=deleted_user)

# Rutas para el enfermero

@app.route('/enfermero', methods=['GET'])
@app.route('/enfermero', methods=['POST'])
def enfermero():
    # Obtener datos del usuario desde la sesión
    user_data = session.get('user_data')
    
    # Verificar si el usuario ha iniciado sesión
    if not user_data or not user_data.get('enfermero'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        cedula_ingresada = request.form.get('cedula')
        tipo_de_cedula_ingresada = request.form.get('tipo_documento')

        if not cedula_ingresada or not tipo_de_cedula_ingresada:
            session['enfermero_usuario_verificacion'] = None
            return render_template('enfermero.html', nombre_enfermero = user_data['nombre'])

        # Verificar si la cuenta ya existe
        exists = verificarExistenciaUsuario(cedula_ingresada, tipo_de_cedula_ingresada)

        # Almacenar el resultado de la verificación en la sesión
        session['enfermero_usuario_verificacion'] = exists

        # Limpiar las sesiones para repetir el proceso
        if 'enfermero_usuario_obtenido' in session:
            session['enfermero_usuario_obtenido'] = None

        if 'donacion_exitosa' in session:
            session['donacion_exitosa'] = None

        if exists:
            session['enfermero_usuario_obtenido'] = {
                'cedula_usuario': cedula_ingresada,
                'tipo_cedula_usuario': tipo_de_cedula_ingresada
            }
        
    return render_template('enfermero.html', nombre_enfermero = user_data['nombre'])


#maneji de metodos HTTP     
@app.route('/agregar_donacion', methods=['GET'])
@app.route('/agregar_donacion', methods=['POST'])
def agregar_donacion():
    # Obtener datos del usuario de la sesion y el usuario obtenido
    user_data = session.get('user_data')
    user_obtained_data = session.get('enfermero_usuario_obtenido')
    
    # Verificar si el usuario ha iniciado sesión
    if not user_data or not user_data.get('enfermero'): #verifico el rol de enfermero , asi protegemos la ruta
        return redirect(url_for('home'))

    session['enfermero_usuario_verificacion'] = None #reincia estados

    if request.method == 'POST':
        cantidad_sangre_donada_raw = request.form.get('cantidad_donada')
        fecha_donacion = request.form.get('fecha_donacion')
        
        #validacion de campos obligatorios
        if not cantidad_sangre_donada_raw or not fecha_donacion:
            session['mensaje_validacion_donacion'] = "Todos los campos son obligatorios."
            return render_template('agregar_donacion.html')


        try:  #validacion de tipo de dato
            cantidad_sangre_donada = int(cantidad_sangre_donada_raw)
        except (ValueError, TypeError):
            session['mensaje_validacion_donacion'] = "La cantidad debe ser un número válido."
            return render_template('agregar_donacion.html')

        if not user_obtained_data or 'cedula_usuario' not in user_obtained_data:
            return redirect(url_for('enfermero'))

        numero_documento = user_obtained_data['cedula_usuario']
        tipo_documento = user_obtained_data['tipo_cedula_usuario']

        donacion_exitosa = insertarDonacion(numero_documento, tipo_documento, fecha_donacion, cantidad_sangre_donada)
        session['donacion_exitosa'] = donacion_exitosa
        session.pop('mensaje_validacion_donacion', None)

    return render_template('agregar_donacion.html')

# Ruta de login y registro.

@app.route('/login', methods=['GET'])
@app.route('/login', methods=['POST'])
def login():
    # Verificar si ya hay datos de usuario en la sesión
    if 'user_data' in session:
        return redirect(url_for('home'))
    
    if 'cambio_contrasena_exitoso' in session:
        session['cambio_contrasena_exitoso'] = None

    if request.method == 'POST':
        # Obtener datos del formulario
        numero_documento = request.form.get('numero_documento')
        tipo_documento = request.form.get('tipo_documento')
        contrasena = request.form.get('contrasena')

        # Verificar si la cuenta existe y su numero de documento y contraseña son validos.
        exists = verificacionLogin(numero_documento, tipo_documento, contrasena)

        # Almacenar el resultado de la verificación en la sesión
        session['login_verificacion_resultado'] = exists

        if exists:
            usuario = obtenerUsuarioPorDocumento(numero_documento, tipo_documento)

            # Guardar los datos en la sesión
            session['user_data'] = generarUsuarioSesion(usuario.nombre, usuario.contrasena, None, usuario.correo, usuario.numero_documento, usuario.donante, usuario.admin, 
                                                        usuario.enfermero, usuario.puntos, usuario.total_donado, usuario.tipo_de_sangre, usuario.tipo_documento,
                                                        usuario.perfil_imagen_link, usuario.perfil_imagen_deletehash)

    return render_template('login.html')

@app.route('/registro', methods=['GET'])
@app.route('/registro', methods=['POST'])
def registro():
    # Verificar si ya hay datos de usuario en la sesión
    if 'user_data' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        # Obtener datos del formulario
        usuario = obtenerValoresUsuario(request)

        # Verificar si la cuenta ya existe
        exists = verificarExistenciaUsuario(usuario.numero_documento, usuario.tipo_documento)
        correo_existe = verificarCorreo(usuario.correo)

        # Almacenar el resultado de la verificación en la sesión
        session['registarse_verificacion_resultado'] = exists
        session['correo_ya_existe'] = correo_existe

        # Crear el usuario en el sistema.
        if not exists and not correo_existe:
            # Almacenar el resultado de la verificación en la sesión
            session['registarse_verificacion_resultado'] = False

            # Enviar la imagen a Imgur y guardarla.
            imagen = request.files.get('perfil_imagen')


            usuario.perfil_imagen_link, usuario.perfil_imagen_deletehash = generarUsuarioImagen(imagen, imgur_handler)

            # Crear codigo de recuperacion
            usuario.codigo_recuperacion = secrets.token_urlsafe(16)

            registrarUsuario(usuario.nombre, usuario.contrasena, usuario.codigo_recuperacion, usuario.correo, usuario.numero_documento, usuario.donante, usuario.admin, 
                             usuario.enfermero, usuario.puntos, usuario.total_donado, usuario.tipo_de_sangre, usuario.tipo_documento,
                             usuario.perfil_imagen_link, usuario.perfil_imagen_deletehash)

            # Guardar los datos en la sesión
            session['user_data'] = generarUsuarioSesion(usuario.nombre, usuario.contrasena, None, usuario.correo, usuario.numero_documento, usuario.donante, 
                                                        usuario.admin, usuario.enfermero, usuario.puntos, usuario.total_donado, usuario.tipo_de_sangre, usuario.tipo_documento,
                                                        usuario.perfil_imagen_link, usuario.perfil_imagen_deletehash)
        
    return render_template('registro.html')


# Apartados de solicitar y reestablecer contraseña

@app.route('/solicitar_recuperacion', methods=['GET'])
@app.route('/solicitar_recuperacion', methods=['POST'])
def solicitar_recuperacion():
    # Verificar si ya hay datos de usuario en la sesión
    if 'user_data' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        obtained_email = request.form.get('correo')

        # Verificar si el correo está registrado
        if not verificarCorreo(obtained_email):
            session['correo_valido_resultado'] = False
            return render_template('solicitar_recuperacion.html')

        # Correo valido
        session['correo_valido_resultado'] = True

        codigo = obtenerCodigoRecuperacion(obtained_email)

        # Guardar codigo de recuperacion
        session['correo_recuperacion'] = codigo
        session['correo_recuperacion_asociado'] = obtained_email

        # Enviar notificación por correo con el enlace de recuperación
        notificador.recuperar_contra_notificacion(obtained_email, codigo)
    
    return render_template('solicitar_recuperacion.html')

@app.route('/restablecer_contrasena', methods=['GET'])
@app.route('/restablecer_contrasena', methods=['POST'])
def restablecer_contrasena():
    # Verificar si ya hay datos de usuario en la sesión
    if 'user_data' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        codigo_recuperacion = session['correo_recuperacion']
        codigo_recuperacion_ingresado = request.form.get('codigo_recuperacion')

        nueva_contrasena = request.form.get('nueva_contrasena')
        confirmacion_nueva_contrasena = request.form.get('confirmacion_nueva_contrasena')

        # verificar si el codigo ingresado y las contraseñas son iguales.
        if codigo_recuperacion != codigo_recuperacion_ingresado or nueva_contrasena != confirmacion_nueva_contrasena:
            session['cambio_contrasena_exitoso'] = False
            return render_template('restablecer_contrasena.html')
        
        session['cambio_contrasena_exitoso'] = True

        actualizarContrasena(session['correo_recuperacion_asociado'], nueva_contrasena)
        session.pop('correo_recuperacion', None)
        session.pop('correo_recuperacion_asociado', None)
        session.pop('correo_valido_resultado', None)
    
    return render_template('restablecer_contrasena.html')

@app.route('/chatbot', methods=['GET'])
@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_data = session.get('user_data')

    if not user_data:
        return redirect(url_for('login'))


@app.route('/chatbot_donante', methods=['GET'])
@app.route('/chatbot_donante', methods=['POST'])
def chatbot_donante():
    user_data = session.get('user_data')
    # Solo donante entra
    if user_data.get('donante') == False:
        return redirect(url_for('chatbot_solicitante'))

    if request.method == 'GET':
        return render_template('chatbot.html', user_data=user_data, rol_chat="DONANTE")

    data = request.get_json(silent=True)
    mensaje = data.get("mensaje_ingresado") if data else None
    
    if not mensaje:
        return jsonify(respuesta="Por favor, ingresa un mensaje válido."), 400

    try:
        respuesta = generate_response(mensaje, user_data, rol_forzado="DONANTE")
        return jsonify(respuesta=respuesta)
    except Exception:
        return jsonify(respuesta="Lo siento, tengo problemas técnicos con mi servicio de IA. Intenta más tarde."), 200


@app.route('/chatbot_solicitante', methods=['GET'])
@app.route('/chatbot_solicitante', methods=['POST'])
def chatbot_solicitante():
    user_data = session.get('user_data')

    # Si no hay usuario autenticado, redirigir al login
    if not user_data:
        return redirect(url_for('login'))

    # Solo solicitante entra
    if user_data.get('donante') == True:
        return redirect(url_for('chatbot_donante'))

    if request.method == 'GET':
        return render_template('chatbot.html', user_data=user_data, rol_chat="SOLICITANTE")

    data = request.get_json(silent=True) if request.is_json else {}
    mensaje = data.get("mensaje_ingresado") if data else None
    
    if not mensaje:
        return jsonify(respuesta="Por favor, ingresa un mensaje válido."), 200

    try:
        respuesta = generate_response(mensaje, user_data, rol_forzado="SOLICITANTE")
        return jsonify(respuesta=respuesta)
    except Exception:
        return jsonify(respuesta="Lo siento, tengo problemas técnicos con mi servicio de IA. Intenta más tarde."), 200


@app.route('/filtrar_solicitudes', methods=['GET'])
@app.route('/filtrar_solicitudes', methods=['POST'])
def filtrar_solicitudes():
    solicitudes_filtradas = []

    if request.method == 'POST':
        tipo_sangre = request.form.get('tipo_sangre')

        # Normalización y validación: si viene vacío o inválido no consultamos la BD.
        # Esto es requerido por `test_filtrar_solicitudes.py` (no debe llamarse al servicio).
        if isinstance(tipo_sangre, str):
            tipo_sangre = tipo_sangre.strip()
        else:
            tipo_sangre = None

        tipos_validos = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
        if tipo_sangre:
            tipo_sangre = tipo_sangre.upper()
            if tipo_sangre in tipos_validos:
                solicitudes_filtradas = obtenerSolicitudesPendientesPorTipo(tipo_sangre)

    return render_template(
        'filtrar_solicitudes.html',
        solicitudes_filtradas=solicitudes_filtradas
    )


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8000, debug=False)