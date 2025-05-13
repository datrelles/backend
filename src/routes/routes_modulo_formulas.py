from functools import reduce
from flask import request, Blueprint, jsonify
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
import logging
from src.config.database import db
from sqlalchemy import text, and_, func
from src.decorators import validate_json, handle_exceptions
from src.enums import tipo_factor, operador, tipo_parametro
from src.models.custom_base import custom_base
from src.models.modulo_formulas import st_proceso, st_formula_proceso, st_parametro_proceso, st_parametro_por_proceso, \
    st_factor_calculo_parametro, st_funcion, validar_cod, tg_sistema, st_parametro_funcion, validar_estado
from src.validations import validar_varchar, validar_number
from src.models.users import Empresa
from src.models.clientes import Cliente

formulas_b = Blueprint('routes_formulas', __name__)
logger = logging.getLogger(__name__)


@formulas_b.route("/empresas/<empresa>/procesos/<cod_proceso>", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar el proceso")
def get_proceso(empresa, cod_proceso):
    empresa = validar_number('empresa', empresa, 2)
    cod_proceso = validar_varchar('cod_proceso', cod_proceso, 8)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    proceso = db.session.get(st_proceso, (empresa, cod_proceso))
    if not proceso:
        mensaje = f'Proceso {cod_proceso} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    return jsonify(proceso.to_dict())


@formulas_b.route("/empresas/<empresa>/procesos", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar los procesos")
def get_procesos(empresa):
    empresa = validar_number('empresa', empresa, 2)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    query = st_proceso.query()
    procesos = query.filter(st_proceso.empresa == empresa).order_by(st_proceso.cod_proceso).all()
    return jsonify(st_proceso.to_list(procesos))


@formulas_b.route("/empresas/<empresa>/procesos", methods=["POST"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("registrar el proceso")
def post_proceso(empresa, data):
    empresa = validar_number('empresa', empresa, 2)
    data = {'empresa': empresa, **data}
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
    mensaje = f'Se registró el proceso {proceso.cod_proceso}'
    logger.info(mensaje)
    return jsonify({'mensaje': mensaje}), 201


@formulas_b.route("/empresas/<empresa>/procesos/<cod_proceso>", methods=["PUT"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("actualizar el proceso")
def put_proceso(empresa, cod_proceso, data):
    empresa = validar_number('empresa', empresa, 2)
    cod_proceso = validar_varchar('cod_proceso', cod_proceso, 8)
    data = {'empresa': empresa, 'cod_proceso': cod_proceso, **data}
    st_proceso(**data)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    proceso = db.session.get(st_proceso, (empresa, cod_proceso))
    if not proceso:
        mensaje = f'No existe un proceso con el código {cod_proceso}'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    proceso.nombre = data['nombre']
    if data.get('estado') is not None:
        proceso.estado = data['estado']
    proceso.audit_usuario_mod = text('user')
    proceso.audit_fecha_mod = text('sysdate')
    db.session.commit()
    mensaje = f'Se actualizó el proceso {cod_proceso}'
    logger.info(mensaje)
    return '', 204


@formulas_b.route("/empresas/<empresa>/procesos/<cod_proceso>", methods=["DELETE"])
@jwt_required()
@cross_origin()
@handle_exceptions("eliminar el proceso")
def delete_proceso(empresa, cod_proceso):
    empresa = validar_number('empresa', empresa, 2)
    cod_proceso = validar_varchar('cod_proceso', cod_proceso, 8)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    proceso = db.session.get(st_proceso, (empresa, cod_proceso))
    if not proceso:
        mensaje = f'No existe un proceso con el código {cod_proceso}'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if db.session.query(st_parametro_por_proceso).filter_by(empresa=empresa, cod_proceso=cod_proceso).first():
        mensaje = f'Existen parámetros vinculados al proceso {cod_proceso}'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    db.session.delete(proceso)
    db.session.commit()
    mensaje = f'Se eliminó el proceso {cod_proceso}'
    logger.info(mensaje)
    return '', 204


@formulas_b.route("/empresas/<empresa>/formulas/<cod_formula>", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar la fórmula")
def get_formula_proceso(empresa, cod_formula):
    empresa = validar_number('empresa', empresa, 2)
    cod_formula = validar_varchar('cod_formula', cod_formula, 8)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    formula = db.session.get(st_formula_proceso, (empresa, cod_formula))
    if not formula:
        mensaje = f'Fórmula {cod_formula} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    return jsonify(formula.to_dict())


@formulas_b.route("/empresas/<empresa>/formulas", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar las fórmulas")
def get_formulas_proceso(empresa):
    empresa = validar_number('empresa', empresa, 2)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    query = st_formula_proceso.query()
    formulas = query.filter(st_formula_proceso.empresa == empresa).order_by(st_formula_proceso.cod_formula).all()
    return jsonify(st_formula_proceso.to_list(formulas))


@formulas_b.route("/empresas/<empresa>/formulas", methods=["POST"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("registrar la fórmula")
def post_formula_proceso(empresa, data):
    empresa = validar_number('empresa', empresa, 2)
    data = {'empresa': empresa, **data}
    formula = st_formula_proceso(**data)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if db.session.get(st_formula_proceso, (empresa, data['cod_formula'])):
        mensaje = f'Ya existe una fórmula con el código {data['cod_formula']}'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    db.session.add(formula)
    db.session.commit()
    mensaje = f'Se registró la fórmula {formula.cod_formula}'
    logger.info(mensaje)
    return jsonify({'mensaje': mensaje}), 201


@formulas_b.route("/empresas/<empresa>/formulas/<cod_formula>", methods=["PUT"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("actualizar la fórmula")
def put_formula_proceso(empresa, cod_formula, data):
    empresa = validar_number('empresa', empresa, 2)
    cod_formula = validar_varchar('cod_formula', cod_formula, 8)
    data = {'empresa': empresa, 'cod_formula': cod_formula, **data}
    st_formula_proceso(**data)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    formula = db.session.get(st_formula_proceso, (empresa, cod_formula))
    if not formula:
        mensaje = f'Fórmula {cod_formula} inexistente'
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
    mensaje = f'Se actualizó la fórmula {cod_formula}'
    logger.info(mensaje)
    return '', 204


@formulas_b.route("/empresas/<empresa>/formulas/<cod_formula>", methods=["DELETE"])
@jwt_required()
@cross_origin()
@handle_exceptions("eliminar la fórmula")
def delete_formula_proceso(empresa, cod_formula):
    empresa = validar_number('empresa', empresa, 2)
    cod_formula = validar_varchar('cod_formula', cod_formula, 8)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    formula = db.session.get(st_formula_proceso, (empresa, cod_formula))
    if not formula:
        mensaje = f'No existe una fórmula con el código {cod_formula}'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    parametro_x_proceso = db.session.query(st_parametro_por_proceso).filter_by(empresa=empresa,
                                                                               cod_formula=cod_formula).first()
    if parametro_x_proceso:
        mensaje = f'La fórmula {cod_formula} está vinculada al parámetro {parametro_x_proceso.cod_parametro} del proceso {parametro_x_proceso.cod_proceso}'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    db.session.delete(formula)
    db.session.commit()
    mensaje = f'Se eliminó la fórmula {cod_formula}'
    logger.info(mensaje)
    return '', 204


@formulas_b.route("/empresas/<empresa>/parametros/<cod_parametro>", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar el parámetro")
def get_parametro_proceso(empresa, cod_parametro):
    empresa = validar_number('empresa', empresa, 2)
    cod_parametro = validar_varchar('cod_parametro', cod_parametro, 8)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    parametro = db.session.get(st_parametro_proceso, (empresa, cod_parametro))
    if not parametro:
        mensaje = f'Parámetro {cod_parametro} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    return jsonify(parametro.to_dict())


@formulas_b.route("/empresas/<empresa>/parametros", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar los parámetros")
def get_parametros_proceso(empresa):
    empresa = validar_number('empresa', empresa, 2)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    query = st_parametro_proceso.query()
    parametros = query.filter(st_parametro_proceso.empresa == empresa).order_by(
        st_parametro_proceso.cod_parametro).all()
    return jsonify(st_parametro_proceso.to_list(parametros))


@formulas_b.route("/empresas/<empresa>/parametros", methods=["POST"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("registrar el parámetro")
def post_parametro_proceso(empresa, data):
    empresa = validar_number('empresa', empresa, 2)
    data = {'empresa': empresa, **data}
    parametro = st_parametro_proceso(**data)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if db.session.get(st_parametro_proceso, (empresa, data['cod_parametro'])):
        mensaje = f'Ya existe un parámetro con el código {data['cod_parametro']}'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    db.session.add(parametro)
    db.session.commit()
    mensaje = f'Se registró el parámetro {parametro.cod_parametro}'
    logger.info(mensaje)
    return jsonify({'mensaje': mensaje}), 201


@formulas_b.route("/empresas/<empresa>/parametros/<cod_parametro>", methods=["PUT"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("actualizar el parámetro")
def put_parametro_proceso(empresa, cod_parametro, data):
    empresa = validar_number('empresa', empresa, 2)
    cod_parametro = validar_varchar('cod_parametro', cod_parametro, 8)
    data = {'empresa': empresa, 'cod_parametro': cod_parametro, **data}
    st_parametro_proceso(**data)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    parametro = db.session.get(st_parametro_proceso, (empresa, cod_parametro))
    if not parametro:
        mensaje = f'No existe un parámetro con el código {cod_parametro}'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    parametro.nombre = data['nombre']
    parametro.descripcion = data.get('descripcion')
    if data.get('estado') is not None:
        parametro.estado = data['estado']
    parametro.audit_usuario_mod = text('user')
    parametro.audit_fecha_mod = text('sysdate')
    db.session.commit()
    mensaje = f'Se actualizó el parámetro {cod_parametro}'
    logger.info(mensaje)
    return '', 204


@formulas_b.route("/empresas/<empresa>/parametros/<cod_parametro>", methods=["DELETE"])
@jwt_required()
@cross_origin()
@handle_exceptions("eliminar el parámetro")
def delete_parametro_proceso(empresa, cod_parametro):
    empresa = validar_number('empresa', empresa, 2)
    cod_parametro = validar_varchar('cod_parametro', cod_parametro, 8)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    parametro = db.session.get(st_parametro_proceso, (empresa, cod_parametro))
    if not parametro:
        mensaje = f'No existe un parámetro con el código {cod_parametro}'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    parametro_x_proceso = db.session.query(st_parametro_por_proceso).filter_by(empresa=empresa,
                                                                               cod_parametro=cod_parametro).first()
    if parametro_x_proceso:
        mensaje = f'El parámetro {cod_parametro} está vinculado al proceso {parametro_x_proceso.cod_proceso}'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    db.session.delete(parametro)
    db.session.commit()
    mensaje = f'Se eliminó el parámetro {cod_parametro}'
    logger.info(mensaje)
    return '', 204


@formulas_b.route("/empresas/<empresa>/procesos/<cod_proceso>/parametros", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar los parámetros vinculados al proceso")
def get_parametros_por_proceso(empresa, cod_proceso):
    empresa = validar_number('empresa', empresa, 2)
    cod_proceso = validar_varchar('cod_proceso', cod_proceso, 8)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_proceso, (empresa, cod_proceso)):
        mensaje = f'Proceso {cod_proceso} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    query = st_parametro_por_proceso.query()
    parametros = query.filter(st_parametro_por_proceso.empresa == empresa,
                              st_parametro_por_proceso.cod_proceso == cod_proceso).order_by(
        st_parametro_por_proceso.orden_imprime).all()
    return jsonify(st_parametro_por_proceso.to_list(parametros, False, 'parametro'))


@formulas_b.route("/empresas/<empresa>/procesos/<cod_proceso>/parametros/<cod_parametro>", methods=["POST"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("vincular el parámetro al proceso")
def post_parametro_por_proceso(empresa, cod_proceso, cod_parametro, data):
    empresa = validar_number('empresa', empresa, 2)
    cod_proceso = validar_varchar('cod_proceso', cod_proceso, 8)
    cod_parametro = validar_varchar('cod_parametro', cod_parametro, 8)
    data = {'empresa': empresa, 'cod_proceso': cod_proceso, 'cod_parametro': cod_parametro, **data}
    parametro_x_proceso = st_parametro_por_proceso(**data)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_proceso, (empresa, cod_proceso)):
        mensaje = f'Proceso {cod_proceso} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_parametro_proceso, (empresa, cod_parametro)):
        mensaje = f'Parámetro {cod_parametro} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if db.session.get(st_parametro_por_proceso, (empresa, cod_proceso, cod_parametro)):
        mensaje = f'El parámetro {cod_parametro} ya está vinculado al proceso {cod_proceso}'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    db.session.add(parametro_x_proceso)
    db.session.commit()
    mensaje = f'Se vinculó el parámetro {cod_parametro} al proceso {cod_proceso}'
    logger.info(mensaje)
    return jsonify({'mensaje': mensaje}), 201


@formulas_b.route("/empresas/<empresa>/procesos/<cod_proceso>/parametros/<cod_parametro>", methods=["PUT"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("actualizar el parámetro vinculado al proceso")
def put_parametro_por_proceso(empresa, cod_proceso, cod_parametro, data):
    empresa = validar_number('empresa', empresa, 2)
    cod_proceso = validar_varchar('cod_proceso', cod_proceso, 8)
    cod_parametro = validar_varchar('cod_parametro', cod_parametro, 8)
    data = {'empresa': empresa, 'cod_proceso': cod_proceso, 'cod_parametro': cod_parametro, **data}
    st_parametro_por_proceso(**data)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_proceso, (empresa, cod_proceso)):
        mensaje = f'Proceso {cod_proceso} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_parametro_proceso, (empresa, cod_parametro)):
        mensaje = f'Parámetro {cod_parametro} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    parametro_x_proceso = db.session.get(st_parametro_por_proceso,
                                         (empresa, cod_proceso, cod_parametro))
    if not parametro_x_proceso:
        mensaje = f'El parámetro {cod_parametro} no está vinculado al proceso {cod_proceso}'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    parametro_x_proceso.orden_calculo = data.get('orden_calculo')
    estado = validar_estado('estado', data.get('estado'), False)
    if estado:
        parametro_x_proceso.estado = estado
    cod_formula = validar_cod('cod_formula', data.get('cod_formula'), False)
    if cod_formula:
        if not db.session.get(st_formula_proceso, (empresa, cod_formula)):
            mensaje = f'Fórmula {cod_formula} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
        if data.get('fecha_calculo_inicio') and data.get('fecha_calculo_fin'):
            parametro_x_proceso.fecha_calculo_inicio = data.get('fecha_calculo_inicio')
            parametro_x_proceso.fecha_calculo_fin = data.get('fecha_calculo_fin')
        elif data.get('fecha_calculo_inicio') or data.get('fecha_calculo_fin'):
            mensaje = f'Se deben proporcionar ambas fechas o ninguna'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        else:
            parametro_x_proceso.fecha_calculo_inicio = None
            parametro_x_proceso.fecha_calculo_fin = None
    else:
        if data.get('fecha_calculo_inicio') or data.get('fecha_calculo_fin'):
            mensaje = 'Solo se deben proporcionar fechas cuando se ha especificado una fórmula'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
    parametro_x_proceso.cod_formula = cod_formula
    parametro_x_proceso.orden_imprime = data['orden_imprime']
    parametro_x_proceso.audit_usuario_mod = text('user')
    parametro_x_proceso.audit_fecha_mod = text('sysdate')
    db.session.commit()
    mensaje = f'Se actualizó el parámetro {cod_parametro} vinculado al proceso {cod_proceso}'
    logger.info(mensaje)
    return '', 204


@formulas_b.route("/empresas/<empresa>/procesos/<cod_proceso>/parametros/<cod_parametro>", methods=["DELETE"])
@jwt_required()
@cross_origin()
@handle_exceptions("desvincular el parámetro del proceso")
def delete_parametro_por_proceso(empresa, cod_proceso, cod_parametro):
    empresa = validar_number('empresa', empresa, 2)
    cod_proceso = validar_varchar('cod_proceso', cod_proceso, 8)
    cod_parametro = validar_varchar('cod_parametro', cod_parametro, 8)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_proceso, (empresa, cod_proceso)):
        mensaje = f'Proceso {cod_proceso} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_parametro_proceso, (empresa, cod_parametro)):
        mensaje = f'Parámetro {cod_parametro} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    parametro_x_proceso = db.session.get(st_parametro_por_proceso, (empresa, cod_proceso, cod_parametro))
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


@formulas_b.route("/empresas/<empresa>/procesos/<cod_proceso>/parametros/<cod_parametro>/factores", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar los factores de cálculo")
def get_factores_calculo_parametro(empresa, cod_proceso, cod_parametro):
    empresa = validar_number('empresa', empresa, 2)
    cod_proceso = validar_varchar('cod_proceso', cod_proceso, 8)
    cod_parametro = validar_varchar('cod_parametro', cod_parametro, 8)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_proceso, (empresa, cod_proceso)):
        mensaje = f'Proceso {cod_proceso} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_parametro_proceso, (empresa, cod_parametro)):
        mensaje = f'Parámetro {cod_parametro} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_parametro_por_proceso, (empresa, cod_proceso, cod_parametro)):
        mensaje = f'Parámetro por proceso inexistente: proceso ({cod_proceso}), parámetro ({cod_parametro})'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    query = st_factor_calculo_parametro.query()
    factores_calculo = query.filter(st_factor_calculo_parametro.empresa == empresa,
                                    st_factor_calculo_parametro.cod_proceso == cod_proceso,
                                    st_factor_calculo_parametro.cod_parametro == cod_parametro).order_by(
        st_factor_calculo_parametro.orden).all()
    return jsonify(st_factor_calculo_parametro.to_list(factores_calculo))


@formulas_b.route("/empresas/<empresa>/procesos/<cod_proceso>/parametros/<cod_parametro>/factores", methods=["POST"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("registrar el factor de cálculo")
def post_factor_calculo_parametro(empresa, cod_proceso, cod_parametro, data):
    empresa = validar_number('empresa', empresa, 2)
    cod_proceso = validar_varchar('cod_proceso', cod_proceso, 8)
    cod_parametro = validar_varchar('cod_parametro', cod_parametro, 8)
    data = {'empresa': empresa, 'cod_proceso': cod_proceso, 'cod_parametro': cod_parametro, **data}
    st_factor_calculo_parametro(**data)
    if not db.session.get(Empresa, data['empresa']):
        mensaje = f'Empresa {data['empresa']} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_proceso, (data['empresa'], data['cod_proceso'])):
        mensaje = f'Proceso {data['cod_proceso']} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_parametro_proceso, (data['empresa'], data['cod_parametro'])):
        mensaje = f'Parámetro {data['cod_parametro']} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_parametro_por_proceso, (data['empresa'], data['cod_proceso'], data['cod_parametro'])):
        mensaje = f'El parámetro {data['cod_parametro']} no está vinculado al proceso {data['cod_proceso']}'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if db.session.get(st_factor_calculo_parametro,
                      (data['empresa'], data['cod_proceso'], data['cod_parametro'], data['orden'])):
        mensaje = f'El factor de cálculo (proceso: {data['cod_proceso']}, parámetro: {data['cod_parametro']}, orden: {data['orden']}) ya existe'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    ultimo_factor = (db.session.query(st_factor_calculo_parametro)
                     .filter_by(**{'empresa': data['empresa'],
                                   'cod_proceso': data['cod_proceso'],
                                   'cod_parametro': data['cod_parametro']})
                     .order_by(st_factor_calculo_parametro.orden.desc())
                     .first())
    if ultimo_factor:
        if ultimo_factor.tipo_factor != tipo_factor.OPERADOR.value and data[
            'tipo_factor'] != tipo_factor.OPERADOR.value:
            mensaje = 'El siguiente factor de cálculo debe ser un operador'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 409
        if ultimo_factor.tipo_factor == tipo_factor.OPERADOR.value and data[
            'tipo_factor'] == tipo_factor.OPERADOR.value:
            mensaje = 'El siguiente factor de cálculo debe ser un parámetro o un valor fijo'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 409
        nuevo_orden = ultimo_factor.orden + 1
        if data['orden'] != nuevo_orden:
            mensaje = f'El orden del factor de cálculo debe ser {nuevo_orden}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 409
    else:
        if data['tipo_factor'] == tipo_factor.OPERADOR.value:
            mensaje = 'El primer factor de cálculo debe ser un parámetro o un valor fijo'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 409
        if data['orden'] != 1:
            mensaje = 'El primer factor de cálculo debe tener orden 1'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 409
    match data['tipo_factor']:
        case tipo_factor.PARAMETRO.value:
            if not data.get('cod_parametro_tipo'):
                mensaje = 'Falta el código del parámetro para el operador'
                logger.error(mensaje)
                return jsonify({'mensaje': mensaje}), 400
            if not db.session.get(st_parametro_proceso, (data['empresa'], data['cod_parametro_tipo'])):
                mensaje = 'Parámetro inexistente para asignar al operador'
                logger.error(mensaje)
                return jsonify({'mensaje': mensaje}), 404
            data['operador'] = None
            data['valor_fijo'] = None
        case tipo_factor.VALOR_FIJO.value:
            if data.get('valor_fijo') is None or data.get('valor_fijo') == "":
                mensaje = 'Falta el valor fijo'
                logger.error(mensaje)
                return jsonify({'mensaje': mensaje}), 400
            data['operador'] = None
            data['cod_parametro_tipo'] = None
        case tipo_factor.OPERADOR.value:
            if not data.get('operador'):
                mensaje = 'Falta el operador'
                logger.error(mensaje)
                return jsonify({'mensaje': mensaje}), 400
            if data['operador'] not in operador.values():
                mensaje = f'Operador inválido, solo se aceptan: {', '.join(operador.values())}'
                logger.error(mensaje)
                return jsonify({'mensaje': mensaje}), 400
            data['valor_fijo'] = None
            data['cod_parametro_tipo'] = None
        case _:
            mensaje = f'Tipo de operador inválido, solo se aceptan: {', '.join(tipo_factor.values())}'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
    db.session.add(st_factor_calculo_parametro(**data))
    db.session.commit()
    mensaje = f'Se registró el factor de cálculo (proceso: {data['cod_proceso']}, parámetro: {data['cod_parametro']}, orden: {data['orden']})'
    logger.info(mensaje)
    return jsonify({'mensaje': mensaje}), 201


@formulas_b.route("/empresas/<empresa>/procesos/<cod_proceso>/parametros/<cod_parametro>/factores/<orden>",
                  methods=["DELETE"])
@jwt_required()
@cross_origin()
@handle_exceptions("eliminar el factor de cálculo")
def delete_factor_calculo_parametro(empresa, cod_proceso, cod_parametro, orden):
    empresa = validar_number('empresa', empresa, 2)
    cod_proceso = validar_varchar('cod_proceso', cod_proceso, 8)
    cod_parametro = validar_varchar('cod_parametro', cod_parametro, 8)
    orden = validar_number('orden', orden, 3)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_proceso, (empresa, cod_proceso)):
        mensaje = f'Proceso {cod_proceso} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_parametro_proceso, (empresa, cod_parametro)):
        mensaje = f'Parámetro {cod_parametro} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_parametro_por_proceso, (empresa, cod_proceso, cod_parametro)):
        mensaje = f'El parámetro {cod_parametro} no está vinculado al proceso {cod_proceso}'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    factor_calculo = db.session.get(st_factor_calculo_parametro, (empresa, cod_proceso, cod_parametro, orden))
    if not factor_calculo:
        mensaje = f'Factor de cálculo (proceso: {cod_proceso}, parámetro: {cod_parametro}, orden: {orden}) inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    ultimo_factor = (db.session.query(st_factor_calculo_parametro)
                     .filter_by(**{'empresa': empresa,
                                   'cod_proceso': cod_proceso,
                                   'cod_parametro': cod_parametro})
                     .order_by(st_factor_calculo_parametro.orden.desc())
                     .first())
    if ultimo_factor and ultimo_factor.orden != orden:
        mensaje = 'Sólo se puede eliminar el último factor de cálculo'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    db.session.delete(factor_calculo)
    db.session.commit()
    mensaje = f'Se eliminó el factor de cálculo (proceso: {cod_proceso}, parámetro: {cod_parametro}, orden: {orden})'
    logger.info(mensaje)
    return '', 204


@formulas_b.route("/modulos", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar los módulos")
def get_modulos():
    query = tg_sistema.query()
    modulos = query.filter(and_(tg_sistema.ruta.isnot(None))).order_by(
        tg_sistema.sistema).all()
    return jsonify(tg_sistema.to_list(modulos))


@formulas_b.route("/empresas/<empresa>/funciones/<cod_funcion>", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar la función")
def get_funcion(empresa, cod_funcion):
    empresa = validar_number('empresa', empresa, 2)
    cod_funcion = validar_cod('cod_funcion', cod_funcion)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    funcion = db.session.get(st_funcion, (empresa, cod_funcion))
    if not funcion:
        mensaje = f'Función {cod_funcion} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    return jsonify(funcion.to_dict())


@formulas_b.route("/empresas/<empresa>/funciones", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar las funciones")
def get_funciones(empresa):
    empresa = validar_number('empresa', empresa, 2)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    query = st_funcion.query()
    funciones = query.filter(st_funcion.empresa == empresa).order_by(st_funcion.cod_funcion).all()
    return jsonify(st_funcion.to_list(funciones))


@formulas_b.route("/empresas/<empresa>/modulos/<cod_modulo>/funciones", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar las funciones por módulo")
def get_funciones_por_modulo(empresa, cod_modulo):
    empresa = validar_number('empresa', empresa, 2)
    cod_modulo = validar_varchar('cod_modulo', cod_modulo, 3)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(tg_sistema, cod_modulo):
        mensaje = f'Módulo {cod_modulo} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    query = st_funcion.query()
    funciones = query.filter(st_funcion.empresa == empresa, st_funcion.cod_modulo == cod_modulo).order_by(
        st_funcion.cod_funcion).all()
    return jsonify(st_funcion.to_list(funciones))


@formulas_b.route("/empresas/<empresa>/funciones", methods=["POST"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("registrar la función")
def post_funcion(empresa, data):
    empresa = validar_number('empresa', empresa, 2)
    data = {'empresa': empresa, **data}
    funcion = st_funcion(**data)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(tg_sistema, data['cod_modulo']):
        mensaje = f'Módulo {data['cod_modulo']} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if db.session.get(st_funcion, (empresa, data['cod_funcion'])):
        mensaje = f'Ya existe una función con el código {data['cod_funcion']}'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    db.session.add(funcion)
    db.session.commit()
    mensaje = f'Se registró la función {funcion.cod_funcion}'
    logger.info(mensaje)
    return jsonify({'mensaje': mensaje}), 201


@formulas_b.route("/empresas/<empresa>/funciones/<cod_funcion>", methods=["PUT"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("actualizar la función")
def put_funcion(empresa, cod_funcion, data):
    empresa = validar_number('empresa', empresa, 2)
    cod_funcion = validar_varchar('cod_funcion', cod_funcion, 8)
    data = {'empresa': empresa, 'cod_funcion': cod_funcion, **data}
    st_funcion(**data)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    funcion = db.session.get(st_funcion, (empresa, cod_funcion))
    if not funcion:
        mensaje = f'Función {cod_funcion} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    if data.get('cod_modulo'):
        if db.session.get(tg_sistema, data['cod_modulo']):
            funcion.cod_modulo = data['cod_modulo']
        else:
            mensaje = f'Módulo {data['cod_modulo']} inexistente'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 404
    funcion.nombre = data['nombre']
    funcion.nombre_base_datos = data['nombre_base_datos']
    if data.get('estado') is not None:
        funcion.estado = data['estado']
    funcion.observaciones = data.get('observaciones')
    funcion.tipo_retorno = data['tipo_retorno']
    funcion.audit_usuario_mod = text('user')
    funcion.audit_fecha_mod = text('sysdate')
    db.session.commit()
    mensaje = f'Se actualizó la función {data['cod_funcion']}'
    logger.info(mensaje)
    return '', 204


@formulas_b.route("/empresas/<empresa>/funciones/<cod_funcion>",
                  methods=["DELETE"])
@jwt_required()
@cross_origin()
@handle_exceptions("eliminar la función")
def delete_funcion(empresa, cod_funcion):
    empresa = validar_number('empresa', empresa, 2)
    cod_funcion = validar_cod('cod_funcion', cod_funcion)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    funcion = db.session.get(st_funcion, (empresa, cod_funcion))
    if not funcion:
        mensaje = f'Función {cod_funcion} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if db.session.query(st_parametro_funcion).filter(st_parametro_funcion.cod_funcion == cod_funcion).first():
        mensaje = 'Existen parámetros vinculados a la función'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    db.session.delete(funcion)
    db.session.commit()
    mensaje = f'Se eliminó la función {cod_funcion}'
    logger.info(mensaje)
    return '', 204


@formulas_b.route("/empresas/<empresa>/funciones/<cod_funcion>/parametros/<secuencia>", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar el parámetro de la función")
def get_parametro_funcion(empresa, cod_funcion, secuencia):
    empresa = validar_number('empresa', empresa, 2)
    cod_funcion = validar_cod('cod_funcion', cod_funcion)
    secuencia = validar_number('secuencia', secuencia, 3)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_funcion, (empresa, cod_funcion)):
        mensaje = f'Función {cod_funcion} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    parametro = db.session.get(st_parametro_funcion, (empresa, cod_funcion, secuencia))
    if not parametro:
        mensaje = f'Parámetro {secuencia} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    return jsonify(parametro.to_dict())


@formulas_b.route("/empresas/<empresa>/funciones/<cod_funcion>/parametros", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar los parametros de la función")
def get_parametros_funcion(empresa, cod_funcion):
    empresa = validar_number('empresa', empresa, 2)
    cod_funcion = validar_cod('cod_funcion', cod_funcion)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_funcion, (empresa, cod_funcion)):
        mensaje = f'Función {cod_funcion} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    query = st_parametro_funcion.query()
    parametros = query.filter(st_parametro_funcion.empresa == empresa,
                              st_parametro_funcion.cod_funcion == cod_funcion).order_by(
        st_parametro_funcion.secuencia).all()
    return jsonify(st_parametro_funcion.to_list(parametros))


@formulas_b.route("/empresas/<empresa>/funciones/<cod_funcion>/parametros", methods=["POST"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("registrar el parámetro de la función")
def post_parametro_funcion(empresa, cod_funcion, data):
    empresa = validar_number('empresa', empresa, 2)
    cod_funcion = validar_cod('cod_funcion', cod_funcion)
    data = {'empresa': empresa, 'cod_funcion': cod_funcion, **data}
    st_parametro_funcion(**data)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_funcion, (empresa, cod_funcion)):
        mensaje = f'Función {cod_funcion} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if db.session.get(st_parametro_funcion, (empresa, cod_funcion, data['secuencia'])):
        mensaje = f'Ya existe un parámetro con la secuencia {data['secuencia']}'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    match (data['tipo_parametro']):
        case tipo_parametro.VARIABLE.value:
            if not data.get('variable'):
                mensaje = 'Falta el nombre de la variable'
                logger.error(mensaje)
                return jsonify({'mensaje': mensaje}), 400
            data['fijo_caracter'] = None
            data['fijo_numero'] = None
        case tipo_parametro.CARACTER.value:
            if not data.get('fijo_caracter'):
                mensaje = 'Falta el valor fijo del caracter'
                logger.error(mensaje)
                return jsonify({'mensaje': mensaje}), 400
            data['variable'] = None
            data['fijo_numero'] = None
        case tipo_parametro.NUMERO.value:
            if data.get('fijo_numero') is None:
                mensaje = 'Falta el valor fijo del número'
                logger.error(mensaje)
                return jsonify({'mensaje': mensaje}), 400
            data['variable'] = None
            data['fijo_caracter'] = None
    ultimo_parametro = (db.session.query(st_parametro_funcion)
                        .filter_by(**{'empresa': empresa, 'cod_funcion': cod_funcion})
                        .order_by(st_parametro_funcion.secuencia.desc())
                        .first())
    secuencia_actual = 1
    if ultimo_parametro:
        secuencia_actual = ultimo_parametro.secuencia + 1
    if data['secuencia'] != secuencia_actual:
        mensaje = f'El parámetro debe tener secuencia {secuencia_actual}'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    parametro = st_parametro_funcion(**data)
    db.session.add(parametro)
    db.session.commit()
    mensaje = f'Se registró el parámetro {data['secuencia']}'
    logger.info(mensaje)
    return jsonify({'mensaje': mensaje}), 201


@formulas_b.route("/empresas/<empresa>/funciones/<cod_funcion>/parametros/<secuencia>", methods=["PUT"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("actualizar el parámetro de la función")
def put_parametro_funcion(empresa, cod_funcion, secuencia, data):
    empresa = validar_number('empresa', empresa, 2)
    cod_funcion = validar_varchar('cod_funcion', cod_funcion, 8)
    secuencia = validar_number('secuencia', secuencia, 10)
    data = {'empresa': empresa, 'cod_funcion': cod_funcion, 'secuencia': secuencia, **data}
    st_parametro_funcion(**data)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_funcion, (empresa, cod_funcion)):
        mensaje = f'Función {cod_funcion} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    parametro = db.session.get(st_parametro_funcion, (empresa, cod_funcion, secuencia))
    if not parametro:
        mensaje = f'Parámetro {secuencia} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    parametro.tipo_parametro = data['tipo_parametro']
    match (data['tipo_parametro']):
        case tipo_parametro.VARIABLE.value:
            if not data.get('variable'):
                mensaje = 'Falta el nombre de la variable'
                logger.error(mensaje)
                return jsonify({'mensaje': mensaje}), 400
            parametro.VARIABLE = data.get('variable')
            parametro.fijo_caracter = None
            parametro.fijo_numero = None
        case tipo_parametro.CARACTER.value:
            if not data.get('fijo_caracter'):
                mensaje = 'Falta el valor fijo del caracter'
                logger.error(mensaje)
                return jsonify({'mensaje': mensaje}), 400
            parametro.fijo_caracter = data.get('fijo_caracter')
            parametro.VARIABLE = None
            parametro.fijo_numero = None
        case tipo_parametro.NUMERO.value:
            if data.get('fijo_numero') is None or data.get('fijo_numero') == "":
                mensaje = 'Falta el valor fijo del número'
                logger.error(mensaje)
                return jsonify({'mensaje': mensaje}), 400
            parametro.fijo_numero = data.get('fijo_numero')
            parametro.VARIABLE = None
            parametro.fijo_caracter = None
    parametro.audit_usuario_mod = text('user')
    parametro.audit_fecha_mod = text('sysdate')
    db.session.commit()
    mensaje = f'Se actualizó el parámetro {secuencia}'
    logger.info(mensaje)
    return '', 204


@formulas_b.route("/empresas/<empresa>/funciones/<cod_funcion>/parametros/<secuencia>",
                  methods=["DELETE"])
@jwt_required()
@cross_origin()
@handle_exceptions("eliminar el parámetro de la función")
def delete_parametro_funcion(empresa, cod_funcion, secuencia):
    empresa = validar_number('empresa', empresa, 2)
    cod_funcion = validar_cod('cod_funcion', cod_funcion)
    secuencia = validar_number('secuencia', secuencia, 3)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(st_funcion, (empresa, cod_funcion)):
        mensaje = f'Función {cod_funcion} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    parametro = db.session.get(st_parametro_funcion, (empresa, cod_funcion, secuencia))
    if not parametro:
        mensaje = f'El parámetro {secuencia} no existe'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    ultimo_parametro = (db.session.query(st_parametro_funcion)
                        .filter_by(**{'empresa': empresa, 'cod_funcion': cod_funcion})
                        .order_by(st_parametro_funcion.secuencia.desc())
                        .first())
    if ultimo_parametro and ultimo_parametro.secuencia != secuencia:
        mensaje = 'Sólo se puede eliminar el último parámetro de la función'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 409
    db.session.delete(parametro)
    db.session.commit()
    mensaje = f'Se eliminó el parámetro {secuencia} de la función'
    logger.info(mensaje)
    return '', 204


@formulas_b.route("/empresas/<empresa>/funciones-bd/<cod_funcion>", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("probar función")
def execute_funcion_bd(empresa, cod_funcion):
    empresa = validar_number('empresa', empresa, 2)
    cod_funcion = validar_cod('cod_funcion', cod_funcion)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    sql = f"SELECT PK_FORMULAS.EJECUTAR_FUNCION({empresa}, '', '', '{cod_funcion}') FROM DUAL"
    result = custom_base.execute_sql(sql)
    return jsonify({"mensaje": result})


@formulas_b.route("/empresas/<empresa>/formulas-bd/<cod_formula>", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("probar fórmula")
def execute_formula_bd(empresa, cod_formula):
    empresa = validar_number('empresa', empresa, 2)
    cod_formula = validar_cod('cod_formula', cod_formula)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    sql = f"SELECT PK_FORMULAS.EJECUTAR_FORMULA({empresa}, '', '', '{cod_formula}') FROM DUAL"
    result = custom_base.execute_sql(sql)
    return jsonify({"mensaje": result})


@formulas_b.route("/empresas/<empresa>/procesos/<cod_proceso>/parametros/<cod_parametro>/factores-bd", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("probar factores de cálculo")
def execute_factores_bd(empresa, cod_proceso, cod_parametro):
    empresa = validar_number('empresa', empresa, 2)
    cod_proceso = validar_cod('cod_proceso', cod_proceso)
    cod_parametro = validar_cod('cod_parametro', cod_parametro)
    if not db.session.get(Empresa, empresa):
        mensaje = f'Empresa {empresa} inexistente'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    sql = f"SELECT PK_FORMULAS.EJECUTAR_FACTORES({empresa}, '{cod_proceso}', '{cod_parametro}') FROM DUAL"
    result = custom_base.execute_sql(sql)
    return jsonify({"mensaje": result})
