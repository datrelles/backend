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
# --- Utilidades de parseo ----------------------------------------------------

DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y")

def parse_date(s: str):
    if not s:
        return None
    s = s.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    # Si no coincide ningún formato, levanta error controlado
    raise ValueError(f"Formato de fecha inválido: '{s}'. Usa YYYY-MM-DD o DD/MM/YYYY.")

def parse_int(s: str):
    if s is None or s == "":
        return None
    try:
        return int(s)
    except ValueError:
        raise ValueError(f"Valor entero inválido: '{s}'")

def parse_str(s: str):
    if s is None:
        return None
    s = s.strip()
    return s if s != "" else None

def parse_order(field: str, default_field="COD_PEDIDO"):
    # Permite solo un conjunto mínimo “seguro” de columnas para ordenar (ajusta a tus columnas reales)
    allowed = {
        "COD_PEDIDO", "FECHA_PEDIDO", "COD_PERSONA_CLI", "COD_PERSONA_VEN",
        "ESTADO", "COD_AGENCIA", "EMPRESA"
    }
    f = (field or default_field).upper().strip()
    return f if f in allowed else default_field

def parse_order_dir(val: str, default_dir="DESC"):
    v = (val or default_dir).upper().strip()
    return "ASC" if v == "ASC" else "DESC"




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

@bplog.route('/pedidos_get', methods=['GET'])
@jwt_required()
@cross_origin()
def get_pedidos_get():
    """
    GET /pedidos?pd_fecha_inicial=2025-08-01&pd_fecha_final=2025-08-21&pedido=12345&pn_empresa=20&pn_cod_agencia=3
    Parámetros aceptados (todos opcionales salvo los que tu SP requiera):
      - pd_fecha_inicial, pd_fecha_final  (YYYY-MM-DD o DD/MM/YYYY)
      - pedido                           -> pv_cod_pedido
      - pv_comprobante_manual
      - pv_cod_persona_ven
      - pv_nombre_persona_ven
      - pv_cod_persona_cli
      - cliente                          -> pv_nombre_persona_cli
      - pv_estado
      - pn_cod_agencia                   (int)
      - pn_empresa                       (int)
      - pv_cod_tipo_pedido
      - pn_cod_bodega_despacho           (int)
      - p_orden                          (validado contra lista segura)
      - p_tipo_orden                     (ASC|DESC)
      - bodega_consignacion              -> pv_bodega_envia
      - direccion                        -> pv_direccion
      - orden                            -> pv_cod_orden
    """
    args = request.args

    try:
        pd_fecha_inicial = parse_date(args.get('pd_fecha_inicial'))
        pd_fecha_final   = parse_date(args.get('pd_fecha_final'))

        pv_cod_pedido            = parse_str(args.get('pedido'))
        pv_comprobante_manual    = parse_str(args.get('pv_comprobante_manual'))
        pv_cod_persona_ven       = parse_str(args.get('pv_cod_persona_ven'))
        pv_nombre_persona_ven    = parse_str(args.get('pv_nombre_persona_ven'))
        pv_cod_persona_cli       = parse_str(args.get('pv_cod_persona_cli'))
        pv_nombre_persona_cli    = parse_str(args.get('cliente'))  # alias que ya usabas
        pv_estado                = parse_str(args.get('pv_estado'))

        pn_cod_agencia           = parse_int(args.get('pn_cod_agencia'))
        pn_empresa               = parse_int(args.get('pn_empresa'))

        pv_cod_tipo_pedido       = parse_str(args.get('pv_cod_tipo_pedido'))
        pn_cod_bodega_despacho   = parse_int(args.get('pn_cod_bodega_despacho'))

        p_orden                  = parse_order(args.get('p_orden'), default_field="COD_PEDIDO")
        p_tipo_orden             = parse_order_dir(args.get('p_tipo_orden'), default_dir="DESC")

        pv_bodega_envia          = parse_str(args.get('bodega_consignacion'))
        pv_direccion             = parse_str(args.get('direccion'))
        pv_cod_orden             = parse_str(args.get('orden'))

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

    db1 = None
    cursor = None
    try:
        # Conexión Oracle
        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = db1.cursor()

        # Cursor de salida del paquete/procedimiento
        result_rc_listado_pedidos = cursor.var(cx_Oracle.CURSOR)

        # Llamada al procedimiento tal como lo tenías, con mismos parámetros/orden
        cursor.callproc(
            'jaher.PK_RC_LISTADO_PEDIDOSMA.slct_rc_listado_pedidos_bod',
            [
                result_rc_listado_pedidos,
                pd_fecha_inicial,
                pd_fecha_final,
                pv_cod_pedido,
                pv_comprobante_manual,
                pv_cod_persona_ven,
                pv_nombre_persona_ven,
                pv_cod_persona_cli,
                pv_nombre_persona_cli,
                pv_estado,
                pn_cod_agencia,
                pn_empresa,
                pv_cod_tipo_pedido,
                pn_cod_bodega_despacho,
                p_orden,
                p_tipo_orden,
                pv_bodega_envia,
                pv_direccion,
                pv_cod_orden
            ]
        )

        # Procesar el cursor de salida
        result = []
        cursor_output = result_rc_listado_pedidos.getvalue()
        columns = [col[0] for col in cursor_output.description]

        for row in cursor_output:
            row_dict = dict(zip(columns, row))
            # Formato de FECHA_PEDIDO (si existe)
            if row_dict.get('FECHA_PEDIDO'):
                row_dict['FECHA_PEDIDO'] = datetime.strftime(row_dict['FECHA_PEDIDO'], "%d/%m/%Y")
            result.append(row_dict)

        return jsonify(result)

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        return jsonify({"error": error.message}), 500

    finally:
        try:
            if cursor: cursor.close()
        finally:
            if db1: db1.close()

