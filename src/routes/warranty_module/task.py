from flask import current_app, copy_current_request_context
from jinja2 import Template
from src.config.database import db
from src.models.postVenta import st_casos_postventa, st_types_mail_warranty
from flask_mail import Message
from datetime import datetime
import logging
import threading

logger = logging.getLogger(__name__)

def send_mail_postventa(cod_comprobante: str, estado_caso: str):
    @copy_current_request_context
    def _send_mail():
        try:
            # Buscar el caso de postventa mediante el código de comprobante
            caso = st_casos_postventa.query().filter_by(cod_comprobante=cod_comprobante).first()
            if not caso:
                logger.error(f"[ERROR] Caso con comprobante {cod_comprobante} no encontrado.")
                return

            empresa = caso.empresa
            type_modulo = 'WARRANTY'

            # Buscar la plantilla de correo correspondiente
            plantilla = st_types_mail_warranty.query().filter_by(
                empresa=empresa,
                type_modulo=type_modulo,
                estado_caso=estado_caso,
                activo=1
            ).first()
            if not plantilla:
                logger.error(f"[ERROR] No se encontró plantilla para empresa={empresa}, estado={estado_caso}")
                return

            # Renderizar el cuerpo del correo utilizando Jinja2
            template = Template(plantilla.cuerpo_html)
            cuerpo = template.render(
                nombre_cliente=caso.nombre_cliente,
                fecha=caso.fecha.strftime('%d/%m/%Y') if caso.fecha else '---'
            )

            # Recopilar los destinatarios válidos
            recipients = [r for r in [caso.e_mail1, caso.e_mail2] if r]
            if not recipients:
                logger.error(f"[ERROR] Caso {cod_comprobante} no tiene correos válidos.")
                return

            # Obtener la instancia de mail desde current_app
            mail_instance = current_app.extensions.get("mail")
            sender_email = "sms@massline.com.ec"  # Correo remitente

            # Crear y enviar el mensaje
            msg = Message(subject=plantilla.asunto, sender=sender_email, recipients=recipients)
            msg.html = cuerpo
            mail_instance.send(msg)

            logger.info(f"[OK] Correo enviado para caso {cod_comprobante} a {', '.join(recipients)}")
        except Exception as e:
            logger.exception(f"[EXCEPTION] Error al enviar correo para caso {cod_comprobante}: {str(e)}")

    # Ejecutar la tarea en un hilo separado
    thread = threading.Thread(target=_send_mail)
    thread.start()
    # Retornar inmediatamente sin esperar que se complete el envío
    return True
