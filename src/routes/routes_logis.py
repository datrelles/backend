from flask import Blueprint, jsonify, request
import logging
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
import datetime
import re
from decimal import Decimal
from datetime import datetime, date
from src import oracle
from os import getenv
import cx_Oracle
from src.config.database import db, engine, session

bplog = Blueprint('routes_log', __name__)

logger = logging.getLogger(__name__)

from flask import request, jsonify
import cx_Oracle

def parse_date(date_string):
    if date_string:
        return datetime.strptime(date_string, '%d/%m/%Y').date()
    return None
@bplog.route('/pedidos', methods=['POST'])
@jwt_required()
@cross_origin()
def get_pedidos():
    data = request.json
    pd_fecha_inicial = parse_date(data.get('pd_fecha_inicial'))
    pd_fecha_final = parse_date(data.get('pd_fecha_final'))
    pv_cod_pedido = data.get('pedido')
    pv_comprobante_manual = data.get('pv_comprobante_manual')
    pv_cod_persona_ven = data.get('pv_cod_persona_ven')
    pv_nombre_persona_ven = data.get('pv_nombre_persona_ven')
    pv_cod_persona_cli = data.get('pv_cod_persona_cli')
    pv_nombre_persona_cli = data.get('cliente')
    pv_estado = data.get('pv_estado')
    pn_cod_agencia = data.get('pn_cod_agencia')
    pn_empresa = data.get('pn_empresa')
    pv_cod_tipo_pedido = data.get('pv_cod_tipo_pedido')
    pn_cod_bodega_despacho = data.get('pn_cod_bodega_despacho')
    p_orden = data.get('p_orden', 'COD_PEDIDO')
    p_tipo_orden = data.get('p_tipo_orden', 'DESC')
    pv_bodega_envia = data.get('bodega_consignacion')
    pv_direccion = data.get('direccion')
    pv_cod_orden = data.get('orden')

    try:
        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = db1.cursor()
        result_rc_listado_pedidos = cursor.var(cx_Oracle.CURSOR)

        cursor.callproc('jaher.PK_RC_LISTADO_PEDIDOSMA.slct_rc_listado_pedidos_bod', [
            result_rc_listado_pedidos, pd_fecha_inicial, pd_fecha_final, pv_cod_pedido,
            pv_comprobante_manual, pv_cod_persona_ven, pv_nombre_persona_ven,
            pv_cod_persona_cli, pv_nombre_persona_cli, pv_estado, pn_cod_agencia,
            pn_empresa, pv_cod_tipo_pedido, pn_cod_bodega_despacho, p_orden,
            p_tipo_orden, pv_bodega_envia, pv_direccion, pv_cod_orden
        ])
        result = []
        cursor_output = result_rc_listado_pedidos.getvalue()
        columns = [col[0] for col in cursor_output.description]
        for row in cursor_output:
            row_dict = dict(zip(columns, row))
            if 'FECHA_PEDIDO' in row_dict and row_dict['FECHA_PEDIDO']:
                row_dict['FECHA_PEDIDO'] = datetime.strftime(row_dict['FECHA_PEDIDO'],"%d/%m/%Y") if row_dict['FECHA_PEDIDO'] else ""
            result.append(row_dict)
        return jsonify(result)
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        return jsonify({"error": error.message}), 500
    finally:
        cursor.close()


@bplog.route('/listado_pedido', methods=['POST'])
@jwt_required()
@cross_origin()
def get_listado_pedido():
    data = request.json
    pn_empresa = data.get('pn_empresa')
    pv_cod_tipo_pedido = data.get('pv_cod_tipo_pedido')
    pv_cod_pedido = data.get('pedido')
    pn_cod_agencia = data.get('pn_cod_agencia')
    pv_bodega_envia = data.get('bodega_consignacion')
    pv_cod_direccion = data.get('cod_direccion')
    p_tipo_orden = data.get('p_tipo_orden', 'DESC')
    pv_cod_orden = data.get('orden')
    try:
        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = db1.cursor()

        p_cod_comprobante = cursor.var(cx_Oracle.STRING)
        p_cod_comprobante.setvalue(0, pv_cod_orden)
        p_cod_tipo_orden = cursor.var(cx_Oracle.STRING)
        p_cod_tipo_orden.setvalue(0, p_tipo_orden)

        cursor.callproc('ksa_comprobante.GENERA_DE_PEDIDO', [pn_empresa, pv_cod_tipo_pedido, pv_cod_pedido,
            pn_cod_agencia, pv_bodega_envia, pv_cod_direccion,
            p_cod_comprobante, p_cod_tipo_orden])

        cod_comprobante = p_cod_comprobante.getvalue()
        cod_tipo_comprobante = p_cod_tipo_orden.getvalue()

        cursor.close
        cursor = db1.cursor()
        sql = """
                        select * from vta_movimiento_trans c 
                        where c.cod_comprobante = :cod_comprobante 
                        and c.tipo_comprobante = :cod_tipo_comprobante
                        """
        cursor = cursor.execute(sql, [cod_comprobante, cod_tipo_comprobante])
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        data = [dict(zip(columns, row)) for row in results]
        cursor.close()
        db1.close()

        return jsonify(data)
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        return jsonify({"error": error.message}), 500

@bplog.route('/presupuesto', methods=['POST'])
@jwt_required()
@cross_origin()
def get_presupuesto():
    data = request.json
    try:
        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = db1.cursor()
        sql = """
                        SELECT v.*, s.valor 
                        FROM vt_presupuesto_sellout v 
                        LEFT JOIN st_presupuesto_valor s 
                        ON v.empresa = s.empresa and v.cod_producto_modelo = s.cod_producto_modelo 
                        and v.cod_persona = s.cod_cliente and v.anio = s.aaaa and v.mes = s.mm 
                        """
        cursor = cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        data = [dict(zip(columns, row)) for row in results]
        cursor.close()
        db1.close()

        return jsonify(data)
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        return jsonify({"error": error.message}), 500

@bplog.route('/update_value', methods=['POST'])
@jwt_required()
@cross_origin()
def update_value():
    data = request.json
    empresa = data.get('empresa')
    cod_persona = data.get('pv_cod_tipo_pedido')
    cod_producto_modelo = data.get('pedido')
    mes = data.get('pn_cod_agencia')
    anio = data.get('bodega_consignacion')

    try:
        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = db1.cursor()
        sql = """
                        SELECT v.*, s.valor 
                        FROM vt_presupuesto_sellout v 
                        LEFT JOIN st_presupuesto_valor s 
                        ON v.empresa = s.empresa and v.cod_producto_modelo = s.cod_producto_modelo 
                        and v.cod_persona = s.cod_cliente and v.anio = s.aaaa and v.mes = s.mm 
                        """
        cursor = cursor.execute(sql, [empresa, cod_persona, cod_producto_modelo, mes, anio])
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        data = [dict(zip(columns, row)) for row in results]
        cursor.close()
        db1.close()

        return jsonify(data)
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        return jsonify({"error": error.message}), 500