from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import desc
from datetime import datetime
from src.config.database import db
from flask_cors import cross_origin
from src.models.auth2.autorizacion import TiOpenAuthorization
from src.models.users import Usuario
import logging

au = Blueprint('routes_auth', __name__)
logger = logging.getLogger(__name__)

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
@jwt_required()
@cross_origin()
def set_auth(usuario):
    try:
        data = request.get_json()
        usuario = usuario.upper()
        user = db.session.query(Usuario).filter_by(usuario_oracle=usuario).first()

        if not user:
            return jsonify({'error': 'El usuario no existe.'}), 404

        if not user.e_mail:
            return jsonify({'error': 'Usuario no tiene correo asignado'}), 404

        usuario = user.usuario_oracle
        email = user.e_mail
        cuenta_whatsapp = data.get('cuenta_whatsapp', None)
        nro_whatsapp = data.get('nro_whatsapp', None)
        ip_autentica = data.get('ip_autentica', None)
        fecha_registro = datetime.now()
        nombre_host = data.get('nombre_host', None)
        token = data.get('token', None)
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
        return jsonify({'Success': 'Registro de Autorizacion ingresado'})

    except Exception as e:
        logger.exception(f"Error al insertar registro: {str(e)}")
        return jsonify({'error': str(e)}), 500

@au.route('/verify_authorization/<usuario>', methods=['PUT'])
@jwt_required()
@cross_origin()
def verify_auth(usuario):
    try:
        data = request.get_json()
        if not data.get('mantiene_sesion') or data.get('mantiene_sesion')=='':
            return jsonify({'error': 'Informacion de sesion faltante'}), 404

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

        if token == auth.token:
            auth.valida = 1
        else:
            return jsonify({'error': 'Token Invalido'}), 404

        mantiene_sesion = data.get('mantiene_sesion', None)
        auth.mantiene_sesion = mantiene_sesion
        db.session.commit()

        return jsonify({'Success': 'Registro de Autorizacion Actualizado'})

    except Exception as e:
        logger.exception(f"Error al editar registro: {str(e)}")
        return jsonify({'error': str(e)}), 500
