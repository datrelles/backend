from flask_jwt_extended import jwt_required
from flask import Blueprint, jsonify
from sqlalchemy import or_, not_
from src.config.database import db
from src.models.alerta_email import alerta_email, alerta_dias, alerta_email_type, email_type_body
from src.models.users import tg_rol
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
        alertas_ecomerb2b = alerta_email.query().filter_by(cod_alerta='ECOMERB2B').all()
        alertas_ecomer = alerta_email.query().filter_by(cod_alerta='ECOMER').all()

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
def check_range_time(type, rol):
    # Obtener la hora y el día actual
    now = datetime.now()
    current_hour = now.hour
    current_day = now.weekday()  # 0 = lunes, 6 = domingo

    # Consulta para verificar horarios en un rango
    times = alerta_dias.query().filter(
        alerta_dias.cod_alerta == type,
        alerta_dias.rol == rol,
        alerta_dias.dia == current_day,
        or_(
            alerta_dias.hora_inicio <= current_hour,  # Hora de inicio <= hora actual
            alerta_dias.hora_final >= current_hour  # Hora de fin >= hora actual
        )
    ).all()

    # Devolver True si hay resultados, False si no
    return bool(times)
def send_email_sms_outlook(destinatarios, tipo, registro, body_template):

    body = body_template.format(
        id_transaction=registro.id_transaction,
        client_name=registro.client_name,
        client_last_name=registro.client_last_name,
        total=registro.total
    )

    try:
        msg = Message(
            subject=f"Alerta: Pedido sin Comprobante - {tipo}",
            sender="sms@massline.com.ec",
            recipients=destinatarios,
            body=body
        )
        mail.send(msg)
        return {"status": "success", "message": "Correo enviado exitosamente"}
    except Exception as e:
        return {"status": "error", "message": f"Error al enviar el correo: {str(e)}"}
def craft_email_alert_ecommerce(cod_type, rol):
    try:
        # Consultar las tablas cab para registros con cod_comprobante vacío
        registros_datafast = []
        registros_deuna = []
        registros_datafast_b2b = []
        registros_deuna_b2b = []
        registros_credito_directo = []

        if cod_type =='ECOMER':
            registros_datafast = st_cab_datafast.query().filter(st_cab_datafast.cod_comprobante == None).all()
            registros_deuna = st_cab_deuna.query().filter(st_cab_deuna.cod_comprobante == None).all()

        elif cod_type =='ECOMERB2B':
            registros_datafast_b2b = st_cab_datafast_b2b.query().filter(st_cab_datafast_b2b.cod_comprobante == None).all()
            registros_deuna_b2b = st_cab_deuna_b2b.query().filter(st_cab_deuna_b2b.cod_comprobante == None).all()

        elif cod_type =='ECOMCRED':
                registros_credito_directo = st_cab_credito_directo.query().filter(st_cab_credito_directo.cod_comprobante == None).all()

    except Exception as e:
        #print(f"Error al consultar las tablas: {e}")
        return
    try:
        # Obtener el correo del destino
        register_email_destiny = alerta_email.query().filter(alerta_email.cod_alerta == cod_type,
                                                             alerta_email.rol == rol).first()
        body_email_destiny = email_type_body.query().filter(
            email_type_body.cod_alerta == cod_type,
            email_type_body.cod_rol == rol
        ).first()

        if not body_email_destiny:
            #print("No se encontró ningún registro de body." + rol +cod_type)
            return

        if not register_email_destiny:
            #print("No se encontró ningún registro de destino para el correo electrónico.")
            return
        email_destiny = [register_email_destiny.email]
        #print(f"Correo destino: {email_destiny}")

    except Exception as e:
        #print(f"Error al obtener el correo de destino: {e}")
        return

    try:
        # Enviar correos electrónicos
        for registro in registros_datafast + registros_deuna:
            tipo = 'Datafast' if isinstance(registro, st_cab_datafast) else \
                   'De_Una' if isinstance(registro, st_cab_deuna) else None
            try:
                status = send_email_sms_outlook(email_destiny, tipo, registro, body_email_destiny.body_template)
                #print(f"Correo enviado con estado: {status}")
            except Exception as e:
                pass
                #print(f"Error al enviar correo para el registro {registro}: {e}")

        for registrob2b in registros_datafast_b2b + registros_deuna_b2b:
            tipo = 'Datafast B2B' if isinstance(registrob2b, registros_datafast_b2b) else \
                   'De_Una B2B' if isinstance(registrob2b, registros_deuna_b2b) else None
            try:
                status = send_email_sms_outlook(email_destiny, tipo, registrob2b, body_email_destiny.body_template)
                #print(f"Correo enviado con estado: {status}")
            except Exception as e:
                pass
                #print(f"Error al enviar correo para el registro {registrob2b}: {e}")

        for registro_cred in registros_credito_directo:
            tipo = 'Credito Directo' if isinstance(registro_cred, st_cab_credito_directo) else None
            try:
                status = send_email_sms_outlook(email_destiny, tipo, registro_cred, body_email_destiny.body_template)
                #print(f"Correo enviado con estado: {status}")
            except Exception as e:
                pass
                #print(f"Error al enviar correo para el registro {registro_cred}: {e}")


    except Exception as e:
        print(f"Error al procesar los registros: {e}")
def execute_send_alert_emails_for_role():
    try:
        type_alert = alerta_email_type.query().all()
        role_users = tg_rol.query().filter(tg_rol.activo==1)

        for type in type_alert:
            for rol in role_users:
                flag_check_range = check_range_time(type.cod_alerta, rol.cod_rol)
                if flag_check_range:
                    craft_email_alert_ecommerce(type.cod_alerta, rol.cod_rol)
        pass
    except Exception as e:
        pass


# Endpoint para enviar correos (opcional)
@aem.route('/send_alert_emails', methods=['POST'])
@jwt_required()
def send_alert_emails():
    execute_send_alert_emails_for_role()
    return jsonify({"message": "Proceso de envío de correos completado."}), 200
