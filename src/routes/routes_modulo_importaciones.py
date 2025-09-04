from flask import request, Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin
import logging
from werkzeug.exceptions import BadRequest
from src.config.database import db
from sqlalchemy.exc import SQLAlchemyError

from src.decorators import validate_json, handle_exceptions
from src.exceptions import validation_error
from src.validations import validar_varchar, validar_number
from src.models.users import Empresa
from src.models.clientes import Cliente
from src.models.modulo_importaciones import st_cabecera_consignacion, st_detalle_consignacion

importaciones_b = Blueprint('routes_importaciones', __name__)
logger = logging.getLogger(__name__)


@importaciones_b.route("/empresas/<empresa>/clientes/<cod_cliente>/cabecera-consignacion", methods=["GET"])
@jwt_required()
@cross_origin()
def get_cabecera_consignacion(empresa, cod_cliente):
    try:
        empresa = validar_number('empresa', empresa, 2)
        cod_cliente = validar_varchar('cod_cliente', cod_cliente, 14)
        query = st_cabecera_consignacion.query()
        cabecera = query.filter(st_cabecera_consignacion.empresa == empresa,
                                st_cabecera_consignacion.cod_cliente == cod_cliente).first()
        if not db.session.get(Empresa, empresa):
            mensaje = 'Empresa {} inexistente'.format(empresa)
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if not db.session.get(Cliente, (empresa, cod_cliente)):
            mensaje = 'Cliente {} inexistente'.format(cod_cliente)
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if cabecera:
            return jsonify(cabecera.to_dict())
        else:
            mensaje = 'No existe cabecera de consignación para el cliente {}'.format(cod_cliente)
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
    except validation_error as e:
        logger.exception(e)
        return jsonify({'mensaje': str(e)}), 400
    except Exception as e:
        logger.exception('Ocurrió una excepción al consultar la cabecera de la consignación: {}'.format(e))
        return jsonify(
            {'mensaje': 'Ocurrió un error al consultar la cabecera de la consignación'}), 500


@importaciones_b.route("/empresas/<empresa>/clientes/<cod_cliente>/cabecera-consignacion", methods=["POST"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("registrar la cabecera de consignación")
def post_cabecera_consignacion(empresa, cod_cliente, data):
    try:
        empresa = validar_number('empresa', empresa, 2)
        cod_cliente = validar_varchar('cod_cliente', cod_cliente, 14)
        data = {'empresa': empresa, 'cod_cliente': cod_cliente, **data, 'audit_usuario_ing': get_jwt_identity()}
        cabecera = st_cabecera_consignacion(**data)
        if db.session.get(st_cabecera_consignacion, (empresa, cod_cliente)):
            mensaje = 'Ya existe una cabecera de consignación para el cliente {}'.format(cod_cliente)
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 409
        if not db.session.get(Empresa, empresa):
            mensaje = 'Empresa {} inexistente'.format(empresa)
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if not db.session.get(Cliente, (empresa, cod_cliente)):
            mensaje = 'Cliente {} inexistente'.format(cod_cliente)
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        db.session.add(cabecera)
        db.session.commit()
        mensaje = 'Se registró la cabecera de consignación para el cliente {}'.format(cod_cliente)
        logger.info(mensaje)
        return jsonify({'mensaje': mensaje}), 201
    except BadRequest as e:
        mensaje = 'Solicitud malformada'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 400
    except validation_error as e:
        db.session.rollback()
        logger.exception(e)
        return jsonify({'mensaje': str(e)}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.exception('Ocurrió una excepción con la base de datos: {}'.format(e))
        return jsonify(
            {'mensaje': 'Ocurrió un error con la base de datos'}), 500
    except Exception as e:
        db.session.rollback()
        logger.exception('Ocurrió una excepción al registrar la cabecera de consignación: {}'.format(e))
        return jsonify(
            {'mensaje': 'Ocurrió un error al registrar la cabecera de consignación'}), 500
