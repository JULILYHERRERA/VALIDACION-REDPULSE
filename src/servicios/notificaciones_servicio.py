from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from secret_config import NOTIEMAIL, NOTI_APPCONTRA, ADMINEMAIL


#  almacenamiento en memoria
notificaciones_data = {}


#  FUNCIÓN PARA GUARDAR NOTIFICACIONES
def agregar_notificacion(correo, mensaje):
    if correo not in notificaciones_data:
        notificaciones_data[correo] = []
    
    notificaciones_data[correo].append(mensaje)


#  FUNCIÓN PARA CONSULTAR NOTIFICACIONES
def obtener_notificaciones(correo):
    return notificaciones_data.get(correo, [])


class Notificaciones:
    def __init__(self, de_email=None, contra=None, admin_email=ADMINEMAIL):
        self.admin_email = admin_email
        if de_email is None:
            self.de_email = NOTIEMAIL
            self.contra = NOTI_APPCONTRA
        else:
            self.de_email = de_email    
            self.contra = contra


    def enviar_notificacion(self, para_email, asunto, mensaje):
        msj = MIMEMultipart()
        msj['From'] = self.de_email
        msj['To'] = para_email
        msj['Subject'] = asunto
        
        msj.attach(MIMEText(mensaje, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.de_email, self.contra)
        
        server.sendmail(msj['From'], msj['To'], msj.as_string())
        server.quit()


    #  DONANTE
    def parametros_notificacion_donante(self, para_email, tipo_sangre):
        asunto = "¡Tu ayuda es crucial!"

        mensaje = (
            f"Necesitamos tu ayuda. Sangre tipo {tipo_sangre}."
        )

        mensaje_corto = f"Escasez de sangre tipo {tipo_sangre}. ¡Dona ahora!"

        #  GUARDAR NOTIFICACIÓN (CLAVE)
        agregar_notificacion(para_email, mensaje_corto)

        #  ENVIAR CORREO
        self.enviar_notificacion(para_email, asunto, mensaje)


    #  ADMIN
    def parametros_notificacion_admin(self, tipo_sangre):
        asunto = f"Niveles de sangre {tipo_sangre} bajos"
        mensaje = (
            f"Los niveles de sangre tipo {tipo_sangre} están bajos."
        )
        self.enviar_notificacion(self.admin_email, asunto, mensaje)


    def recuperar_contra_notificacion(self, para_email, codigo):
        asunto = "Recuperación de Contraseña"
        mensaje = (
            f"Tu código de recuperación es:\n\n{codigo}"
        )
        self.enviar_notificacion(para_email, asunto, mensaje)


    def solicitud_notificacion(self, para_email, estado):
        if estado == "Aprobado":
            asunto = "Solicitud aprobada"
            mensaje = "Tu solicitud fue aprobada."
        else:
            asunto = "Solicitud rechazada"
            mensaje = "Tu solicitud fue rechazada."

        self.enviar_notificacion(para_email, asunto, mensaje)


    def redimir_puntos_notificacion(self, para_email, codigo):
        asunto = "Redención de puntos"
        mensaje = (
            f"Has redimido tus puntos.\n\nCódigo: {codigo}"
        )
        self.enviar_notificacion(para_email, asunto, mensaje)