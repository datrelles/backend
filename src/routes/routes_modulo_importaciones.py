from flask import request, Blueprint, jsonify
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
import logging
from werkzeug.exceptions import BadRequest
from src.config.database import db
from sqlalchemy.exc import IntegrityError, StatementError
from src.exceptions.validation import validation_error
from src.validations.numericas import validar_number
from src.validations.alfanumericas import validar_varchar
from src.models.modulo_importaciones import st_cabecera_consignacion, st_detalle_consignacion

importaciones_b = Blueprint('routes_importaciones', __name__)
logger = logging.getLogger(__name__)


@importaciones_b.route("/cabecera-consignacion", methods=["GET"])
@jwt_required()
@cross_origin()
def get_cabecera_consignacion():
    try:
        empresa = validar_number('empresa', request.args.get('empresa'), 2)
        cod_cliente = validar_varchar('cod_cliente', request.args.get('cod_cliente'), 14)
        query = st_cabecera_consignacion.query()
        cabecera = query.filter(st_cabecera_consignacion.empresa == empresa,
                                st_cabecera_consignacion.cod_cliente == cod_cliente).first()
        if cabecera:
            return jsonify(cabecera.to_dict())
        else:
            mensaje = f'No existe cabecera de consignación para el cliente {cod_cliente}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
    except validation_error as e:
        logger.exception(e)
        return jsonify({'mensaje': str(e)}), 400
    except Exception as e:
        logger.exception(f'Ocurrió una excepción al consultar la cabecera de la consignación: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al consultar la cabecera de la consignación'}), 500


@importaciones_b.route("/cabecera-consignacion", methods=["POST"])
@jwt_required()
@cross_origin()
def post_cabecera_consignacion():
    try:
        data = request.get_json()
        cabecera = st_cabecera_consignacion(**data)
        if db.session.get(st_cabecera_consignacion, (data['empresa'], data['cod_cliente'])):
            mensaje = f'Ya existe una cabecera de consignación para el cliente {data['cod_cliente']}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        db.session.add(cabecera)
        db.session.commit()
        mensaje = f'Se registró la cabecera de consignación para el cliente {data['cod_cliente']}'
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
    except (TypeError, ValueError, StatementError) as e:
        db.session.rollback()
        mensaje = 'Atributos provistos inválidos'
        logger.exception(f'{mensaje}: {e}')
        return jsonify({'mensaje': mensaje}), 400
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al registrar la cabecera de consignación: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al registrar la cabecera de consignación'}), 500
