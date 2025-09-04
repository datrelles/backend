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
