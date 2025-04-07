from functools import reduce
from flask import request, Blueprint, jsonify
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
import logging
from werkzeug.exceptions import BadRequest
from src.config.database import db
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from src.models.modulo_formulas import st_proceso, st_formula, st_parametro, st_parametros_x_proceso, \
    st_factores_calculo_parametros, tipos_ope_validos, operadores_validos
from src.exceptions.validation import validation_error
from src.validations.alfanumericas import validar_varchar
from src.validations.numericas import validar_number
from src.models.users import Empresa
from src.models.clientes import Cliente

formulas_b = Blueprint('routes_formulas', __name__)
logger = logging.getLogger(__name__)


@formulas_b.route("/procesos", methods=["GET"])
@jwt_required()
@cross_origin()
def get_procesos():
    try:
        empresa = validar_number('empresa', request.args.get('empresa'), 2)
        if not db.session.get(Empresa, empresa):
            mensaje = f'Empresa {empresa} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        query = st_proceso.query()
        procesos = query.filter(st_proceso.empresa == empresa).all()
        return jsonify(st_proceso.to_list(procesos))
    except validation_error as e:
        logger.exception(e)
        return jsonify({'mensaje': str(e)}), 400
    except Exception as e:
        logger.exception(f'Ocurrió una excepción al consultar los procesos: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al consultar los procesos'}), 500


@formulas_b.route("/procesos", methods=["POST"])
@jwt_required()
@cross_origin()
def post_procesos():
    try:
        data = request.get_json()
        proceso = st_proceso(**data)
        if not db.session.get(Empresa, data['empresa']):
            mensaje = f'Empresa {data['empresa']} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if db.session.get(st_proceso, (data['empresa'], data['cod_proceso'])):
            mensaje = f'Ya existe un proceso con el código {data['cod_proceso']}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 409
        db.session.add(proceso)
        db.session.commit()
        mensaje = f'Se registró el proceso {data['cod_proceso']}'
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
        logger.exception(f'Ocurrió una excepción con la base de datos: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error con la base de datos'}), 500
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al registrar el proceso: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al registrar el proceso'}), 500


@formulas_b.route("/procesos", methods=["PUT"])
@jwt_required()
@cross_origin()
def put_procesos():
    try:
        data = request.get_json()
        st_proceso(**data)
        if not db.session.get(Empresa, data['empresa']):
            mensaje = f'Empresa {data['empresa']} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        proceso = db.session.get(st_proceso, (data['empresa'], data['cod_proceso']))
        if not proceso:
            mensaje = f'No existe un proceso con el código {data['cod_proceso']}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        proceso.nombre = data['nombre']
        if data.get('estado') is not None:
            proceso.estado = data['estado']
        proceso.audit_usuario_mod = text('user')
        proceso.audit_fecha_mod = text('sysdate')
        db.session.commit()
        mensaje = f'Se actualizó el proceso {data['cod_proceso']}'
        logger.info(mensaje)
        return jsonify({'mensaje': mensaje}), 204
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
        logger.exception(f'Ocurrió una excepción con la base de datos: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error con la base de datos'}), 500
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al actualizar el proceso: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al actualizar el proceso'}), 500

@formulas_b.route("/procesos", methods=["DELETE"])
@jwt_required()
@cross_origin()
def delete_procesos():
    try:
        empresa = validar_number('empresa', request.args.get('empresa'), 2)
        cod_proceso = validar_varchar('cod_proceso', request.args.get('cod_proceso'), 8)
        if not db.session.get(Empresa, empresa):
            mensaje = f'Empresa {empresa} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        proceso = db.session.get(st_proceso, (empresa, cod_proceso))
        if not proceso:
            mensaje = f'No existe un proceso con el código {cod_proceso}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if db.session.query(st_parametros_x_proceso).filter_by(empresa=empresa, cod_proceso=cod_proceso).first():
            mensaje = f'Existen parámetros vinculados al proceso {cod_proceso}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 409
        db.session.delete(proceso)
        db.session.commit()
        mensaje = f'Se eliminó el proceso {cod_proceso}'
        logger.info(mensaje)
        return '', 204
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
        logger.exception(f'Ocurrió una excepción con la base de datos: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error con la base de datos'}), 500
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al eliminar el proceso: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al eliminar el proceso'}), 500

@formulas_b.route("/formulas", methods=["GET"])
@jwt_required()
@cross_origin()
def get_formulas():
    try:
        empresa = validar_number('empresa', request.args.get('empresa'), 2)
        if not db.session.get(Empresa, empresa):
            mensaje = f'Empresa {empresa} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        query = st_formula.query()
        formulas = query.filter(st_formula.empresa == empresa).all()
        return jsonify(st_formula.to_list(formulas))
    except validation_error as e:
        logger.exception(e)
        return jsonify({'mensaje': str(e)}), 400
    except Exception as e:
        logger.exception(f'Ocurrió una excepción al consultar las fórmulas: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al consultar las fórmulas'}), 500


@formulas_b.route("/formulas", methods=["POST"])
@jwt_required()
@cross_origin()
def post_formulas():
    try:
        data = request.get_json()
        formula = st_formula(**data)
        if not db.session.get(Empresa, data['empresa']):
            mensaje = f'Empresa {data['empresa']} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if db.session.get(st_formula, (data['empresa'], data['cod_formula'])):
            mensaje = f'Ya existe una fórmula con el código {data['cod_formula']}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 409
        db.session.add(formula)
        db.session.commit()
        mensaje = f'Se registró la fórmula {data['cod_formula']}'
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
        logger.exception(f'Ocurrió una excepción con la base de datos: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error con la base de datos'}), 500
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al registrar la fórmula: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al registrar la fórmula'}), 500


@formulas_b.route("/formulas", methods=["PUT"])
@jwt_required()
@cross_origin()
def put_formulas():
    try:
        data = request.get_json()
        st_formula(**data)
        if not db.session.get(Empresa, data['empresa']):
            mensaje = f'Empresa {data['empresa']} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        formula = db.session.get(st_formula, (data['empresa'], data['cod_formula']))
        if not formula:
            mensaje = f'Fórmula {data['cod_formula']} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        formula.nombre = data['nombre']
        formula.observaciones = data.get('observaciones')
        if data.get('estado') is not None:
            formula.estado = data['estado']
        formula.definicion = data['definicion']
        formula.audit_usuario_mod = text('user')
        formula.audit_fecha_mod = text('sysdate')
        db.session.commit()
        mensaje = f'Se actualizó la fórmula {data['cod_formula']}'
        logger.info(mensaje)
        return jsonify({'mensaje': mensaje}), 204
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
        logger.exception(f'Ocurrió una excepción con la base de datos: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error con la base de datos'}), 500
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al actualizar la fórmula: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al actualizar la fórmula'}), 500


@formulas_b.route("/parametros", methods=["GET"])
@jwt_required()
@cross_origin()
def get_parametros():
    try:
        empresa = validar_number('empresa', request.args.get('empresa'), 2)
        if not db.session.get(Empresa, empresa):
            mensaje = f'Empresa {empresa} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        query = st_parametro.query()
        parametros = query.filter(st_parametro.empresa == empresa).all()
        return jsonify(st_parametro.to_list(parametros))
    except validation_error as e:
        db.session.rollback()
        logger.exception(e)
        return jsonify({'mensaje': str(e)}), 400
    except Exception as e:
        logger.exception(f'Ocurrió una excepción al consultar los parámetros: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al consultar los parámetros'}), 500


@formulas_b.route("/parametros", methods=["POST"])
@jwt_required()
@cross_origin()
def post_parametros():
    try:
        data = request.get_json()
        parametro = st_parametro(**data)
        if not db.session.get(Empresa, data['empresa']):
            mensaje = f'Empresa {data['empresa']} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if db.session.get(st_parametro, (data['empresa'], data['cod_parametro'])):
            mensaje = f'Ya existe un parámetro con el código {data['cod_parametro']}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 409
        db.session.add(parametro)
        db.session.commit()
        mensaje = f'Se registró el parámetro {data['cod_parametro']}'
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
        logger.exception(f'Ocurrió una excepción con la base de datos: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error con la base de datos'}), 500
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al registrar el parámetro: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al registrar el parámetro'}), 500


@formulas_b.route("/parametros", methods=["PUT"])
@jwt_required()
@cross_origin()
def put_parametros():
    try:
        data = request.get_json()
        st_parametro(**data)
        if not db.session.get(Empresa, data['empresa']):
            mensaje = f'Empresa {data['empresa']} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        parametro = db.session.get(st_parametro, (data['empresa'], data['cod_parametro']))
        if not parametro:
            mensaje = f'No existe un parámetro con el código {data['cod_parametro']}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        parametro.nombre = data['nombre']
        parametro.descripcion = data.get('descripcion')
        if data.get('estado') is not None:
            parametro.estado = data['estado']
        parametro.audit_usuario_mod = text('user')
        parametro.audit_fecha_mod = text('sysdate')
        db.session.commit()
        mensaje = f'Se actualizó el parámetro {data['cod_parametro']}'
        logger.info(mensaje)
        return jsonify({'mensaje': mensaje}), 204
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
        logger.exception(f'Ocurrió una excepción con la base de datos: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error con la base de datos'}), 500
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al actualizar el parámetro: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al actualizar el parámetro'}), 500


@formulas_b.route("/parametros-x-proceso", methods=["GET"])
@jwt_required()
@cross_origin()
def get_parametros_x_proceso():
    try:
        empresa = validar_number('empresa', request.args.get('empresa'), 2)
        cod_proceso = validar_varchar('cod_proceso', request.args.get('cod_proceso'), 8)
        if not db.session.get(Empresa, empresa):
            mensaje = f'Empresa {empresa} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if not db.session.get(st_proceso, (empresa, cod_proceso)):
            mensaje = f'Proceso {cod_proceso} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        query = st_parametros_x_proceso.query()
        parametros = query.filter(st_parametros_x_proceso.empresa == empresa,
                                  st_parametros_x_proceso.cod_proceso == cod_proceso).order_by(
            st_parametros_x_proceso.orden_imprime).all()
        return jsonify(st_parametro.to_list(parametros))
    except validation_error as e:
        logger.exception(e)
        return jsonify({'mensaje': str(e)}), 400
    except Exception as e:
        logger.exception(f'Ocurrió una excepción al consultar los parámetros vinculados al proceso {cod_proceso}: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al consultar los parámetros vinculados al proceso {cod_proceso}'}), 500


@formulas_b.route("/parametros-x-proceso", methods=["POST"])
@jwt_required()
@cross_origin()
def post_parametros_x_proceso():
    try:
        data = request.get_json()
        parametro_x_proceso = st_parametros_x_proceso(**data)
        if not db.session.get(Empresa, data['empresa']):
            mensaje = f'Empresa {data['empresa']} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if not db.session.get(st_proceso, (data['empresa'], data['cod_proceso'])):
            mensaje = f'Proceso {data['cod_proceso']} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if not db.session.get(st_parametro, (data['empresa'], data['cod_parametro'])):
            mensaje = f'Parámetro {data['cod_parametro']} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if db.session.get(st_parametros_x_proceso, (data['empresa'], data['cod_proceso'], data['cod_parametro'])):
            mensaje = f'El parámetro {data['cod_parametro']} ya está vinculado al proceso {data['cod_proceso']}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 409
        db.session.add(parametro_x_proceso)
        db.session.commit()
        mensaje = f'Se vinculó el parámetro {data['cod_parametro']} al proceso {data['cod_proceso']}'
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
        logger.exception(f'Ocurrió una excepción con la base de datos: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error con la base de datos'}), 500
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al vincular el parámetro al proceso: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al vincular el parámetro al proceso'}), 500


@formulas_b.route("/parametros-x-proceso", methods=["PUT"])
@jwt_required()
@cross_origin()
def put_parametros_x_proceso():
    try:
        data = request.get_json()
        st_parametros_x_proceso(**data)
        if not db.session.get(Empresa, data['empresa']):
            mensaje = f'Empresa {data['empresa']} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if not db.session.get(st_proceso, (data['empresa'], data['cod_proceso'])):
            mensaje = f'Proceso {data['cod_proceso']} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if not db.session.get(st_parametro, (data['empresa'], data['cod_parametro'])):
            mensaje = f'Parámetro {data['cod_parametro']} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        parametro_x_proceso = db.session.get(st_parametros_x_proceso,
                                             (data['empresa'], data['cod_proceso'], data['cod_parametro']))
        if not parametro_x_proceso:
            mensaje = f'El parámetro {data['cod_parametro']} no está vinculado al proceso {data['cod_proceso']}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 409
        parametro_x_proceso.cod_formula = data.get('cod_formula')
        parametro_x_proceso.orden_calculo = data.get('orden_calculo')
        if data.get('estado') is not None:
            parametro_x_proceso.estado = data['estado']
        parametro_x_proceso.fecha_calculo_inicio = data.get('fecha_calculo_inicio')
        parametro_x_proceso.fecha_calculo_fin = data.get('fecha_calculo_fin')
        parametro_x_proceso.orden_imprime = data['orden_imprime']
        parametro_x_proceso.audit_usuario_mod = text('user')
        parametro_x_proceso.audit_fecha_mod = text('sysdate')
        db.session.commit()
        mensaje = f'Se actualizó el parámetro {data['cod_parametro']} vinculado al proceso {data['cod_proceso']}'
        logger.info(mensaje)
        return jsonify({'mensaje': mensaje}), 204
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
        logger.exception(f'Ocurrió una excepción con la base de datos: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error con la base de datos'}), 500
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al vincular el parámetro al proceso: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al vincular el parámetro al proceso'}), 500


@formulas_b.route("/parametros-x-proceso", methods=["DELETE"])
@jwt_required()
@cross_origin()
def delete_parametros_x_proceso():
    try:
        empresa = validar_number('empresa', request.args.get('empresa'), 2)
        cod_proceso = validar_varchar('cod_proceso', request.args.get('cod_proceso'), 8)
        cod_parametro = validar_varchar('cod_parametro', request.args.get('cod_parametro'), 8)
        if not db.session.get(Empresa, empresa):
            mensaje = f'Empresa {empresa} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if not db.session.get(st_proceso, (empresa, cod_proceso)):
            mensaje = f'Proceso {cod_proceso} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if not db.session.get(st_parametro, (empresa, cod_parametro)):
            mensaje = f'Parámetro {cod_parametro} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        parametro_x_proceso = db.session.get(st_parametros_x_proceso, (empresa, cod_proceso, cod_parametro))
        if not parametro_x_proceso:
            mensaje = f'El parámetro {cod_parametro} no está vinculado al proceso {cod_proceso}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if parametro_x_proceso.factores_calculo:
            mensaje = f'Existen factores de cálculo vinculados al proceso {cod_proceso} y parámetro {cod_parametro}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 409
        db.session.delete(parametro_x_proceso)
        db.session.commit()
        mensaje = f'Se desvinculó el parámetro {cod_parametro} del proceso {cod_proceso}'
        logger.info(mensaje)
        return '', 204
    except validation_error as e:
        db.session.rollback()
        logger.exception(e)
        return jsonify({'mensaje': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al desvincular el parámetro del proceso: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al desvincular el parámetro del proceso'}), 500


@formulas_b.route("/factores-calculo-parametros", methods=["GET"])
@jwt_required()
@cross_origin()
def get_factores_calculo_parametros():
    try:
        empresa = validar_number('empresa', request.args.get('empresa'), 2)
        cod_proceso = validar_varchar('cod_proceso', request.args.get('cod_proceso'), 8)
        cod_parametro = validar_varchar('cod_parametro', request.args.get('cod_parametro'), 8)
        if not db.session.get(Empresa, empresa):
            mensaje = f'Empresa {empresa} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if not db.session.get(st_proceso, (empresa, cod_proceso)):
            mensaje = f'Proceso {cod_proceso} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if not db.session.get(st_parametro, (empresa, cod_parametro)):
            mensaje = f'Parámetro {cod_parametro} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if not db.session.get(st_parametros_x_proceso, (empresa, cod_proceso, cod_parametro)):
            mensaje = f'Parámetro por proceso inexistente: proceso ({cod_proceso}), parámetro ({cod_parametro})'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        query = st_factores_calculo_parametros.query()
        factores_calculo = query.filter(st_factores_calculo_parametros.empresa == empresa,
                                        st_factores_calculo_parametros.cod_proceso == cod_proceso,
                                        st_factores_calculo_parametros.cod_parametro == cod_parametro).order_by(
            st_factores_calculo_parametros.orden).all()
        return jsonify(st_factores_calculo_parametros.to_list(factores_calculo))
    except validation_error as e:
        logger.exception(e)
        return jsonify({'mensaje': str(e)}), 400
    except Exception as e:
        logger.exception(
            f'Ocurrió una excepción al consultar los factores de cálculo (proceso ({cod_proceso}), parámetro ({cod_parametro})): {e}')
        return jsonify(
            {
                'mensaje': f'Ocurrió un error al consultar los factores de cálculo: proceso ({cod_proceso}), parámetro ({cod_parametro})'}), 500


@formulas_b.route("/factores-calculo-parametros", methods=["POST"])
@jwt_required()
@cross_origin()
def post_factores_calculo_parametros():
    try:
        data = request.get_json()
        st_factores_calculo_parametros(**data)
        if not db.session.get(Empresa, data['empresa']):
            mensaje = f'Empresa {data['empresa']} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if not db.session.get(st_proceso, (data['empresa'], data['cod_proceso'])):
            mensaje = f'Proceso {data['cod_proceso']} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if not db.session.get(st_parametro, (data['empresa'], data['cod_parametro'])):
            mensaje = f'Parámetro {data['cod_parametro']} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if not db.session.get(st_parametros_x_proceso, (data['empresa'], data['cod_proceso'], data['cod_parametro'])):
            mensaje = f'El parámetro {data['cod_parametro']} no está vinculado al proceso {data['cod_proceso']}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if db.session.get(st_factores_calculo_parametros,
                          (data['empresa'], data['cod_proceso'], data['cod_parametro'], data['orden'])):
            mensaje = f'El factor de cálculo (proceso: {data['cod_proceso']}, parámetro: {data['cod_parametro']}, orden: {data['orden']}) ya existe'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 409
        match data['tipo_operador']:
            case 'PAR':
                if not data.get('cod_parametro_operador'):
                    mensaje = 'Falta el código del parámetro para el operador'
                    logger.error(mensaje)
                    return jsonify({'mensaje': mensaje}), 400
                if not db.session.get(st_parametro, (data['empresa'], data['cod_parametro_operador'])):
                    mensaje = 'Parámetro inexistente para asignar al operador'
                    logger.error(mensaje)
                    return jsonify({'mensaje': mensaje}), 404
                data['operador'] = None
                data['valor_fijo'] = None
            case 'VAL':
                try:
                    float(data.get('valor_fijo'))
                except Exception as e:
                    mensaje = 'El valor fijo para el operador es inválido'
                    logger.error(mensaje)
                    return jsonify({'mensaje': mensaje}), 400
                data['operador'] = None
                data['cod_parametro_operador'] = None
            case 'OPE':
                if not data.get('operador'):
                    mensaje = 'Falta el operador'
                    logger.error(mensaje)
                    return jsonify({'mensaje': mensaje}), 400
                if data['operador'] not in operadores_validos:
                    mensaje = f'Operador inválido, solo se aceptan: {', '.join(operadores_validos)}'
                    logger.error(mensaje)
                    return jsonify({'mensaje': mensaje}), 400
                data['valor_fijo'] = None
                data['cod_parametro_operador'] = None
            case _:
                mensaje = f'Tipo de operador inválido, solo se aceptan: {', '.join(tipos_ope_validos)}'
                logger.error(mensaje)
                return jsonify({'mensaje': mensaje}), 400
        db.session.add(st_factores_calculo_parametros(**data))
        db.session.commit()
        mensaje = f'Se registró el factor de cálculo (proceso: {data['cod_proceso']}, parámetro: {data['cod_parametro']}, orden: {data['orden']})'
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
        logger.exception(f'Ocurrió una excepción con la base de datos: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error con la base de datos'}), 500
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al registrar el factor de cálculo: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al registrar el factor de cálculo'}), 500


@formulas_b.route("/factores-calculo-parametros", methods=["DELETE"])
@jwt_required()
@cross_origin()
def delete_factores_calculo_parametros():
    try:
        empresa = validar_number('empresa', request.args.get('empresa'), 2)
        cod_proceso = validar_varchar('cod_proceso', request.args.get('cod_proceso'), 8)
        cod_parametro = validar_varchar('cod_parametro', request.args.get('cod_parametro'), 8)
        orden = validar_number('orden', request.args.get('orden'), 3)
        if not db.session.get(Empresa, empresa):
            mensaje = f'Empresa {empresa} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if not db.session.get(st_proceso, (empresa, cod_proceso)):
            mensaje = f'Proceso {cod_proceso} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if not db.session.get(st_parametro, (empresa, cod_parametro)):
            mensaje = f'Parámetro {cod_parametro} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if not db.session.get(st_parametros_x_proceso, (empresa, cod_proceso, cod_parametro)):
            mensaje = f'El parámetro {cod_parametro} no está vinculado al proceso {cod_proceso}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        factor_calculo = db.session.get(st_factores_calculo_parametros, (empresa, cod_proceso, cod_parametro, orden))
        if not factor_calculo:
            mensaje = f'Factor de cálculo (proceso: {cod_proceso}, parámetro: {cod_parametro}, orden: {orden}) inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        db.session.delete(factor_calculo)
        db.session.commit()
        mensaje = f'Se eliminó el factor de cálculo (proceso: {cod_proceso}, parámetro: {cod_parametro}, orden: {orden})'
        logger.info(mensaje)
        return '', 204
    except validation_error as e:
        db.session.rollback()
        logger.exception(e)
        return jsonify({'mensaje': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al eliminar el factor de cálculo: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al eliminar el factor de cálculo'}), 500
