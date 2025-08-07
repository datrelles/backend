from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
import logging

from sqlalchemy import text

from src.decorators import validate_json, handle_exceptions
from src.config.database import db
from src.models.modulo_formulas import validar_empresa
from src.models.users import Empresa
from src.validations import validar_number, validar_varchar

activaciones_b = Blueprint('routes_activaciones', __name__)
logger = logging.getLogger(__name__)

COD_MODELO_CATAL_ACTIV = "ACT"


@activaciones_b.route("/promotores", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar los promotores")
def get_proceso():
    sql = text("""
                SELECT
                    e.identificacion,
                    e.apellido_paterno,
                    e.apellido_materno,
                    e.nombres
                FROM
                    rh_empleados e
                WHERE
                    e.activo = 'S'
                ORDER BY e.apellido_paterno, e.apellido_materno, e.nombres
                """)
    rows = db.session.execute(sql).fetchall()
    result = [{"identificacion": row[0], "apellido_paterno": row[1], "apellido_materno": row[2], "nombres": row[3]} for
              row in rows]
    return jsonify(result)


@activaciones_b.route("/empresas/<empresa>/clientes", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar los clientes")
def get_clientes(empresa):
    if not db.session.get(Empresa, empresa):
        mensaje = 'Empresa {} inexistente'.format(empresa)
        logger.error(mensaje)
        return jsonify({'mensaje': mensaje}), 404
    empresa = validar_empresa('empresa', empresa)
    sql = text("""
                SELECT
                    ch.cod_clienteh,
                    ch.cod_tipo_clienteh,
                    SUBSTR(c.nombre, 1) AS nombre
                FROM
                    cliente_hor ch
                INNER JOIN
                    cliente c
                ON
                    ch.empresah = c.empresa AND
                    ch.cod_clienteh=c.cod_cliente
                WHERE
                    ch.empresah = :empresa
                """)
    rows = db.session.execute(sql, {"empresa": empresa}).fetchall()
    result = [{"cod_clienteh": row[0], "cod_tipo_clienteh": row[1], "nombre": row[2]} for row in rows]
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


@activaciones_b.route("/promotores/<cod_promotor>/clientes", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar los clientes del promotor")
def get_clientes_por_promotor(cod_promotor):
    cod_promotor = validar_varchar('cod_promotor', cod_promotor, 20)
    sql = text("""
                SELECT
                    DISTINCT(p.cod_cliente) AS cod_cliente,
                    c.nombre
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
                    c.nombre
                """)
    rows = db.session.execute(sql, {"cod_promotor": cod_promotor}).fetchall()
    result = [{"cod_cliente": row[0], "nombre": row[1]} for row in rows]
    return jsonify(result)


@activaciones_b.route("/promotores/<cod_promotor>/clientes/<cod_cliente>/direcciones", methods=["GET"])
@jwt_required()
@cross_origin()
@handle_exceptions("consultar las tiendas del promotor por cliente")
def get_direcciones_por_promotor_cliente(cod_promotor, cod_cliente):
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
    result = [{"cod_cliente": row[0], "nombre": row[1]} for row in rows]
    return jsonify(result)
