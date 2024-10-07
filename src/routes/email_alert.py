from flask_jwt_extended import jwt_required
from flask import Blueprint, jsonify
from src.config.database import db
from src.models.alerta_email import alert_email
from src.models.st_proforma import st_cab_deuna, st_cab_datafast, st_cab_deuna_b2b, st_cab_datafast_b2b, st_cab_credito_directo
from flask_mail import Message, Mail
import logging
from datetime import datetime

# Configurar el blueprint y el logger
aem = Blueprint('routes_mail_sending', __name__)
logger = logging.getLogger(__name__)

# Configurar Flask-Mail
mail = Mail()

# Función independiente para enviar correos
def execute_send_alert_emails():
    try:
        # Verificar si la tarea debe ejecutarse según el día y la hora
        now = datetime.now()
        current_hour = now.hour
        current_day = now.weekday()  # 0 = Lunes, 6 = Domingo

        # Verificar días y horas: Lunes-Viernes 8:00-18:00, Sábado 8:00-17:00
        if not ((0 <= current_day <= 4 and 8 <= current_hour < 18) or (current_day == 5 and 8 <= current_hour < 17)):
            return  # No ejecutar la tarea fuera de los horarios especificados

        # Consultar las tablas cab para registros con cod_comprobante vacío
        registros_datafast = st_cab_datafast.query().filter(st_cab_datafast.cod_comprobante == None).all()
        registros_deuna = st_cab_deuna.query().filter(st_cab_deuna.cod_comprobante == None).all()
        registros_datafast_b2b = st_cab_datafast_b2b.query().filter(st_cab_datafast_b2b.cod_comprobante == None).all()
        registros_deuna_b2b = st_cab_deuna_b2b.query().filter(st_cab_deuna_b2b.cod_comprobante == None).all()
        registros_credito_directo = st_cab_credito_directo.query().filter(st_cab_credito_directo.cod_comprobante == None).all()

        # Obtener todos los registros de alert_email para los diferentes cod_alerta
        alertas_ecomerb2b = alert_email.query().filter_by(cod_alerta='ECOMERB2B').all()
        alertas_ecomer = alert_email.query().filter_by(cod_alerta='ECOMER').all()

        if not alertas_ecomerb2b and not alertas_ecomer:
            logger.info("No hay correos registrados.")
            return

        # Crear una lista de destinatarios por tipo de alerta
        destinatarios_ecomerb2b = [alert.email for alert in alertas_ecomerb2b]
        destinatarios_ecomer = [alert.email for alert in alertas_ecomer]

        # Función para enviar correos
        def enviar_correo(destinatarios, tipo, registro):
            msg = Message(
                subject=f"Alerta: Pedido sin Comprobante - {tipo}",
                sender="sms@massline.com.ec",
                recipients=destinatarios,
                body=f"El pedido con ID: {registro.id_transaction}, Cliente: {registro.client_name} {registro.client_last_name}, Total: {registro.total} está pendiente de comprobante."
            )
            mail.send(msg)

        # Enviar correos para los registros de B2B
        for registro in registros_datafast_b2b + registros_deuna_b2b:
            enviar_correo(destinatarios_ecomerb2b, 'B2B', registro)

        # Enviar correos para los registros de las demás tablas
        for registro in registros_datafast + registros_deuna + registros_credito_directo:
            tipo = 'Datafast' if isinstance(registro, st_cab_datafast) else 'De_Una' if isinstance(registro, st_cab_deuna) else 'Crédito Directo'
            enviar_correo(destinatarios_ecomer, tipo, registro)

        logger.info("Correos enviados exitosamente.")
    except Exception as e:
        logger.error(f"Error al enviar correos: {e}")

# Endpoint para enviar correos (opcional)
@aem.route('/send_alert_emails', methods=['POST'])
@jwt_required()
def send_alert_emails():
    execute_send_alert_emails()
    return jsonify({"message": "Proceso de envío de correos completado."}), 200
