from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy import desc
from datetime import datetime, timedelta
from src.config.database import db
from flask_cors import cross_origin
from src.models.auth2.autorizacion import TiOpenAuthorization
from src.models.users import Usuario
from flask_mail import Message
import logging
from src.models.entities.User import User
import secrets
import string
au = Blueprint('routes_auth', __name__)
logger = logging.getLogger(__name__)
from flask_jwt_extended import create_access_token
def generate_random_token():
    # Generar 6 números aleatorios
    random_numbers = ''.join(secrets.choice(string.digits) for _ in range(6))

    # Generar una letra aleatoria
    random_letter = secrets.choice(string.ascii_uppercase)

    # Combinar los números y la letra para formar el token de 7 dígitos
    token = random_numbers + random_letter

    return token

def send_2fa_code(username, code, email_recipient):
    mail = current_app.extensions.get("mail")
    subject = "Código de Autenticación de Dos Factores:"
    body = f"""Estimado/a {username},

La empresa ha implementado un sistema de autenticación de dos factores (2FA).

Su código de autenticación es el siguiente:

{code}

Por favor, introduzca este código cuando se le solicite durante el proceso de inicio de sesión. Este código es válido por 10 minutos.

Si no ha intentado acceder a su cuenta en este momento, le recomendamos que contacte con nuestro equipo de soporte de inmediato.


Atentamente,
El Equipo de Massline
sistemas@massline.com.ec
"""

    # Replace the placeholder with your actual sender email address
    sender_email = "sms@massline.com.ec"

    # Replace the placeholder with your actual recipient email address
    recipients = [email_recipient]

    try:
        msg = Message(subject, sender=sender_email, recipients=recipients)
        msg.body = body
        mail.send(msg)
        print("Email sent successfully.")
        return True  # Indicate that the email was sent successfully
    except Exception as ex:
        print("Error sending email:", ex)
        return False  # Indicate that an error occurred while sending the email



@au.route('/get_authorization')
@jwt_required()
@cross_origin()
def get_auth():

    usuario = request.args.get('usuario', None)
    query = TiOpenAuthorization.query()

    if usuario:
        query = query.filter(TiOpenAuthorization.usuario_oracle.like(f'%{usuario.upper()}%'))
        query = query.order_by(desc(TiOpenAuthorization.fecha_registro))

    auth = query.first()
    serialized_auth = []
    serialized_auth.append({
        'usuario_oracle': auth.usuario_oracle,
        'email': auth.email,
        'cuenta_whatsapp': auth.cuenta_whatsapp,
        'nro_whatsapp': auth.nro_whatsapp,
        'ip_autentica': auth.ip_autentica,
        'fecha_registro': auth.fecha_registro,
        'nombre_host': auth.nombre_host,
        'token': auth.token,
        'valida': auth.valida,
        'mantiene_sesion': auth.mantiene_sesion,
        'navegador_so': auth.navegador_so
        })
    return jsonify(serialized_auth)

@au.route('/set_authorization/<usuario>', methods=['POST'])
@cross_origin()
def set_auth(usuario):
    try:
        data = request.get_json()
        usuario = usuario.upper()
        password = data.get("password", None)
        user = db.session.query(Usuario).filter_by(usuario_oracle=usuario).first()
        if not user:
            return jsonify({'error': 'El usuario no existe.'}), 404

        if not user.e_mail:
            return jsonify({'error': 'Usuario no tiene correo asignado'}), 404
        ##
        isCorrect = User.check_password(user.password,password)
        if not isCorrect:
            return jsonify({'error': 'contraseña Incorrecta' })
        token = generate_random_token()
        print(token)

        usuario = user.usuario_oracle
        email = user.e_mail
        cuenta_whatsapp = data.get('cuenta_whatsapp', None)
        nro_whatsapp = user.celular
        ip_autentica = request.headers.get('X-Forwarded-For') if request.headers.get(
            'X-Forwarded-For') else request.remote_addr
        fecha_registro = datetime.now()
        nombre_host = data.get('nombre_host', None)

        ###Generacion token
        valida = 0
        mantiene_sesion = 0
        navegador_so = data.get('navegador_so', None)

        if len(token) != 7 or token[-1].islower() or token[-1].isdigit():
            return jsonify({'error': 'Formato incorrecto de token'}), 404

        auth = TiOpenAuthorization(
            usuario_oracle = usuario,
            email= email,
            cuenta_whatsapp = cuenta_whatsapp,
            nro_whatsapp = nro_whatsapp,
            ip_autentica = ip_autentica,
            fecha_registro = fecha_registro,
            nombre_host = nombre_host,
            token = token,
            valida = valida,
            mantiene_sesion = mantiene_sesion,
            navegador_so = navegador_so
        )
        db.session.add(auth)
        db.session.commit()
        send_2fa_code(usuario,token, email)
        return jsonify({
            'auth2': 'True',
            'email': email,
            'user': usuario
        })

    except Exception as e:
        logger.exception(f"Error al insertar registro: {str(e)}")
        return jsonify({'error': str(e)}), 500


@au.route('/verify_authorization/<usuario>', methods=['PUT'])
@cross_origin()
def verify_auth(usuario):
    try:
        data = request.get_json()
        #if not data.get('mantiene_sesion') or data.get('mantiene_sesion')=='':
         #   return jsonify({'error': 'Informacion de sesion faltante'}), 404

        usuario = usuario.upper()
        user = db.session.query(Usuario).filter_by(usuario_oracle=usuario).first()

        if not user:
            return jsonify({'error': 'El usuario no existe.'}), 404

        auth = db.session.query(TiOpenAuthorization).filter_by(usuario_oracle=usuario)
        auth = auth.order_by(desc(TiOpenAuthorization.fecha_registro))
        auth = auth.first()

        token = data.get('token', None)

        if len(token)!=7 or token[-1].islower() or token[-1].isdigit():
            return jsonify({'error': 'Formato incorrecto de token'}), 404

        print(token)
        print(auth.token)
        if token == auth.token:
            if datetime.now() - auth.fecha_registro < timedelta(minutes=10):
                auth.valida = 1
                access_token = create_access_token(identity=usuario)
                print(access_token)
                db.session.commit()
                return {
                    "access_token": access_token

                }
            else:
                return jsonify({'error': 'Token expirado'}), 404
        else:
            return jsonify({'error': 'Token Invalido'}), 404

        #mantiene_sesion = data.get('mantiene_sesion', None)
        #auth.mantiene_sesion = mantiene_sesion

    except Exception as e:
        logger.exception(f"Error al editar registro: {str(e)}")
        return jsonify({'error': str(e)}), 500

@au.route('/verify_sesion/<usuario>', methods=['PUT'])
@jwt_required()
@cross_origin()
def verify_session(usuario):
    try:
        data = request.get_json()
        so=data.get('navegador')
        if not data.get('mantiene_sesion') or data.get('mantiene_sesion')=='':
            return jsonify({'error': 'Informacion de sesion faltante'}), 404

        usuario = usuario.upper()
        user = db.session.query(Usuario).filter_by(usuario_oracle=usuario).first()

        if not user:
            return jsonify({'error': 'El usuario no existe.'}), 404

        auth = db.session.query(TiOpenAuthorization).filter_by(usuario_oracle=usuario)
        auth = auth.order_by(desc(TiOpenAuthorization.fecha_registro))
        auth = auth.first()
        mantiene_sesion = data.get('mantiene_sesion', None)
        auth.mantiene_sesion = mantiene_sesion
        auth.navegador_so=so

        db.session.commit()
        return jsonify({'saveDevice': 'successful'})

    except Exception as e:
        logger.exception(f"Error al editar registro: {str(e)}")
        return jsonify({'error': str(e)}), 500