from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
import logging

from sqlalchemy import text

from src.decorators import validate_json, handle_exceptions
from src.config.database import db
from src.exceptions import validation_error
from src.models.clientes import cliente_hor
from src.models.modulo_activaciones import st_activacion
from src.models.modulo_formulas import validar_empresa
from src.models.proveedores import TgModeloItem, Proveedor
from src.models.users import Empresa
from src.validations import validar_number, validar_varchar, validar_fecha
from src.validations.alfanumericas import validar_hora

activaciones_b = Blueprint('routes_activaciones', __name__)
logger = logging.getLogger(__name__)

COD_MODELO_CATAL_ACTIV = "ACT"


def calcular_diferencia_horas_en_minutos(inicio, fin):
    inicio = validar_hora('hora_inicio', inicio, devuelve_string=False)
    fin = validar_hora('hora_fin', fin, devuelve_string=False)
    if inicio >= fin:
        raise validation_error(mensaje='La hora de inicio debe ser menor a la hora de fin')
    return (fin - inicio).total_seconds() / 60


@activaciones_b.route("/promotores", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar los promotores")
def get_promotores():
    sql = text("""
                SELECT
                    e.identificacion,
                    e.apellido_paterno,
                    e.apellido_materno,
                    e.nombres
                FROM
                    rh_empleados e
                WHERE
                    e.activo = 'S' AND
                    EXISTS (
                        SELECT 1
                        FROM st_promotor_tienda p
                        WHERE p.cod_promotor = e.identificacion
                    )
                ORDER BY e.apellido_paterno, e.apellido_materno, e.nombres
                """)
    rows = db.session.execute(sql).fetchall()
    result = [{"identificacion": row[0], "apellido_paterno": row[1], "apellido_materno": row[2], "nombres": row[3]} for
              row in rows]
    return jsonify(result)


@activaciones_b.route("/promotores/<cod_promotor>/clientes", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar los clientes del promotor")
def get_clientes_por_promotor(cod_promotor):
    cod_promotor = validar_varchar('cod_promotor', cod_promotor, 20)
    sql = text("""
                SELECT
                    DISTINCT(p.cod_cliente) AS cod_cliente,
                    ch.cod_tipo_clienteh,
                    SUBSTR(c.nombre, 1) AS nombre
                FROM
                    ST_PROMOTOR_TIENDA p
                INNER JOIN
                    CLIENTE_HOR ch
                    ON
                    ch.empresah = p.empresa AND
                    ch.cod_clienteh = p.cod_cliente
                INNER JOIN
                    CLIENTE c
                    ON
                    c.empresa = ch.empresah AND
                    c.cod_cliente = ch.cod_clienteh
                WHERE
                    p.cod_promotor = :cod_promotor
                ORDER BY
                    nombre
                """)
    rows = db.session.execute(sql, {"cod_promotor": cod_promotor}).fetchall()
    result = [{"cod_cliente": row[0], "cod_tipo_clienteh": row[1], "nombre": row[2]} for row in rows]
    return jsonify(result)


@activaciones_b.route("/promotores/<cod_promotor>/clientes/<cod_cliente>/direcciones", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar las tiendas del promotor por cliente")
def get_direcciones_por_promotor_y_cliente(cod_promotor, cod_cliente):
    cod_promotor = validar_varchar('cod_promotor', cod_promotor, 20)
    cod_cliente = validar_varchar('cod_cliente', cod_cliente, 14)
    sql = text("""
                SELECT
                   g.cod_direccion,
                   SUBSTR(g.ciudad, 1) AS ciudad,
                   SUBSTR(CASE
                     WHEN b.nombre IS NULL THEN
                       CASE
                         WHEN g.nombre IS NOT NULL THEN g.nombre
                         ELSE 'SIN NOMBRE'
                       END
                     ELSE b.nombre
                   END, 1) AS nombre,
                   SUBSTR(g.direccion, 1) AS direccion
                FROM
                   ST_PROMOTOR_TIENDA p
                INNER JOIN
                   ST_CLIENTE_DIRECCION_GUIAS g
                   ON
                   g.empresa = p.empresa AND
                   g.cod_cliente = p.cod_cliente AND
                   g.cod_direccion = p.cod_direccion_guia
                LEFT JOIN
                   ST_BODEGA_CONSIGNACION b
                   ON
                   b.empresa = g.empresa AND
                   b.ruc_cliente = g.cod_cliente AND
                   b.cod_direccion = g.cod_direccion
                WHERE
                  g.es_activo = 1 AND
                  p.cod_promotor = :cod_promotor AND
                  p.cod_cliente = :cod_cliente
                """)
    rows = db.session.execute(sql, {"cod_promotor": cod_promotor, "cod_cliente": cod_cliente}).fetchall()
    result = [{"cod_direccion": row[0], "ciudad": row[1], "nombre": row[2], "direccion": row[3]} for row in rows]
    return jsonify(result)


@activaciones_b.route("/empresas/<empresa>/proveedores", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar los proveedores")
def get_proveedores(empresa):
    empresa = validar_empresa('empresa', empresa)
    if not db.session.get(Empresa, empresa):
        mensaje = 'Empresa {} inexistente'.format(empresa)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    sql = text("""
                SELECT
                    p.cod_proveedor,
                    REPLACE(TRIM(p.nombre), CHR(9), '') AS nombre
                FROM
                    proveedor p
                WHERE
                    p.empresa = :empresa
                ORDER BY p.nombre
                """)
    rows = db.session.execute(sql, {"empresa": empresa}).fetchall()
    result = [{"cod_proveedor": row[0], "nombre": row[1]} for row in rows]
    return jsonify(result)


@activaciones_b.route("/empresas/<empresa>/tipos-activacion", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar los tipos de activación")
def get_tipos_activacion(empresa):
    empresa = validar_empresa('empresa', empresa)
    if not db.session.get(Empresa, empresa):
        mensaje = 'Empresa {} inexistente'.format(empresa)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    sql = text("""
                SELECT
                    m.cod_modelo,
                    m.cod_item,
                    m.nombre
                FROM
                    tg_modelo_item m
                WHERE
                    m.empresa = :empresa AND
                    m.cod_modelo = :cod_modelo
                ORDER BY m.nombre
                """)
    rows = db.session.execute(sql, {"empresa": empresa, "cod_modelo": COD_MODELO_CATAL_ACTIV}).fetchall()
    result = [{"cod_modelo": row[0], "cod_item": row[1], "nombre": row[2]} for row in rows]
    return jsonify(result)


@activaciones_b.route("/empresas/<empresa>/promotores/<cod_promotor>/activaciones", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar las activaciones del promotor")
def get_activaciones_por_promotor(empresa, cod_promotor):
    empresa = validar_number('empresa', empresa, 2)
    cod_promotor = validar_varchar('cod_promotor', cod_promotor, 20)
    fecha_inicio = request.args.get("fecha_inicio")
    fecha_inicio = validar_fecha('fecha_inicio', fecha_inicio) if fecha_inicio else None
    fecha_fin = request.args.get("fecha_fin")
    fecha_fin = validar_fecha('fecha_fin', fecha_fin) if fecha_fin else None
    cod_cliente = validar_varchar('cod_cliente', request.args.get("cod_cliente"), 14, False)
    if not db.session.get(Empresa, empresa):
        mensaje = 'Empresa {} inexistente'.format(empresa)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if cod_cliente and not db.session.get(cliente_hor, (empresa, cod_cliente)):
        mensaje = 'Cliente {} inexistente'.format(cod_cliente)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if (fecha_inicio and not fecha_fin) or (not fecha_inicio and fecha_fin):
        mensaje = 'Debes proveer las fechas de inicio y fin para filtrar por ese parámetro'
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 400
    query = st_activacion.query()
    activaciones = query.filter(st_activacion.empresa == empresa, st_activacion.cod_promotor == cod_promotor)
    if fecha_inicio and fecha_fin:
        if fecha_inicio >= fecha_fin:
            mensaje = 'La fecha de inicio debe ser menor a la de fin'
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400
        activaciones = activaciones.filter(st_activacion.fecha_act.between(fecha_inicio, fecha_fin))
    if cod_cliente:
        activaciones = activaciones.filter(st_activacion.cod_cliente == cod_cliente)
    activaciones = activaciones.all()
    return jsonify(st_activacion.to_list(activaciones, ["promotor", "cliente", "tienda", "proveedor"]))


@activaciones_b.route("/empresas/<empresa>/activaciones", methods=["POST"])
@jwt_required()
@cross_origin()
@validate_json()
@handle_exceptions("registrar la activación")
def post_activacion(empresa, data):
    empresa = validar_number('empresa', empresa, 2)
    data = {'empresa': empresa, **data}
    activacion = st_activacion(**data)
    if not db.session.get(Empresa, data['empresa']):
        mensaje = 'Empresa {} inexistente'.format(data['empresa'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(Proveedor, (data['empresa'], data['cod_proveedor'])):
        mensaje = 'Proveedor {} inexistente'.format(data['cod_proveedor'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    if not db.session.get(TgModeloItem, (data['empresa'], data['cod_modelo_act'], data['cod_item_act'])):
        mensaje = 'Tipo de activación {} inexistente'.format(data['cod_item_act'])
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    activacion.total_minutos = calcular_diferencia_horas_en_minutos(activacion.hora_inicio, activacion.hora_fin)
    db.session.add(activacion)
    db.session.commit()
    mensaje = 'Se registró la activación {}'.format(activacion.cod_activacion)
    logger.info(mensaje)
    return jsonify({'mensaje': mensaje}), 201
