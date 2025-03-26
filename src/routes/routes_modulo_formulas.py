from flask import request, Blueprint, jsonify
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
import logging
from src.config.database import db
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from src.models.modulo_formulas import Proceso, Formula, Parametro, ParametrosXProceso, FactoresCalculoParametros

formulas_b = Blueprint('routes_formulas', __name__)
logger = logging.getLogger(__name__)

"""
###################################################################################
ENDPOINTS PARA GESTIONAR FÓRMULAS DINÁMICAS
###################################################################################
"""

@formulas_b.route("/procesos", methods=["GET"])
@jwt_required()
@cross_origin()
def get_procesos():
    """
    Endpoint para listar los procesos registrados
    """
    try:
        empresa = request.args.get('empresa')
        if not empresa:
            mensaje = 'Solicitud incompleta'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        query = Proceso.query()
        procesos = query.filter(Proceso.empresa == empresa).all()
        return jsonify(Proceso.to_list(procesos))
    except Exception as e:
        logger.exception(f'Ocurrió una excepción al consultar los procesos: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al consultar los procesos'}), 500


@formulas_b.route("/procesos", methods=["POST"])
@jwt_required()
@cross_origin()
def post_procesos():
    """
    Endpoint para crear un proceso
    """
    try:
        data = request.get_json()
        if not data.get('empresa') or not data.get('cod_proceso') or not data.get('nombre'):
            mensaje = 'Solicitud incompleta'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        proceso = db.session.get(Proceso, (data['empresa'], data['cod_proceso']))
        if proceso:
            mensaje = f'Ya existe un proceso con el código {data['cod_proceso']}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        proceso = Proceso(**data)
        db.session.add(proceso)
        db.session.commit()
        mensaje = f'Se registró el proceso {data['cod_proceso']}'
        logger.info(mensaje)
        return jsonify({'mensaje': mensaje}), 201
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al registrar el proceso: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al registrar el proceso'}), 500


@formulas_b.route("/procesos", methods=["PUT"])
@jwt_required()
@cross_origin()
def put_procesos():
    """
    Endpoint para actualizar un proceso
    """
    try:
        data = request.get_json()
        if not data.get('empresa') or not data.get('cod_proceso') or not data.get('nombre') or not data.get('estado'):
            mensaje = 'Solicitud incompleta'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        proceso = db.session.get(Proceso, (data['empresa'], data['cod_proceso']))
        if not proceso:
            mensaje = f'No existe un proceso con el código {data['cod_proceso']}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        proceso.nombre = data['nombre']
        proceso.estado = data['estado']
        proceso.audit_usuario_mod = text('user')
        proceso.audit_fecha_mod = text('sysdate')
        db.session.commit()
        mensaje = f'Se actualizó el proceso {data['cod_proceso']}'
        logger.info(mensaje)
        return jsonify({'mensaje': mensaje}), 204
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al actualizar el proceso: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al actualizar el proceso'}), 500


@formulas_b.route("/formulas", methods=["GET"])
@jwt_required()
@cross_origin()
def get_formulas():
    """
    Endpoint para listar las fórmulas
    """
    try:
        empresa = request.args.get('empresa')
        if not empresa:
            mensaje = 'Solicitud incompleta'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        query = Formula.query()
        formulas = query.filter(Formula.empresa == empresa).all()
        return jsonify(Formula.to_list(formulas))
    except Exception as e:
        logger.exception(f'Ocurrió una excepción al consultar las fórmulas: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al consultar las fórmulas'}), 500


@formulas_b.route("/formulas", methods=["POST"])
@jwt_required()
@cross_origin()
def post_formulas():
    """
    Endpoint para crear una fórmula
    """
    try:
        data = request.get_json()
        if not data.get('empresa') or not data.get('cod_formula') or not data.get('nombre') or not data.get(
                'definicion'):
            mensaje = 'Solicitud incompleta'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        formula = db.session.get(Formula, (data['empresa'], data['cod_formula']))
        if formula:
            mensaje = f'Ya existe una fórmula con el código {data['cod_formula']}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        formula = Formula(**data)
        db.session.add(formula)
        db.session.commit()
        mensaje = f'Se registró la fórmula {data['cod_formula']}'
        logger.info(mensaje)
        return jsonify({'mensaje': mensaje}), 201
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al registrar la fórmula: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al registrar la fórmula'}), 500


@formulas_b.route("/formulas", methods=["PUT"])
@jwt_required()
@cross_origin()
def put_formulas():
    """
    Endpoint para actualizar una fórmula
    """
    try:
        data = request.get_json()
        if not data.get('empresa') or not data.get('cod_formula') or not data.get('nombre') or not data.get(
                'estado') or not data.get('definicion'):
            mensaje = 'Solicitud incompleta'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        formula = db.session.get(Formula, (data['empresa'], data['cod_formula']))
        if not formula:
            mensaje = f'No existe una fórmula con el código {data['cod_formula']}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        formula.nombre = data['nombre']
        formula.observaciones = data.get('observaciones')
        formula.estado = data['estado']
        formula.definicion = data['definicion']
        formula.audit_usuario_mod = text('user')
        formula.audit_fecha_mod = text('sysdate')
        db.session.commit()
        mensaje = f'Se actualizó la fórmula {data['cod_formula']}'
        logger.info(mensaje)
        return jsonify({'mensaje': mensaje}), 204
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al actualizar la fórmula: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al actualizar la fórmula'}), 500


@formulas_b.route("/parametros", methods=["GET"])
@jwt_required()
@cross_origin()
def get_parametros():
    """
    Endpoint para listar los parámetros
    """
    try:
        empresa = request.args.get('empresa')
        if not empresa:
            mensaje = 'Solicitud incompleta'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        query = Parametro.query()
        parametros = query.filter(Parametro.empresa == empresa).all()
        return jsonify(Parametro.to_list(parametros))
    except Exception as e:
        logger.exception(f'Ocurrió una excepción al consultar los parámetros: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al consultar los parámetros'}), 500


@formulas_b.route("/parametros", methods=["POST"])
@jwt_required()
@cross_origin()
def post_parametros():
    """
    Endpoint para crear un parámetro
    """
    try:
        data = request.get_json()
        if not data.get('empresa') or not data.get('cod_parametro') or not data.get('nombre'):
            mensaje = 'Solicitud incompleta'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        parametro = db.session.get(Parametro, (data['empresa'], data['cod_parametro']))
        if parametro:
            mensaje = f'Ya existe un parámetro con el código {data['cod_parametro']}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        parametro = Parametro(**data)
        db.session.add(parametro)
        db.session.commit()
        mensaje = f'Se registró el parámetro {data['cod_parametro']}'
        logger.info(mensaje)
        return jsonify({'mensaje': mensaje}), 201
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al registrar el parámetro: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al registrar el parámetro'}), 500


@formulas_b.route("/parametros", methods=["PUT"])
@jwt_required()
@cross_origin()
def put_parametros():
    """
    Endpoint para actualizar un parámetro
    """
    try:
        data = request.get_json()
        if not data.get('empresa') or not data.get('cod_parametro') or not data.get('nombre') or not data.get('estado'):
            mensaje = 'Solicitud incompleta'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        parametro = db.session.get(Parametro, (data['empresa'], data['cod_parametro']))
        if not parametro:
            mensaje = f'No existe un parámetro con el código {data['cod_parametro']}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        parametro.nombre = data['nombre']
        parametro.definicion = data.get('definicion')
        parametro.estado = data['estado']
        parametro.audit_usuario_mod = text('user')
        parametro.audit_fecha_mod = text('sysdate')
        db.session.commit()
        mensaje = f'Se actualizó el parámetro {data['cod_parametro']}'
        logger.info(mensaje)
        return jsonify({'mensaje': mensaje}), 204
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al actualizar el parámetro: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al actualizar el parámetro'}), 500


@formulas_b.route("/parametros-x-proceso", methods=["GET"])
@jwt_required()
@cross_origin()
def get_parametros_x_proceso():
    """
    Endpoint para listar los parámetros por proceso
    """
    try:
        empresa = request.args.get('empresa')
        cod_proceso = request.args.get('cod_proceso')
        if not empresa or not cod_proceso:
            mensaje = 'Solicitud incompleta'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        if not db.session.get(Proceso, (empresa, cod_proceso)):
            mensaje = f'Proceso {cod_proceso} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        query = ParametrosXProceso.query()
        parametros = query.filter(ParametrosXProceso.empresa == empresa,
                                  ParametrosXProceso.cod_proceso == cod_proceso).order_by(
            ParametrosXProceso.orden_imprime).all()
        return jsonify(Parametro.to_list(parametros))
    except Exception as e:
        logger.exception(f'Ocurrió una excepción al consultar los parámetros vinculados al proceso {cod_proceso}: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al consultar los parámetros vinculados al proceso {cod_proceso}'}), 500


@formulas_b.route("/parametros-x-proceso", methods=["POST"])
@jwt_required()
@cross_origin()
def post_parametros_x_proceso():
    """
    Endpoint para crear un parámetro por proceso, es decir, vincular un parámetro a un proceso
    """
    try:
        data = request.get_json()
        if not data.get('empresa') or not data.get('cod_proceso') or not data.get('cod_parametro') or not data.get(
                'orden_imprime'):
            mensaje = 'Solicitud incompleta'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        parametro_x_proceso = db.session.get(ParametrosXProceso,
                                             (data['empresa'], data['cod_proceso'], data['cod_parametro']))
        if parametro_x_proceso:
            mensaje = f'El parámetro {data['cod_parametro']} ya está vinculado al proceso {data['cod_proceso']}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 409
        parametro_x_proceso = ParametrosXProceso(**data)
        db.session.add(parametro_x_proceso)
        db.session.commit()
        mensaje = f'Se vinculó el parámetro {data['cod_parametro']} al proceso {data['cod_proceso']}'
        logger.info(mensaje)
        return jsonify({'mensaje': mensaje}), 201
    except IntegrityError as e:
        db.session.rollback()
        logger.exception(f'Proceso y/o parámetro inexistentes: {e}')
        return jsonify(
            {'mensaje': f'Proceso y/o parámetro inexistentes'}), 400
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al vincular el parámetro al proceso: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al vincular el parámetro al proceso'}), 500


@formulas_b.route("/parametros-x-proceso", methods=["PUT"])
@jwt_required()
@cross_origin()
def put_parametros_x_proceso():
    """
    Endpoint para actualizar un parámetro por proceso, es decir, cambiar atributos de un parámetro vinculado a un proceso
    """
    try:
        data = request.get_json()
        if not data.get('empresa') or not data.get('cod_proceso') or not data.get('cod_parametro') or not data.get(
                'estado') or data.get('orden_imprime') is None or not str(data['orden_imprime']).isdigit():
            mensaje = 'Solicitud incompleta'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        if not db.session.get(Proceso, (data['empresa'], data['cod_proceso'])):
            mensaje = f'Proceso {data['cod_proceso']} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        if not db.session.get(Parametro, (data['empresa'], data['cod_parametro'])):
            mensaje = f'Parámetro {data['cod_parametro']} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        parametro_x_proceso = db.session.get(ParametrosXProceso,
                                             (data['empresa'], data['cod_proceso'], data['cod_parametro']))
        if not parametro_x_proceso:
            mensaje = f'El parámetro {data['cod_parametro']} no está vinculado al proceso {data['cod_proceso']}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 409
        parametro_x_proceso.cod_formula = data.get('cod_formula')
        parametro_x_proceso.orden_calculo = data.get('orden_calculo')
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
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al vincular el parámetro al proceso: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al vincular el parámetro al proceso'}), 500


@formulas_b.route("/parametros-x-proceso", methods=["DELETE"])
@jwt_required()
@cross_origin()
def delete_parametros_x_proceso():
    """
    Endpoint para eliminar un parámetro por proceso, es decir, desvincular un parámetro de un proceso
    """
    try:
        args = request.args
        empresa = args.get('empresa')
        cod_proceso = args.get('cod_proceso')
        cod_parametro = args.get('cod_parametro')
        if not empresa or not cod_proceso or not cod_parametro:
            mensaje = 'Solicitud incompleta'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        if not db.session.get(Proceso, (empresa, cod_proceso)):
            mensaje = f'Proceso {cod_proceso} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        if not db.session.get(Parametro, (empresa, cod_parametro)):
            mensaje = f'Parámetro {cod_parametro} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        parametro_x_proceso = db.session.get(ParametrosXProceso, (empresa, cod_proceso, cod_parametro))
        if not parametro_x_proceso:
            mensaje = f'El parámetro {cod_parametro} no está vinculado al proceso {cod_proceso}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        if parametro_x_proceso.factores_calculo:
            mensaje = f'Existen factores de cálculo vinculados al proceso {cod_proceso} y parámetro {cod_parametro} '
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        db.session.delete(parametro_x_proceso)
        db.session.commit()
        mensaje = f'Se desvinculó el parámetro {cod_parametro} del proceso {cod_proceso}'
        logger.info(mensaje)
        return jsonify({'mensaje': mensaje}), 204
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al desvincular el parámetro del proceso: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al desvincular el parámetro del proceso'}), 500


@formulas_b.route("/factores-calculo-parametros", methods=["GET"])
@jwt_required()
@cross_origin()
def get_factores_calculo_parametros():
    """
    Endpoint para listar los factores de cálculo de los parámetros
    """
    try:
        empresa = request.args.get('empresa')
        cod_proceso = request.args.get('cod_proceso')
        cod_parametro = request.args.get('cod_parametro')
        if not empresa or not cod_proceso or not cod_parametro:
            mensaje = 'Solicitud incompleta'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        if not db.session.get(ParametrosXProceso, (empresa, cod_proceso, cod_parametro)):
            mensaje = f'Parámetros por proceso inexistente: proceso ({cod_proceso}), parámetro ({cod_parametro})'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        query = FactoresCalculoParametros.query()
        factores_calculo = query.filter(FactoresCalculoParametros.empresa == empresa,
                                        FactoresCalculoParametros.cod_proceso == cod_proceso,
                                        FactoresCalculoParametros.cod_parametro == cod_parametro).order_by(
            FactoresCalculoParametros.orden).all()
        return jsonify(FactoresCalculoParametros.to_list(factores_calculo))
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
    """
    Endpoint para crear un factor de cálculo de un parámetro
    """
    try:
        data = request.get_json()
        if not data.get('empresa') or not data.get('cod_proceso') or not data.get('cod_parametro') or not data.get(
                'orden') or not data.get('tipo_operador'):
            mensaje = 'Solicitud incompleta'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        factor_calculo = db.session.get(FactoresCalculoParametros,
                                        (data['empresa'], data['cod_proceso'], data['cod_parametro'], data['orden']))
        if factor_calculo:
            mensaje = f'El factor de cálculo (parámetro: {data['cod_parametro']}, orden: {data['orden']}) ya existe'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 409
        factor_calculo = FactoresCalculoParametros(**data)
        match factor_calculo.tipo_operador:
            case 'PAR':
                if not data.get('cod_parametro_operador'):
                    mensaje = 'Falta el código del parámetro para el operador'
                    logger.error(mensaje)
                    return jsonify({'mensaje': mensaje}), 400
                if not db.session.get(Parametro, (data['empresa'], data['cod_parametro_operador'])):
                    mensaje = 'Parámetro inexistente para asignar al operador'
                    logger.error(mensaje)
                    return jsonify({'mensaje': mensaje}), 400
            case 'VAL':
                try:
                    float(data.get('valor_fijo'))
                except Exception as e:
                    mensaje = 'El valor fijo para el operador es inválido'
                    logger.error(mensaje)
                    return jsonify({'mensaje': mensaje}), 400
            case 'OPE':
                if not data.get('operador'):
                    mensaje = 'Falta el operador'
                    logger.error(mensaje)
                    return jsonify({'mensaje': mensaje}), 400
                if data['operador'] not in ('+', '-', '*', '/'):
                    mensaje = 'Operador inválido'
                    logger.error(mensaje)
                    return jsonify({'mensaje': mensaje}), 400
        db.session.add(factor_calculo)
        db.session.commit()
        mensaje = f'Se registró el factor de cálculo (parámetro: {data['cod_parametro']}, orden: {data['orden']})'
        logger.info(mensaje)
        return jsonify({'mensaje': mensaje}), 201
    except IntegrityError as e:
        db.session.rollback()
        logger.exception(f'Proceso y/o parámetro inexistentes: {e}')
        return jsonify(
            {'mensaje': f'Proceso y/o parámetro inexistentes'}), 400
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al registrar el factor de cálculo: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al registrar el factor de cálculo'}), 500


@formulas_b.route("/factores-calculo-parametros", methods=["DELETE"])
@jwt_required()
@cross_origin()
def delete_factores_calculo_parametros():
    """
    Endpoint para eliminar un factor de cálculo
    """
    try:
        args = request.args
        empresa = args.get('empresa')
        cod_proceso = args.get('cod_proceso')
        cod_parametro = args.get('cod_parametro')
        orden = args.get('orden')
        if not empresa or not cod_proceso or not cod_parametro or not orden:
            mensaje = 'Solicitud incompleta'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        factor_calculo = db.session.get(FactoresCalculoParametros, (empresa, cod_proceso, cod_parametro, orden))
        if not factor_calculo:
            mensaje = f'Factor de cálculo (proceso: {cod_proceso}, parámetro: {cod_parametro}, orden: {orden}) inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        db.session.delete(factor_calculo)
        db.session.commit()
        mensaje = f'Se eliminó el factor de cálculo (proceso: {cod_proceso}, parámetro: {cod_parametro}, orden: {orden})'
        logger.info(mensaje)
        return jsonify({'mensaje': mensaje}), 204
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Ocurrió una excepción al eliminar el factor de cálculo: {e}')
        return jsonify(
            {'mensaje': f'Ocurrió un error al eliminar el factor de cálculo'}), 500
