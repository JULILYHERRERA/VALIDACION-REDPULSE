from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from secret_config import NOTIEMAIL, NOTI_APPCONTRA, ADMINEMAIL


class Notificaciones:
    def __init__(self,de_email=None, contra=None, admin_email=ADMINEMAIL):
        self.admin_email = admin_email
        if None in [de_email]:
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
    
    def parametros_notificacion_donante(self, para_email, tipo_sangre):
            asunto = "¡Tu ayuda es crucial! Necesitamos que te acerques a nuestro centro de donacion!"
            mensaje = (
                f"Espero que estés bien. Nos gustaría informarte sobre una importante accion que se llevará a cabo. "
                f"Necesitamos de tu presencia en nuestro centro de donación ya que es una situación crítica porque estamos en necesidad urgente de sangre de tipo {tipo_sangre}. "
                f"Como donante valioso, tu participación puede marcar la diferencia en la vida de muchos pacientes que dependen de transfusiones. "
                f"La donación es rápida y segura, y cada gota cuenta, gracias."
            )
            self.enviar_notificacion(para_email, asunto, mensaje)

    def parametros_notificacion_admin(self, tipo_sangre):
        asunto = f"Niveles de sangre {tipo_sangre} bajos"
        mensaje = (
            f"Los niveles actuales de la sangre de tipo {tipo_sangre} se encuentran por debajo de lo recomendado, "
            "se le ha notificado a todos los donantes con ese tipo de sangre especifico, es recomendable tomar medidas para retomar niveles seguros de sangre."
        )
        self.enviar_notificacion(self.admin_email, asunto, mensaje)

    def recuperar_contra_notificacion(self, para_email, codigo):
        codigo_recuperacion = f"Tu código de confirmación es: {codigo}" #cambiar cuando tengamos el deploy
        asunto = "Recuperación de Contraseña"
        mensaje = (
            f"Has solicitado restablecer tu contraseña. Para continuar, copia y pega en nuestra pagina web el siguiente codigo:\n\n"
            f"{codigo_recuperacion}\n\n"
            "Con este codigo puedes restaurar tu contraseña. Si no solicitaste este cambio, puedes ignorar este mensaje."
        )
        self.enviar_notificacion(para_email, asunto, mensaje)

         
    def solicitud_notificacion(self, para_email, estado):
        asunto = ""
        if(estado == "Aprobado"):
            asunto = "Solicitud de sangre aprobada"
            res = "aprobada. Puede reclamarla en nuestro punto oficial de atención o, si lo prefiere, comuníquese con nosotros para obtener más detalles."
        else:
            asunto = "Solicitud de sangre denegada"
            res = "denegada. Si desea obtener información adicional, no dude en ponerse en contacto con nosotros."
        mensaje = "Su solicitud ha sido " + res
        self.enviar_notificacion(para_email, asunto, mensaje)

    def redimir_puntos_notificacion(self, para_email, codigo):
        asunto = "Redención de puntos"
        mensaje = (
                    "Gracias por redimir sus puntos en nuestro sistema de recompensas. "
                    "Su solicitud ha sido procesada con éxito, y a continuación le proporcionamos su código de bono:\n\n"
                    f"Código de Bono: {codigo}\n\n"
                    "Puede utilizar este código para disfrutar de su recompensa. "
                    "Si necesita asistencia adicional o tiene alguna pregunta, estamos aquí para ayudarle."
                    )
        self.enviar_notificacion(para_email, asunto, mensaje)