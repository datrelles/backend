from flask import Blueprint, jsonify, request,  url_for
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
from src.models.asignacion_cupo import QueryParamsSchema, STReservaProducto, ALLOWED_ORDERING, reservas_schema, \
    CreateReservaSchema, UpdateReservaSchema, ReservaSchema, map_integrity_error, validate_no_active_duplicate, \
    validate_available_stock_before_create, validate_available_stock_before_update, ajustar_cantidad_reserva
from marshmallow import ValidationError
from urllib.parse import urlencode, urlparse, parse_qsl, urlunparse
from sqlalchemy.exc import IntegrityError



bplog = Blueprint('routes_log', __name__)

logger = logging.getLogger(__name__)

from flask import request, jsonify
import cx_Oracle
from typing import Dict


class AgenteNoEncontrado(Exception):
    pass

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

class AgenteNoEncontrado(Exception):
    pass

class ProductoSerieNoExiste(Exception):
    pass

def cambia_estado_y_graba(
    db1,
    *,
    empresa: int,
    cod_producto: str,
    cod_serie: str,
    estado_nuevo: str,
    numero_agencia: int,
    empresa_g: int = None
) -> Dict:
    if empresa_g is None:
        empresa_g = empresa

    def _consulta_producto_serie(db1, *, empresa, cod_producto, cod_serie) -> Dict:
        sql = """
            SELECT *
              FROM stock.st_producto_serie
             WHERE empresa = :empresa
               AND cod_producto = :cod_producto
               AND numero_serie = :cod_serie 
        """
        with db1.cursor() as cur:
            cur.execute(sql, {
                "empresa": empresa,
                "cod_producto": cod_producto,
                "cod_serie": cod_serie
            })
            row = cur.fetchone()
            if not row:
                raise ProductoSerieNoExiste(
                    f"Producto/serie no existe. Empresa={empresa}, Producto={cod_producto}, Serie={cod_serie}"
                )
            cols = [c[0].lower() for c in cur.description]
            return dict(zip(cols, row))

    def _obtener_agente_y_useridc(db1) -> Dict:
        sql = """
            SELECT b.cod_vendedor, a.useridc_anterior
              FROM ad_usuarios a
              JOIN st_vendedor b
                ON a.identificacion = REPLACE(b.cedula, '-') 
             WHERE a.codigo_usuario = USER
               AND b.activo = 'S'
               AND ROWNUM = 1
        """
        with db1.cursor() as cur:
            cur.execute(sql)
            row = cur.fetchone()
            if not row:
                raise AgenteNoEncontrado(
                    "No existe Código de Agente para el usuario actual (USER)."
                )
            return {"cod_agente": row[0], "useridc": row[1]}

    try:
        reg = _consulta_producto_serie(
            db1, empresa=empresa, cod_producto=cod_producto, cod_serie=cod_serie
        )

        datos_agente = _obtener_agente_y_useridc(db1)
        v_cod_agente = datos_agente["cod_agente"]
        v_useridc = datos_agente["useridc"]

        with db1.cursor() as cur:
            v_tipo_comprobante = cur.var(str)
            v_cod_comprobante = cur.var(str)

            cur.callproc(
                "KS_TRANSFERENCIA.CAMBIO_ESTADO",
                [
                    empresa,
                    reg["cod_producto"],
                    reg["numero_serie"],
                    reg["cod_estado_producto"],
                    estado_nuevo,
                    numero_agencia,
                    v_tipo_comprobante,    # OUT
                    v_cod_comprobante,     # OUT
                ],
            )
            v_tipo_comprobante_val = v_tipo_comprobante.getvalue()
            v_cod_comprobante_val = v_cod_comprobante.getvalue()

            v_cod_tipo_comprobante_g = cur.var(str)
            v_cod_comprobante_g = cur.var(str)

            cur.callproc(
                "KSA_COMPROBANTE.GRABA_TS",
                [
                    empresa,
                    v_tipo_comprobante_val,
                    v_cod_comprobante_val,
                    "VEN",
                    v_cod_agente,
                    numero_agencia,
                    v_useridc,
                    empresa_g,                 # IN
                    v_cod_tipo_comprobante_g,  # OUT
                    v_cod_comprobante_g,       # OUT
                ],
            )
            v_cod_tipo_comprobante_g_val = v_cod_tipo_comprobante_g.getvalue()
            v_cod_comprobante_g_val = v_cod_comprobante_g.getvalue()

            cur.callproc(
                "KSA_COMPROBANTE.GRABA_NE",
                [
                    empresa,
                    v_cod_tipo_comprobante_g_val,
                    v_cod_comprobante_g_val,
                    empresa_g,
                    v_tipo_comprobante_val,
                    v_cod_comprobante_val,
                ],
            )

        db1.commit()

        return {
            "ok": True,
            "mensaje": "Transferencia y comprobantes procesados correctamente.",
            "outs": {
                "tipo_comprobante": v_tipo_comprobante_val,
                "cod_comprobante": v_cod_comprobante_val,
                "cod_tipo_comprobante_g": v_cod_tipo_comprobante_g_val,
                "cod_comprobante_g": v_cod_comprobante_g_val,
            },
            "agente": {"cod_agente": v_cod_agente, "useridc": v_useridc},
            "producto_serie": {
                "cod_producto": reg["cod_producto"],
                "numero_serie": reg["numero_serie"],
                "cod_estado_producto": reg["cod_estado_producto"],
            },
        }

    except (AgenteNoEncontrado, ProductoSerieNoExiste) as e:
        db1.rollback()
        return {"ok": False, "mensaje": str(e)}
    except Exception:
        db1.rollback()
        raise

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
        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = db1.cursor()
        result_rc_listado_pedidos = cursor.var(cx_Oracle.CURSOR)
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

        result = []
        cursor_output = result_rc_listado_pedidos.getvalue()
        columns = [col[0] for col in cursor_output.description]

        for row in cursor_output:
            row_dict = dict(zip(columns, row))
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


@bplog.route('/info_moto', methods=['POST'])
@jwt_required()
@cross_origin()
def info_moto():
    data = request.json or {}
    cod_comprobante = data.get('cod_comprobante')
    tipo_comprobante = data.get('tipo_comprobante')
    cod_producto = data.get('cod_producto')
    empresa = data.get('empresa')
    cod_bodega = data.get('cod_bodega')
    current_identification = data.get('current_identification')
    cod_motor = data.get('cod_motor')

    required = {
        "cod_comprobante": cod_comprobante,
        "tipo_comprobante": tipo_comprobante,
        "empresa": empresa,
        "cod_bodega": cod_bodega,
        "cod_motor": cod_motor,
    }
    missing = [k for k, v in required.items() if v in (None, "")]
    if missing:
        return jsonify({"error": f"Faltan campos requeridos: {', '.join(missing)}"}), 400

    if cod_bodega == 1:
        bodega_actual = cod_bodega
        bodega_contra = 25
    else:
        bodega_actual = 25
        bodega_contra = cod_bodega

    db1 = None
    try:
        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))

        def existe_transferencia_por_serie(
                db1,
                *,
                empresa: int,
                numero_serie: str
        ) -> bool:
            """
            Valida si existe al menos un registro en STA_TRANSFERENCIA
            con los parámetros dados.
            Retorna True si existe, False en caso contrario.
            """
            sql = """
                SELECT COUNT(1)
                  FROM sta_transferencia x
                 WHERE x.cod_tipo_comprobante in ('DG', 'CN') 
                   AND x.empresa              = :empresa
                   AND x.numero_serie         = :numero_serie
                   AND x.fecha_adicion > sysdate -10
            """
            with db1.cursor() as cur:
                cur.execute(sql, {
                    "empresa": empresa,
                    "numero_serie": numero_serie,
                })
                row = cur.fetchone()
                return row and row[0] > 0

        def obtener_cod_producto_por_motor(
                db1,
                *,
                cod_motor: str
        ) -> str:
            """
            Devuelve el cod_producto asociado a un cod_motor en st_prod_packing_list.
            Si no existe, retorna None.
            """
            sql = """
                SELECT s.cod_producto
                  FROM st_prod_packing_list s
                 WHERE s.cod_motor = :cod_motor
            """
            with db1.cursor() as cur:
                cur.execute(sql, {"cod_motor": cod_motor})
                row = cur.fetchone()
                return row[0] if row else None


        if existe_transferencia_por_serie(
                db1,
                empresa=20,
                numero_serie=cod_motor
        ):
            return jsonify({"error": "Serie previamente asignada"}), 500

        print(obtener_cod_producto_por_motor(db1, cod_motor=cod_motor))

        if obtener_cod_producto_por_motor(db1, cod_motor=cod_motor)!= cod_producto:
            return jsonify({"error": "Serie no pertenece a Modelo Seleccionado"}), 500
        def fetch_one_count(sql, binds):
            with db1.cursor() as cur:
                cur.execute(sql, binds)
                row = cur.fetchone()
                return int(row[0]) if row and row[0] is not None else 0

        sql_x = """
            select count(*) as x
            from st_prod_packing_list a, st_inventario_serie b, producto p
            where a.cod_motor = b.numero_serie
              and a.cod_producto = b.cod_producto
              and a.empresa = b.empresa
              and a.cod_producto = p.cod_producto
              and a.empresa = p.empresa
              and replace(a.cod_motor,' ') = replace(:cod_motor,' ')
              and b.cod_bodega = :bodega_actual
              and exists (
                select 1 from sta_movimiento x
                where a.cod_producto = x.cod_producto
                  and x.cod_comprobante = :cod_comprobante
                  and x.tipo_comprobante = :tipo_comprobante
                  and x.empresa = a.empresa
              )
        """
        x = fetch_one_count(sql_x, {
            "cod_motor": cod_motor,
            "bodega_actual": bodega_actual,
            "cod_comprobante": cod_comprobante,
            "tipo_comprobante": tipo_comprobante
        })

        if x != 0:
#################################PROCESO BODEGA INTERNA##################################################################
            with db1.cursor() as cur:
                cur.execute("""
                    select a.*
                    from stock.st_producto_serie a, st_inventario_serie b
                    where a.empresa=20
                      and a.cod_producto=b.cod_producto
                      and a.numero_serie=b.numero_serie
                      and a.empresa=b.empresa
                      and a.numero_serie=:cod_motor
                      and b.cod_bodega=:cod_bodega
                """, {"cod_motor": cod_motor, "cod_bodega": cod_bodega})
                row = cur.fetchone()
                if not row:
                    return jsonify({"error": "Serie no encontrada en bodega 5"}), 404

                colnames = [d[0] for d in cur.description]
                cod_prod = row[colnames.index('COD_PRODUCTO')]

            with db1.cursor() as cur:
                cur.execute("""
                    select TRUNC(months_between(sysdate, a.fecha)) as X
                    from st_serie_movimiento a
                    where a.empresa = 20
                      and a.cod_producto = :cod_prod
                      and a.numero_serie = :cod_motor
                      and a.cod_bodega = :cod_bodega
                      and a.es_anulado='0'
                      and a.debito_credito=1
                    order by a.fecha asc
                """, {"cod_prod": cod_prod, "cod_motor": cod_motor, "cod_bodega": cod_bodega})
                row = cur.fetchone()
                v_meses = int(row[0]) if row and row[0] is not None else 0


            def count_antiguas(sql, binds):
                with db1.cursor() as cur:
                    cur.execute(sql, binds)
                    row = cur.fetchone()
                    return int(row[0]) if row and row[0] is not None else 0


            sql_antiguas_base = """
                select count(*) as y from (
                    select a.cod_bodega, a.cod_producto, a.numero_serie,
                           TRUNC(months_between(sysdate, ks_inventario_serie.obt_fecha_produccion_sb(20, a.numero_serie, 5))) meses,
                           b.cod_estado_producto
                    from st_inventario_serie a, st_producto_serie b
                    where a.empresa=b.empresa
                      and a.cod_producto=b.cod_producto
                      and b.cod_estado_producto='A'
                      and a.numero_serie=b.numero_serie
                      and {filtro_producto}
                      and a.cod_bodega={bodega}
                      and a.empresa=20
                      and not exists (
                        select '+'
                        from st_producto_excepcion_edad p
                        where a.cod_bodega=p.cod_bodega
                          and p.cod_producto=a.cod_producto
                          and a.empresa=p.empresa
                          and p.es_activo=1
                          and trunc(sysdate) between p.fecha_inicio and p.fecha_final
                          and nvl(:current_identification, nvl(p.ruc_cliente,'x'))=p.ruc_cliente
                      )
                ) where meses > :v_meses
            """

            v_series_antiguas = count_antiguas(
                sql_antiguas_base.format(filtro_producto="a.cod_producto=:cod_prod", bodega=5),
                {"cod_prod": cod_prod, "current_identification": current_identification, "v_meses": v_meses}
            )

            v_series_antiguas_2 = count_antiguas(
                sql_antiguas_base.format(filtro_producto="a.cod_producto=:cod_producto", bodega=":cod_bodega"),
                {"cod_producto": cod_producto, "cod_bodega": cod_bodega, "current_identification": current_identification,
                 "v_meses": v_meses}
            )

            v_series_antiguas_5 = v_series_antiguas + v_series_antiguas_2

            if cod_bodega != 1:
                v_series_antiguas_4 = count_antiguas(
                    sql_antiguas_base.format(filtro_producto="a.cod_producto=:cod_producto", bodega="1"),
                    {"cod_producto": cod_producto, "current_identification": current_identification, "v_meses": v_meses}
                )
                v_series_antiguas_5 += v_series_antiguas_4

            if v_series_antiguas_5 > 0:
                return jsonify({
                    "error": f"Existen {v_series_antiguas_5} serie(s) más antigua(s) que la actual. Utilice esa(s) primero."
                }), 409


            resultado = cambia_estado_y_graba(
                db1,
                empresa=empresa,
                cod_producto=cod_producto,
                cod_serie=cod_motor,
                estado_nuevo='L',
                numero_agencia=cod_bodega,
                empresa_g=empresa
            )

            def obtener_siguiente_secuencia(db1, *, empresa, cod_comprobante, tipo_comprobante) -> int:
                sql = """
                                        select nvl(max(secuencia),0)+1 as next_seq
                                          from sta_transferencia x
                                         where x.cod_comprobante = :cod_comprobante
                                           and x.cod_tipo_comprobante = :tipo_comprobante
                                           and x.empresa = :empresa
                                    """
                with db1.cursor() as cur:
                    cur.execute(sql, {
                                "cod_comprobante": cod_comprobante,
                                "tipo_comprobante": tipo_comprobante,
                                "empresa": empresa
                        })
                    row = cur.fetchone()
                    return int(row[0]) if row and row[0] is not None else 1

            secuencia = obtener_siguiente_secuencia(
                    db1,
                    empresa=empresa,
                    cod_comprobante=cod_comprobante,
                    tipo_comprobante=tipo_comprobante
                )

            with db1.cursor() as cur:
                cur.execute("""
                        insert into STA_TRANSFERENCIA (
                                COD_COMPROBANTE, COD_TIPO_COMPROBANTE, EMPRESA, SECUENCIA,
                                COD_PRODUCTO, COD_UNIDAD, CANTIDAD, ES_SERIE, NUMERO_SERIE,
                                COD_ESTADO_PRODUCTO, COD_ESTADO_PRODUCTO_ING, ES_TRANSFERENCIA_ESTADO
                        ) values (
                                :cod_comprobante, :tipo_comprobante, :empresa, :secuencia,
                                :cod_producto, 'U', 1, 1, :numero_serie, 'L', 'L', 0
                        )
                        """, {
                            "cod_comprobante": cod_comprobante,
                            "tipo_comprobante": tipo_comprobante,
                            "empresa": empresa,
                            "secuencia": secuencia,
                            "cod_producto": cod_prod,
                            "numero_serie": cod_motor
                        })


            updated_qty = ajustar_cantidad_reserva(
                empresa=empresa,
                cod_bodega=cod_bodega,
                cod_producto=cod_producto,
                op="inc",
            )
            db1.commit()

            return jsonify({"ok": "Proceso de bodega interna"}), 200


#####################################PROCESO BODEGA B1##############################################################

        sql_y = """
            select count(*) as x
            from st_prod_packing_list a, st_inventario_serie b, producto p
            where a.cod_motor = b.numero_serie
              and a.cod_producto = b.cod_producto
              and a.empresa = b.empresa
              and a.cod_producto = p.cod_producto
              and a.empresa = p.empresa
              and replace(a.cod_motor,' ') = replace(:cod_motor,' ')
              and b.cod_bodega in (:bodega_contra, 5)
              and exists (
                select 1 from sta_movimiento x
                where a.cod_producto = x.cod_producto
                  and x.cod_comprobante = :cod_comprobante
                  and x.tipo_comprobante = :tipo_comprobante
                  and x.empresa = a.empresa
              )
        """
        y = fetch_one_count(sql_y, {
            "cod_motor": cod_motor,
            "bodega_contra": bodega_contra,
            "cod_comprobante": cod_comprobante,
            "tipo_comprobante": tipo_comprobante
        })
        if y == 0:
            return jsonify({"error": "SERIE NO EXISTE EN B1, A3 ni N2"}), 404

        with db1.cursor() as cur:
            cur.execute("""
                select a.*
                from stock.st_producto_serie a, st_inventario_serie b
                where a.empresa=20
                  and a.cod_producto=b.cod_producto
                  and a.numero_serie=b.numero_serie
                  and a.empresa=b.empresa
                  and a.numero_serie=:cod_motor
                  and b.cod_bodega=5
            """, {"cod_motor": cod_motor})
            row = cur.fetchone()
            if not row:
                return jsonify({"error": "Serie no encontrada en bodega 5"}), 404

            colnames = [d[0] for d in cur.description]
            cod_prod = row[colnames.index('COD_PRODUCTO')]

        with db1.cursor() as cur:
            cur.execute("""
                select TRUNC(months_between(sysdate, a.fecha)) as X
                from st_serie_movimiento a
                where a.empresa = 20
                  and a.cod_producto = :cod_prod
                  and a.numero_serie = :cod_motor
                  and a.cod_bodega = 5
                  and a.es_anulado='0'
                  and a.debito_credito=1
                order by a.fecha asc
            """, {"cod_prod": cod_prod, "cod_motor": cod_motor})
            row = cur.fetchone()
            v_meses = int(row[0]) if row and row[0] is not None else 0

        def count_antiguas(sql, binds):
            with db1.cursor() as cur:
                cur.execute(sql, binds)
                row = cur.fetchone()
                return int(row[0]) if row and row[0] is not None else 0

        sql_antiguas_base = """
            select count(*) as y from (
                select a.cod_bodega, a.cod_producto, a.numero_serie,
                       TRUNC(months_between(sysdate, ks_inventario_serie.obt_fecha_produccion_sb(20, a.numero_serie, 5))) meses,
                       b.cod_estado_producto
                from st_inventario_serie a, st_producto_serie b
                where a.empresa=b.empresa
                  and a.cod_producto=b.cod_producto
                  and b.cod_estado_producto='A'
                  and a.numero_serie=b.numero_serie
                  and {filtro_producto}
                  and a.cod_bodega={bodega}
                  and a.empresa=20
                  and not exists (
                    select '+'
                    from st_producto_excepcion_edad p
                    where a.cod_bodega=p.cod_bodega
                      and p.cod_producto=a.cod_producto
                      and a.empresa=p.empresa
                      and p.es_activo=1
                      and trunc(sysdate) between p.fecha_inicio and p.fecha_final
                      and nvl(:current_identification, nvl(p.ruc_cliente,'x'))=p.ruc_cliente
                  )
            ) where meses > :v_meses
        """

        v_series_antiguas  = count_antiguas(
            sql_antiguas_base.format(filtro_producto="a.cod_producto=:cod_prod", bodega=5),
            {"cod_prod": cod_prod, "current_identification": current_identification, "v_meses": v_meses}
        )

        v_series_antiguas_2 = count_antiguas(
            sql_antiguas_base.format(filtro_producto="a.cod_producto=:cod_producto", bodega=":cod_bodega"),
            {"cod_producto": cod_producto, "cod_bodega": cod_bodega, "current_identification": current_identification, "v_meses": v_meses}
        )

        v_series_antiguas_5 = v_series_antiguas + v_series_antiguas_2

        if cod_bodega != 1:
            v_series_antiguas_4 = count_antiguas(
                sql_antiguas_base.format(filtro_producto="a.cod_producto=:cod_producto", bodega="1"),
                {"cod_producto": cod_producto, "current_identification": current_identification, "v_meses": v_meses}
            )
            v_series_antiguas_5 += v_series_antiguas_4

        if v_series_antiguas_5 > 0:
            return jsonify({
                "error": f"Existen {v_series_antiguas_5} serie(s) más antigua(s) que la actual. Utilice esa(s) primero."
            }), 409

        with db1.cursor() as cur:
            cur.callproc(
                "STOCK.ks_prod_orden_d_proceso.genera_ip_trans",
                [empresa, cod_comprobante, tipo_comprobante, cod_motor, cod_bodega]
            )
        db1.commit()
        return jsonify({"ok": "Serie asignada correctamente"}), 200

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        return jsonify({"error": error.message}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            if db1:
                db1.close()
        except Exception:
            pass
@bplog.route('/info_moto_des', methods=['POST'])
@jwt_required()
@cross_origin()
def revertir_transferencia():
    data = request.json or {}

    empresa            = data.get("empresa")
    cod_comprobante    = data.get("cod_comprobante")
    tipo_comprobante   = data.get("tipo_comprobante")
    cod_producto       = data.get("cod_producto")
    numero_serie       = data.get("numero_serie")
    numero_agencia     = data.get("numero_agencia")
    empresa_g          = data.get("empresa_g") or empresa
    cod_estado_actual  = data.get("cod_estado_producto")
    # Validaciones mínimas
    requeridos = {
        "empresa": empresa,
        "cod_comprobante": cod_comprobante,
        "tipo_comprobante": tipo_comprobante,
        "cod_producto": cod_producto,
        "numero_serie": numero_serie,
        "numero_agencia": numero_agencia,
    }
    faltantes = [k for k, v in requeridos.items() if v in (None, "")]
    if faltantes:
        return jsonify({"error": f"Faltan campos requeridos: {', '.join(faltantes)}"}), 400

    db1 = None
    try:
        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))

        with db1.cursor() as cur:
            cur.execute(
                """
                DELETE FROM sta_transferencia x
                 WHERE x.cod_comprobante      = :cod_comprobante
                   AND x.cod_tipo_comprobante = :tipo_comprobante
                   AND x.empresa              = :empresa
                   AND x.cod_producto         = :cod_producto
                   AND x.numero_serie         = :numero_serie
                """,
                {
                    "cod_comprobante": cod_comprobante,
                    "tipo_comprobante": tipo_comprobante,
                    "empresa": empresa,
                    "cod_producto": cod_producto,
                    "numero_serie": numero_serie,
                },
            )
        db1.commit()

        if str(cod_estado_actual) == "L":
            resultado = cambia_estado_y_graba(
                db1,
                empresa=int(empresa),
                cod_producto=str(cod_producto),
                cod_serie=str(numero_serie),
                estado_nuevo="A",
                numero_agencia=int(numero_agencia),
                empresa_g=int(empresa_g),
            )
            return jsonify({
                "ok": True,
                "mensaje": "Transferencia revertida y estado cambiado a 'A'.",
                "outs": resultado.get("outs", {}),
                "agente": resultado.get("agente", {}),
                "producto_serie": resultado.get("producto_serie", {}),
            }), 200

        return jsonify({
            "ok": True,
            "mensaje": "Transferencia revertida. No se cambió estado porque no era 'L'.",
            "estado_actual": cod_estado_actual
        }), 200

    except cx_Oracle.DatabaseError as e:
        if db1:
            try:
                db1.rollback()
            except Exception:
                pass
        error, = e.args
        return jsonify({"error": error.message}), 500
    except Exception as e:
        if db1:
            try:
                db1.rollback()
            except Exception:
                pass
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            if db1:
                db1.close()
        except Exception:
            pass

@bplog.route('/transferencias', methods=['GET'])
@jwt_required()
@cross_origin()
def get_transferencias():
    """
    GET /transferencias?cod_comprobante=...&cod_tipo_comprobante=...&empresa=...&cod_producto=...
    Retorna las filas de STA_TRANSFERENCIA que coinciden con los parámetros.
    """
    try:
        cod_comprobante = request.args.get('cod_comprobante', type=str)
        cod_tipo_comprobante = request.args.get('cod_tipo_comprobante', type=str)
        empresa = request.args.get('empresa', type=int)
        cod_producto = request.args.get('cod_producto', type=str)  # <-- opcional

        # Validación de parámetros obligatorios
        missing = []
        if not cod_comprobante:
            missing.append("cod_comprobante")
        if not cod_tipo_comprobante:
            missing.append("cod_tipo_comprobante")
        if empresa is None:
            missing.append("empresa")

        if missing:
            return jsonify({"error": f"Faltan parámetros: {', '.join(missing)}"}), 400

        # Conexión y consulta
        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = db1.cursor()

        sql = """
            SELECT
                COD_COMPROBANTE,
                COD_TIPO_COMPROBANTE,
                EMPRESA,
                SECUENCIA,
                COD_PRODUCTO,
                COD_UNIDAD,
                CANTIDAD,
                ES_SERIE,
                NUMERO_SERIE,
                COD_ESTADO_PRODUCTO,
                COD_ESTADO_PRODUCTO_ING,
                ES_TRANSFERENCIA_ESTADO,
                FECHA_ADICION
            FROM STA_TRANSFERENCIA
            WHERE COD_COMPROBANTE = :cod_comprobante
              AND COD_TIPO_COMPROBANTE = :cod_tipo_comprobante
              AND EMPRESA = :empresa
        """

        params = {
            "cod_comprobante": cod_comprobante,
            "cod_tipo_comprobante": cod_tipo_comprobante,
            "empresa": empresa
        }

        if cod_producto:  # se agrega filtro extra si llega
            sql += " AND COD_PRODUCTO = :cod_producto"
            params["cod_producto"] = cod_producto

        sql += " ORDER BY SECUENCIA"

        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        data = [dict(zip(columns, row)) for row in results]

        cursor.close()
        db1.close()

        return jsonify(data), 200

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        return jsonify({"error": error.message}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bplog.route('/series_antiguas_por_serie', methods=['GET'])
@jwt_required()
@cross_origin()
def series_antiguas_por_serie():
    """
    GET /series_antiguas_por_serie?numero_serie=XY163FMLTA029358&empresa=20

    Devuelve las filas (de bodegas 1, 25 y 5) cuya fecha de producción
    resulta en una edad mayor que la edad de la serie actual (calculada
    desde KS_INVENTARIO_SERIE.OBT_FECHA_PRODUCCION_SB_PT) y ordenadas
    por edad_dias desc.
    """
    try:
        numero_serie = request.args.get('numero_serie', type=str)
        empresa = request.args.get('empresa', type=int, default=20)

        if not numero_serie:
            return jsonify({"error": "Falta parámetro: numero_serie"}), 400

        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur = db1.cursor()

        sql = """
            SELECT *
              FROM (
                    SELECT i.*,
                           b.nombre,
                           TRUNC(SYSDATE) -
                           TRUNC(ks_inventario_serie.obt_fecha_produccion_sb_pt(
                                    p_cod_empresa => i.empresa,
                                    p_cod_motor   => i.numero_serie,
                                    p_cod_bodega  => 5
                                )) AS edad_dias,
                        x.fecha_produccion,
                           x.edad_dias AS edad_serie_actual
                      FROM st_inventario_serie i,
                           bodega b,
                           (
                                SELECT s.cod_producto,
                                       s.empresa,
                                       s.numero_serie,
                                       TRUNC(SYSDATE) -
                                       TRUNC(
                                           NVL(
                                               ks_inventario_serie.obt_fecha_produccion_sb_pt(
                                                   p_cod_empresa => s.empresa,
                                                   p_cod_motor   => s.numero_serie,
                                                   p_cod_bodega  => 5
                                               ),
                                               ks_inventario_serie.obt_fecha_produccion_sb_pt(
                                                   p_cod_empresa => s.empresa,
                                                   p_cod_motor   => s.numero_serie,
                                                   p_cod_bodega  => 3
                                               )
                                           )
                                       ) AS edad_dias,
                                        ks_inventario_serie.obt_fecha_produccion_sb_pt(
                                    p_cod_empresa => s.empresa,
                                    p_cod_motor   => s.numero_serie,
                                    p_cod_bodega  => 5
                                ) fecha_produccion
                                    
                                  FROM st_producto_serie s,
                                       st_inventario_serie iv
                                 WHERE s.numero_serie = :numero_serie
                                   AND s.empresa      = :empresa
                                   AND s.cantidad    != 0
                                   AND s.empresa      = iv.empresa
                                   AND iv.numero_serie= s.numero_serie
                           ) x
                     WHERE i.empresa = :empresa
                       AND x.empresa = i.empresa
                       AND x.cod_producto = i.cod_producto
                       AND x.numero_serie <> i.numero_serie
                       AND b.empresa = i.empresa
                       AND b.bodega  = i.cod_bodega
                       AND i.cod_bodega IN (1, 25, 5)
                       AND TRUNC(SYSDATE) -
                           TRUNC(ks_inventario_serie.obt_fecha_produccion_sb_pt(
                                    p_cod_empresa => i.empresa,
                                    p_cod_motor   => i.numero_serie,
                                    p_cod_bodega  => 5
                                )) > x.edad_dias
                   ) sub
             ORDER BY sub.edad_dias DESC
        """

        params = {
            "numero_serie": numero_serie.strip(),
            "empresa": int(empresa),
        }

        cur.execute(sql, params)
        cols = [c[0] for c in cur.description]
        rows = cur.fetchall()
        data = [dict(zip(cols, r)) for r in rows]

        cur.close()
        db1.close()

        return jsonify(data), 200

    except cx_Oracle.DatabaseError as e:
        try:
            if db1:
                db1.close()
        except Exception:
            pass
        error, = e.args
        return jsonify({"error": error.message}), 500
    except Exception as e:
        try:
            if db1:
                db1.close()
        except Exception:
            pass
        return jsonify({"error": str(e)}), 500

# ===============================================
# STA_TRANS_COMENTARIOS_HANDHELD ENDPOINTS
# ===============================================

@bplog.route('/transferencias/comentarios/rango', methods=['GET'])
@jwt_required()
@cross_origin()
def comentarios_por_rango():
    """
    GET /transferencias/comentarios/rango?empresa=20&desde=2025-09-01&hasta=2025-09-08
      [opcionales]
        cod_comprobante=...
        cod_tipo_comprobante=...
        secuencia=...
        cod_producto=...
        numero_serie=...
        usuario_creacion=...
        origen=...
        tipo_comentario=...
        es_activo=0|1
        buscar=texto  (LIKE sobre COMENTARIO)
    Requiere: empresa, desde, hasta
    """
    db1 = None
    try:
        args = request.args

        empresa = args.get('empresa', type=int)
        desde_s = parse_str(args.get('desde'))
        hasta_s = parse_str(args.get('hasta'))

        missing = []
        if empresa is None: missing.append("empresa")
        if not desde_s:     missing.append("desde")
        if not hasta_s:     missing.append("hasta")
        if missing:
            return jsonify({"error": f"Faltan parámetros: {', '.join(missing)}"}), 400

        desde = parse_date(desde_s)
        hasta = parse_date(hasta_s)

        cod_comprobante      = parse_str(args.get('cod_comprobante'))
        cod_tipo_comprobante = parse_str(args.get('cod_tipo_comprobante'))
        secuencia            = args.get('secuencia', type=int)
        cod_producto         = parse_str(args.get('cod_producto'))
        numero_serie         = parse_str(args.get('numero_serie'))
        usuario_creacion     = parse_str(args.get('usuario_creacion'))
        origen               = parse_str(args.get('origen'))
        tipo_comentario      = parse_str(args.get('tipo_comentario'))
        es_activo            = args.get('es_activo', type=int)
        buscar               = parse_str(args.get('buscar'))

        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur = db1.cursor()

        sql = """
            SELECT
                COD_COMPROBANTE,
                COD_TIPO_COMPROBANTE,
                EMPRESA,
                SECUENCIA,
                COD_PRODUCTO,
                SECUENCIA_COMENTARIO,
                NUMERO_SERIE,
                COMENTARIO,
                USUARIO_CREACION,
                FECHA_CREACION,
                USUARIO_MODIFICACION,
                FECHA_MODIFICACION,
                ORIGEN,
                TIPO_COMENTARIO,
                ES_ACTIVO
              FROM STA_TRANS_COMENTARIOS_HANDHELD
             WHERE EMPRESA = :empresa
               AND TRUNC(FECHA_CREACION) BETWEEN TRUNC(:desde) AND TRUNC(:hasta)
        """
        params = {"empresa": empresa, "desde": desde, "hasta": hasta}

        if cod_comprobante:
            sql += " AND COD_COMPROBANTE = :cod_comprobante"
            params["cod_comprobante"] = cod_comprobante
        if cod_tipo_comprobante:
            sql += " AND COD_TIPO_COMPROBANTE = :cod_tipo_comprobante"
            params["cod_tipo_comprobante"] = cod_tipo_comprobante
        if secuencia is not None:
            sql += " AND SECUENCIA = :secuencia"
            params["secuencia"] = secuencia
        if cod_producto:
            sql += " AND COD_PRODUCTO = :cod_producto"
            params["cod_producto"] = cod_producto
        if numero_serie:
            sql += " AND NUMERO_SERIE = :numero_serie"
            params["numero_serie"] = numero_serie
        if usuario_creacion:
            sql += " AND USUARIO_CREACION = :usuario_creacion"
            params["usuario_creacion"] = usuario_creacion
        if origen:
            sql += " AND ORIGEN = :origen"
            params["origen"] = origen
        if tipo_comentario:
            sql += " AND TIPO_COMENTARIO = :tipo_comentario"
            params["tipo_comentario"] = tipo_comentario
        if es_activo in (0, 1):
            sql += " AND ES_ACTIVO = :es_activo"
            params["es_activo"] = es_activo
        if buscar:
            sql += " AND UPPER(COMENTARIO) LIKE UPPER(:buscar)"
            params["buscar"] = f"%{buscar}%"

        sql += " ORDER BY FECHA_CREACION DESC, COD_COMPROBANTE, SECUENCIA, SECUENCIA_COMENTARIO"

        cur.execute(sql, params)
        cols = [c[0] for c in cur.description]
        data = [dict(zip(cols, r)) for r in cur.fetchall()]

        cur.close()
        db1.close()
        return jsonify(data), 200

    except cx_Oracle.DatabaseError as e:
        try:
            if db1: db1.close()
        except Exception:
            pass
        error, = e.args
        return jsonify({"error": error.message}), 500
    except Exception as e:
        try:
            if db1: db1.close()
        except Exception:
            pass
        return jsonify({"error": str(e)}), 500


@bplog.route('/transferencias/comentarios', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_comentario_transferencia():
    """
    POST /transferencias/comentarios
    Body JSON (NO opcionales):
      - cod_comprobante (str)
      - cod_tipo_comprobante (str)
      - empresa (int)
      - secuencia (int)
      - cod_producto (str)
      - comentario (str)
    Opcionales:
      - secuencia_comentario (int)  -> si no llega, se calcula MAX+1
      - numero_serie (str)
      - usuario_creacion (str)      -> si no llega, usa USER de Oracle
      - origen (str)
      - tipo_comentario (str)
      - es_activo (int: 0/1, default 1)
    """
    db1 = None
    try:
        body = request.get_json(silent=True) or {}

        cod_comprobante      = parse_str(body.get('cod_comprobante'))
        cod_tipo_comprobante = parse_str(body.get('cod_tipo_comprobante'))
        empresa              = body.get('empresa', None)
        secuencia            = None
        cod_producto         = parse_str(body.get('cod_producto'))
        comentario           = parse_str(body.get('comentario'))

        missing = []
        if not cod_comprobante:      missing.append("cod_comprobante")
        if not cod_tipo_comprobante: missing.append("cod_tipo_comprobante")
        if empresa is None:          missing.append("empresa")
        if not cod_producto:         missing.append("cod_producto")
        if not comentario:           missing.append("comentario")
        if missing:
            return jsonify({"error": f"Faltan campos requeridos: {', '.join(missing)}"}), 400

        secuencia_comentario = None
        numero_serie         = parse_str(body.get('numero_serie'))
        usuario_creacion     = parse_str(body.get('usuario_creacion'))
        origen               = parse_str(body.get('origen'))
        tipo_comentario      = parse_str(body.get('tipo_comentario'))
        es_activo            = body.get('es_activo', 1)

        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))

        # Usuario Oracle por defecto si no llega usuario_creacion
        if not usuario_creacion:
            with db1.cursor() as cur:
                cur.execute("SELECT USER FROM dual")
                usuario_creacion = cur.fetchone()[0]

        # Si no llega secuencia_comentario, calcular MAX+1 por PK parcial
        if secuencia_comentario is None:
            with db1.cursor() as cur:
                cur.execute("""
                    SELECT NVL(MAX(SECUENCIA_COMENTARIO),0)+1
                      FROM STA_TRANS_COMENTARIOS_HANDHELD
                     WHERE COD_COMPROBANTE = :c
                       AND COD_TIPO_COMPROBANTE = :t
                       AND EMPRESA = :e
                """, {"c": cod_comprobante, "t": cod_tipo_comprobante, "e": int(empresa)})
                row = cur.fetchone()
                secuencia_comentario = int(row[0]) if row and row[0] is not None else 1

        secuencia = secuencia_comentario

        with db1.cursor() as cur:
            cur.execute("""
                INSERT INTO STA_TRANS_COMENTARIOS_HANDHELD (
                    COD_COMPROBANTE, COD_TIPO_COMPROBANTE, EMPRESA, SECUENCIA,
                    COD_PRODUCTO, SECUENCIA_COMENTARIO, NUMERO_SERIE, COMENTARIO,
                    USUARIO_CREACION, FECHA_CREACION, USUARIO_MODIFICACION, FECHA_MODIFICACION,
                    ORIGEN, TIPO_COMENTARIO, ES_ACTIVO
                ) VALUES (
                    :cod_comprobante, :cod_tipo_comprobante, :empresa, :secuencia,
                    :cod_producto, :secuencia_comentario, :numero_serie, :comentario,
                    :usuario_creacion, SYSDATE, NULL, NULL,
                    :origen, :tipo_comentario, :es_activo
                )
            """, {
                "cod_comprobante": cod_comprobante,
                "cod_tipo_comprobante": cod_tipo_comprobante,
                "empresa": int(empresa),
                "secuencia": int(secuencia),
                "cod_producto": cod_producto,
                "secuencia_comentario": int(secuencia_comentario),
                "numero_serie": numero_serie,
                "comentario": comentario,
                "usuario_creacion": usuario_creacion,
                "origen": origen,
                "tipo_comentario": tipo_comentario,
                "es_activo": int(es_activo) if es_activo in (0,1) else 1
            })

        db1.commit()

        # Devolver el registro insertado
        with db1.cursor() as cur:
            cur.execute("""
                SELECT
                    COD_COMPROBANTE, COD_TIPO_COMPROBANTE, EMPRESA, SECUENCIA,
                    COD_PRODUCTO, SECUENCIA_COMENTARIO, NUMERO_SERIE, COMENTARIO,
                    USUARIO_CREACION, FECHA_CREACION, USUARIO_MODIFICACION, FECHA_MODIFICACION,
                    ORIGEN, TIPO_COMENTARIO, ES_ACTIVO
                  FROM STA_TRANS_COMENTARIOS_HANDHELD
                 WHERE COD_COMPROBANTE = :c
                   AND COD_TIPO_COMPROBANTE = :t
                   AND EMPRESA = :e
                   AND SECUENCIA = :s
                   AND SECUENCIA_COMENTARIO = :sc
            """, {"c": cod_comprobante, "t": cod_tipo_comprobante, "e": int(empresa), "s": int(secuencia), "sc": int(secuencia_comentario)})
            cols = [d[0] for d in cur.description]
            row = cur.fetchone()
            data = dict(zip(cols, row)) if row else None

        return jsonify({"ok": True, "data": data}), 201

    except cx_Oracle.DatabaseError as e:
        if db1:
            try: db1.rollback()
            except Exception: pass
        error, = e.args
        return jsonify({"error": error.message}), 500
    except Exception as e:
        if db1:
            try: db1.rollback()
            except Exception: pass
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            if db1: db1.close()
        except Exception:
            pass


@bplog.route('/transferencias/comentarios', methods=['DELETE'])
@jwt_required()
@cross_origin()
def borrar_comentario_transferencia():
    """
    DELETE /transferencias/comentarios?cod_comprobante=...&cod_tipo_comprobante=...&empresa=...&secuencia=...&secuencia_comentario=...
    Requiere: PK completa
    """
    db1 = None
    try:
        args = request.args

        cod_comprobante      = parse_str(args.get('cod_comprobante'))
        cod_tipo_comprobante = parse_str(args.get('cod_tipo_comprobante'))
        empresa              = args.get('empresa', type=int)
        secuencia            = args.get('secuencia', type=int)
        secuencia_comentario = args.get('secuencia_comentario', type=int)

        missing = []
        if not cod_comprobante:      missing.append("cod_comprobante")
        if not cod_tipo_comprobante: missing.append("cod_tipo_comprobante")
        if empresa is None:          missing.append("empresa")
        if secuencia is None:        missing.append("secuencia")
        if secuencia_comentario is None: missing.append("secuencia_comentario")
        if missing:
            return jsonify({"error": f"Faltan parámetros: {', '.join(missing)}"}), 400

        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        with db1.cursor() as cur:
            cur.execute("""
                DELETE FROM STA_TRANS_COMENTARIOS_HANDHELD
                 WHERE COD_COMPROBANTE = :c
                   AND COD_TIPO_COMPROBANTE = :t
                   AND EMPRESA = :e
                   AND SECUENCIA = :s
                   AND SECUENCIA_COMENTARIO = :sc
            """, {"c": cod_comprobante, "t": cod_tipo_comprobante, "e": int(empresa), "s": int(secuencia), "sc": int(secuencia_comentario)})
            deleted = cur.rowcount

        db1.commit()
        return jsonify({"ok": True, "deleted": deleted}), 200

    except cx_Oracle.DatabaseError as e:
        if db1:
            try: db1.rollback()
            except Exception: pass
        error, = e.args
        return jsonify({"error": error.message}), 500
    except Exception as e:
        if db1:
            try: db1.rollback()
            except Exception: pass
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            if db1: db1.close()
        except Exception:
            pass

query_params_schema = QueryParamsSchema()

# ---------- Helpers ----------
def apply_filters(q, params):
    if "empresa" in params:
        q = q.filter(STReservaProducto.empresa == params["empresa"])
    if "cod_producto" in params:
        # Exacto por defecto; si quieres LIKE prefijo, cambia aquí.
        q = q.filter(STReservaProducto.cod_producto == params["cod_producto"])
    if "cod_cliente" in params:
        q = q.filter(STReservaProducto.cod_cliente == params["cod_cliente"])
    if "cod_bodega" in params:
        q = q.filter(STReservaProducto.cod_bodega == params["cod_bodega"])
    # Fechas: si solo envían desde/hasta, aplico condición correspondiente sobre fecha_ini
    if "fecha_desde" in params:
        q = q.filter(STReservaProducto.fecha_ini >= params["fecha_desde"])
    if "fecha_hasta" in params:
        q = q.filter(STReservaProducto.fecha_ini <= params["fecha_hasta"])
    return q

def apply_ordering(q, ordering_param):
    if not ordering_param:
        # Por defecto: más reciente primero (fecha_ini DESC), luego cod_reserva DESC
        return q.order_by(STReservaProducto.fecha_ini.desc(),
                          STReservaProducto.cod_reserva.desc())
    clauses = []
    for token in ordering_param.split(","):
        token = token.strip()
        desc = token.startswith("-")
        key = token.lstrip("-")
        col = ALLOWED_ORDERING[key]
        clauses.append(col.desc() if desc else col.asc())
    return q.order_by(*clauses)

def build_page_link(page, page_size):
    if page < 1:
        return None
    # Reconstruyo URL con page y page_size
    url = request.url
    parsed = urlparse(url)
    params = dict(parse_qsl(parsed.query, keep_blank_values=True))
    params["page"] = str(page)
    params["page_size"] = str(page_size)
    new_qs = urlencode(params, doseq=True)
    return urlunparse(parsed._replace(query=new_qs))

# ---------- Endpoint ----------
@bplog.route("/reservas", methods=["GET"])
def list_reservas():
    # Validar y normalizar query params
    try:
        # Nota: Marshmallow parsea fechas ISO automáticamente
        params = query_params_schema.load(request.args)
    except ValidationError as err:
        return jsonify({"detail": "Parámetros inválidos.", "errors": err.messages}), 400

    page = params.get("page", 1)
    page_size = params.get("page_size", 20)

    # Construcción de Query
    q = db.session.query(STReservaProducto)
    q = apply_filters(q, params)
    q = apply_ordering(q, params.get("ordering"))

    # count total (antes de paginar)
    total = q.count()

    # Paginación
    items = q.offset((page - 1) * page_size).limit(page_size).all()

    # Serialización
    data = reservas_schema.dump(items)

    # Enlaces estilo DRF
    next_link = build_page_link(page + 1, page_size) if page * page_size < total else None
    prev_link = build_page_link(page - 1, page_size) if page > 1 else None

    return jsonify({
        "count": total,
        "next": next_link,
        "previous": prev_link,
        "results": data
    })

create_schema = CreateReservaSchema()
update_schema = UpdateReservaSchema()
out_schema = ReservaSchema()


@bplog.route("/reservas", methods=["POST"])
def create_reserva():
    payload = request.get_json(silent=True) or {}
    try:
        data = create_schema.load(payload)
        validate_no_active_duplicate(data)
        validate_available_stock_before_create(data)
    except Exception as e:
        from marshmallow import ValidationError
        if isinstance(e, ValidationError):
            return jsonify({"detail": "Datos inválidos.", "errors": e.messages}), 200
        raise

    # Verificación explícita de duplicado por PK
    if data.get("cod_reserva") is not None:
        existing = db.session.get(
            STReservaProducto, {"EMPRESA": data["empresa"], "COD_RESERVA": data["cod_reserva"]}
        )
        if existing:
            return jsonify({"detail": "El registro ya existe."}), 409

    obj = STReservaProducto(
        empresa=data["empresa"],
        cod_reserva=data.get("cod_reserva"),
        cod_producto=data.get("cod_producto"),
        cod_bodega=data.get("cod_bodega"),
        cod_cliente=data.get("cod_cliente"),
        fecha_ini=data.get("fecha_ini"),
        fecha_fin=data.get("fecha_fin"),
        observacion=data.get("observacion"),
        es_inactivo=data.get("es_inactivo", 0),
        cantidad=data.get("cantidad"),
        cod_bodega_destino=data.get("cod_bodega_destino"),
        cantidad_utilizada=data.get("cantidad_utilizada"),
    )

    db.session.add(obj)
    try:
        db.session.commit()
    except IntegrityError as ie:
        db.session.rollback()
        status, detail = map_integrity_error(ie)
        return jsonify({"detail": detail}), status

    body = out_schema.dump(obj)
    # Ubicación del recurso creada
    location = url_for(
        "routes_log.update_reserva",
        empresa=int(obj.empresa),
        cod_reserva=int(obj.cod_reserva),
        _external=True,
    )
    return jsonify(body), 201, {"Location": location}

@bplog.route("/reservas/<int:empresa>/<int:cod_reserva>", methods=["PUT"])
def update_reserva(empresa: int, cod_reserva: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = update_schema.load(payload)
    except Exception as e:
        from marshmallow import ValidationError
        if isinstance(e, ValidationError):
            return jsonify({"detail": "Datos inválidos.", "errors": e.messages}), 200
        raise

    # Evitar cambio de PK vía payload
    if "empresa" in data and data["empresa"] != empresa:
        return jsonify({"detail": "No se permite cambiar empresa en PUT."}), 400
    if "cod_reserva" in data and data["cod_reserva"] != cod_reserva:
        return jsonify({"detail": "No se permite cambiar cod_reserva en PUT."}), 400

    obj = db.session.get(STReservaProducto, (cod_reserva, empresa))

    if not obj:
        return jsonify({"detail": "No encontrado."}), 404

    validate_available_stock_before_update(obj, data)

    # Actualización parcial estilo PATCH pero por PUT para practicidad
    updatable_fields = [
        "cod_producto", "cod_bodega", "cod_cliente",
        "fecha_ini", "fecha_fin", "observacion",
        "es_inactivo", "cantidad", "cod_bodega_destino",
        "cantidad_utilizada"
    ]
    for f in updatable_fields:
        if f in data:
            setattr(obj, f, data[f])

    try:
        db.session.commit()
    except IntegrityError as ie:
        db.session.rollback()
        status, detail = map_integrity_error(ie)
        return jsonify({"detail": detail}), status

    return jsonify(out_schema.dump(obj)), 200

@bplog.route('/stock_productos_motos', methods=['GET'])
@jwt_required()
@cross_origin()
def get_stock_productos_motos():
    """
    GET /stock_productos_motos
    Parámetros (opcionales, defaults):
      - empresa               (int, default=20)
      - bodegas               (csv de ints, default=5,1,25)
      - aa                    (int, default=0)
      - cod_tipo_inventario   (int, default=1)
      - estado_producto       (str, default='A')                -> s.cod_estado_producto
      - cod_item_cat          (str, default='T')
      - cat_match             (str: 'exact'|'prefix', default='exact')
      - cod_producto          (str, exacto)
      - nombre_like           (str, LIKE %valor%, case-insensitive)
      - only_positive         (0|1, default=1)                  -> filtra por DISPONIBLE > 0
      - order_by              (COD_PRODUCTO|NOMBRE|COD_ITEM_CAT|STOCK_TOTAL|RESERVADO_ACTIVO|DISPONIBLE, default=NOMBRE)
      - order_dir             (ASC|DESC, default=ASC)
      - limit                 (int, default=200; 0 = sin límite)
      - offset                (int, default=0)

    Nota:
      - Reservas activas: NVL(es_inactivo,0)=0 AND fecha_fin > SYSDATE.
      - Se consideran reservas por bodega origen (r.cod_bodega IN bodegas).
        Si necesitas destino, cambia RESERVA_BODEGA_FIELD a 'cod_bodega_destino' en el SQL.
    """
    args = request.args

    def _parse_int(v, default=None):
        if v is None or str(v).strip() == '':
            return default
        return int(v)

    def _parse_csv_ints(v, default):
        if v is None or str(v).strip() == '':
            return default
        try:
            return [int(x.strip()) for x in str(v).split(',') if x.strip() != '']
        except ValueError:
            raise ValueError("Parámetro 'bodegas' inválido. Use enteros separados por coma.")

    def _parse_bool_01(v, default=1):
        if v is None or str(v).strip() == '':
            return default
        iv = int(v)
        if iv not in (0, 1):
            raise ValueError("Parámetro booleano inválido. Use 0 ó 1.")
        return iv

    allowed_order = {
        "COD_PRODUCTO": "COD_PRODUCTO",
        "NOMBRE": "NOMBRE",
        "COD_ITEM_CAT": "COD_ITEM_CAT",
        "STOCK_TOTAL": "STOCK_TOTAL",
        "RESERVADO_ACTIVO": "RESERVADO_ACTIVO",
        "DISPONIBLE": "DISPONIBLE",
    }

    try:
        empresa         = _parse_int(args.get('empresa'), 20)
        bodegas         = _parse_csv_ints(args.get('bodegas'), [5, 1, 25])
        aa              = _parse_int(args.get('aa'), 0)
        cod_tipo_inv    = _parse_int(args.get('cod_tipo_inventario'), 1)
        estado_producto = (args.get('estado_producto') or 'A').strip().upper()
        cod_item_cat    = (args.get('cod_item_cat') or 'T').strip()
        cat_match       = (args.get('cat_match') or 'exact').strip().lower()  # 'exact'|'prefix'
        cod_producto_f  = (args.get('cod_producto') or '').strip()
        nombre_like     = (args.get('nombre_like') or '').strip()
        only_positive   = _parse_bool_01(args.get('only_positive'), 1)
        order_by        = allowed_order.get((args.get('order_by') or 'NOMBRE').strip().upper(), "NOMBRE")
        order_dir       = "ASC" if (args.get('order_dir') or 'ASC').strip().upper() == "ASC" else "DESC"
        limit           = max(0, _parse_int(args.get('limit'), 200))
        offset          = max(0, _parse_int(args.get('offset'), 0))
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

    # Bindings compartidos
    binds = {
        "empresa": empresa,
        "aa": aa,
        "cod_tipo_inv": cod_tipo_inv,
        "estado_producto": estado_producto,
        "cod_item_cat": cod_item_cat,
    }

    # IN list para bodegas de inventario
    in_placeholders_stock = []
    for i, b in enumerate(bodegas):
        key = f"b{i}"
        in_placeholders_stock.append(f":{key}")
        binds[key] = b
    bodegas_in_stock = ",".join(in_placeholders_stock)

    # IN list para bodegas de reservas (usar claves distintas para claridad)
    in_placeholders_resv = []
    for i, b in enumerate(bodegas):
        key = f"rb{i}"
        in_placeholders_resv.append(f":{key}")
        binds[key] = b
    bodegas_in_resv = ",".join(in_placeholders_resv)

    # Filtro de categoría
    if cat_match == "prefix":
        cat_filter = "d.cod_item_cat LIKE :cod_item_cat_like"
        binds["cod_item_cat_like"] = f"{cod_item_cat}%"
    else:
        cat_filter = "d.cod_item_cat = :cod_item_cat"

    # Filtros opcionales
    where_extra = []
    if cod_producto_f:
        where_extra.append("d.cod_producto = :cod_producto_f")
        binds["cod_producto_f"] = cod_producto_f
    if nombre_like:
        where_extra.append("UPPER(d.nombre) LIKE :nombre_like")
        binds["nombre_like"] = f"%{nombre_like.upper()}%"

    where_extra_sql = f" AND {' AND '.join(where_extra)}" if where_extra else ""

    # Importante: cuando only_positive=1 filtramos por DISPONIBLE > 0
    only_positive_sql = "AND NVL(i.stock_total,0) > 0"   if only_positive == 1 else ""

    # Campo de bodega a considerar para reservas (origen por defecto)
    # Si deseas destino, cambia 'r.cod_bodega' -> 'r.cod_bodega_destino'
    RESERVA_BODEGA_FIELD = "r.cod_bodega"

    base_sql = f"""
        /* CTE de inventario total por producto */
        WITH inv AS (
            SELECT
                s.empresa,
                s.cod_producto,
                SUM(s.cantidad) AS stock_total
            FROM st_inventario s
            WHERE s.empresa = :empresa
              AND s.cod_bodega IN ({bodegas_in_stock})
              AND s.aa = :aa
              AND s.cod_tipo_inventario = :cod_tipo_inv
              AND s.cod_estado_producto = :estado_producto
            GROUP BY s.empresa, s.cod_producto
        ),
        /* CTE de reservas activas por producto (remanente = cantidad - NVL(cantidad_utilizada,0)) */
        resv AS (
            SELECT
                r.empresa,
                r.cod_producto,
                SUM(GREATEST(r.cantidad - NVL(r.cantidad_utilizada,0), 0)) AS reservado_activo
            FROM ST_RESERVA_PRODUCTO r
            WHERE r.empresa = :empresa
              AND NVL(r.es_inactivo, 0) = 0
              AND r.fecha_fin IS NOT NULL
              AND r.fecha_fin > SYSDATE
              AND {RESERVA_BODEGA_FIELD} IN ({bodegas_in_resv})
            GROUP BY r.empresa, r.cod_producto
        )
        SELECT
            i.cod_producto                  AS COD_PRODUCTO,
            d.nombre                        AS NOMBRE,
            d.cod_item_cat                  AS COD_ITEM_CAT,
            NVL(i.stock_total, 0)           AS STOCK_TOTAL,
            NVL(r.reservado_activo, 0)      AS RESERVADO_ACTIVO,
            (NVL(i.stock_total,0) - NVL(r.reservado_activo,0)) AS DISPONIBLE
        FROM inv i
        JOIN producto d
          ON d.empresa = i.empresa
         AND d.cod_producto = i.cod_producto
        LEFT JOIN resv r
          ON r.empresa = i.empresa
         AND r.cod_producto = i.cod_producto
        WHERE {cat_filter}
        {where_extra_sql}
        {only_positive_sql}
        ORDER BY {order_by} {order_dir}
    """

    # Paginación Oracle (ROWNUM)
    if limit > 0:
        binds["min_row"] = offset
        binds["max_row"] = offset + limit
        sql = f"""
            SELECT * FROM (
                SELECT q.*, ROWNUM rnum
                FROM (
                    {base_sql}
                ) q
                WHERE ROWNUM <= :max_row
            )
            WHERE rnum > :min_row
        """
    else:
        sql = base_sql

    db1 = None
    cur = None
    try:
        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur = db1.cursor()
        cur.execute(sql, binds)
        cols = [c[0] for c in cur.description]
        rows = cur.fetchall()
        data = [dict(zip(cols, r)) for r in rows]
        return jsonify(data), 200
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        return jsonify({"error": error.message}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            if cur: cur.close()
        finally:
            try:
                if db1: db1.close()
            except Exception:
                pass
