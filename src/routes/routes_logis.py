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
    pv_cod_pedido = data.get('pv_cod_pedido')
    pv_comprobante_manual = data.get('pv_comprobante_manual')
    pv_cod_persona_ven = data.get('pv_cod_persona_ven')
    pv_nombre_persona_ven = data.get('pv_nombre_persona_ven')
    pv_cod_persona_cli = data.get('pv_cod_persona_cli')
    pv_nombre_persona_cli = data.get('pv_nombre_persona_cli')
    pv_estado = data.get('pv_estado')
    pn_cod_agencia = data.get('pn_cod_agencia')
    pn_empresa = data.get('pn_empresa')
    pv_cod_tipo_pedido = data.get('pv_cod_tipo_pedido')
    pn_cod_bodega_despacho = data.get('pn_cod_bodega_despacho')
    p_orden = data.get('p_orden', 'COD_PEDIDO')
    p_tipo_orden = data.get('p_tipo_orden', 'DESC')
    pv_bodega_envia = data.get('pv_bodega_envia')
    pv_direccion = data.get('pv_direccion')
    pv_cod_orden = data.get('pv_cod_orden')
    print(pd_fecha_inicial)
    print(pd_fecha_final)

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

        if cursor_output:
            columns = [col[0] for col in cursor_output.description]
            for row in cursor_output:
                result.append(dict(zip(columns, row)))

        return jsonify(result)
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        return jsonify({"error": error.message}), 500
    finally:
        cursor.close()


