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

@bplog.route('/info_moto', methods=['POST'])
@jwt_required()
@cross_origin()
def info_moto():
    data = request.json
    cod_comprobante = data.get('cod_comprobante')
    tipo_comprobante = data.get('tipo_comprobante')
    cod_producto = data.get('cod_producto')
    empresa = data.get('empresa')
    cod_bodega = data.get('cod_bodega')
    current_identification = data.get('current_identification')
    cod_motor = data.get('cod_motor')
    try:
        db1 = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = db1.cursor()


        sql = """
                        select count(*) as x
                          from  
                            st_prod_packing_list a,
                            st_inventario_serie b,
                            producto p 
                          where a.cod_motor=b.numero_serie 
                          and a.cod_producto = b.cod_producto  
                          and a.empresa=b.empresa 
                          and a.cod_producto=p.cod_producto 
                          and a.empresa=p.empresa 
                          and replace(a.cod_motor,' ') =replace(:cod_motor,' ') 
                          and b.cod_bodega=5 
                          and exists 
                            (select * from sta_movimiento x 
                                where a.cod_producto=x.cod_producto 
                                and x.cod_comprobante=:cod_comprobante 
                                and x.tipo_comprobante=:tipo_comprobante 
                                and x.empresa=a.empresa 
                            )  
                                    """

        cursor = cursor.execute(sql, [cod_motor, cod_comprobante, tipo_comprobante])
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        data = [dict(zip(columns, row)) for row in results]
        x = data[0]['X']
        # if x == 0:
        #     return jsonify({"error": 'SERIE NO EXISTE EN B1'}), 500

        cursor.close()
    ###########################################################################################
        cursor = db1.cursor()

        sql = """
                            SELECT A.*
                            FROM stock.st_prod_orden_d a, ST_PROD_PACKING_LIST B
                            WHERE A.empresa = 20
                                AND A.cod_motor = REPLACE(:cod_motor, ' ')
                                AND fecha_fin IS NULL
                                AND fecha_inicio IS NOT NULL
                                AND A.COD_PRODUCTO = B.COD_PRODUCTO
                                AND A.COD_CHASIS = B.COD_CHASIS
                                AND A.COD_MOTOR = B.COD_MOTOR
                                AND A.EMPRESA = B.EMPRESA
                                        """

        cursor = cursor.execute(sql, [cod_motor])
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        data = [dict(zip(columns, row)) for row in results]
        if not data:
            sql = """
                                    SELECT A.*
                                    FROM stock.st_prod_orden_d a, ST_PROD_PACKING_LIST B
                                    WHERE A.empresa = 20
                                        AND A.cod_motor = REPLACE(:cod_motor, ' ')
                                        AND fecha_fin IS NOT NULL
                                        AND fecha_inicio IS NOT NULL
                                        AND A.COD_PRODUCTO = B.COD_PRODUCTO
                                        AND A.COD_CHASIS = B.COD_CHASIS
                                        AND A.COD_MOTOR = B.COD_MOTOR
                                        AND A.EMPRESA = B.EMPRESA
                                                """

            cursor = cursor.execute(sql, [cod_motor])
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()
            data = [dict(zip(columns, row)) for row in results]

        cursor.close()

        cod_orden = data[0]['COD_ORDEN']
        secuencia = data[0]['SECUENCIA']
        secuencia1 = data[0]['SECUENCIA1']
        fecha_inicio = data[0]['FECHA_INICIO']
        fecha_fin = data[0]['FECHA_FIN']
        cod_producto_x = data[0]['COD_PRODUCTO']
        cod_chasis = data[0]['COD_CHASIS']

        ###############################validar si existen series mas antiguas para liberar##################################################################################

        cursor = db1.cursor()

        sql = """
                                select a.*
                                from stock.st_producto_serie a, st_inventario_serie b
                                where a.empresa=20
                                and   a.cod_producto=b.cod_producto
                                and a.numero_serie=b.numero_serie
                                and a.empresa=b.empresa
                                and   a.numero_serie=:cod_motor
                                and b.cod_bodega=5
                                            """

        cursor = cursor.execute(sql, [cod_motor])
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        data = [dict(zip(columns, row)) for row in results]
        cod_prod = data[0]['COD_PRODUCTO']
        cursor.close()

        cursor = db1.cursor()

        sql = """
                                    select TRUNC(months_between(sysdate, a.fecha)) as X
                                    from st_serie_movimiento a
                                    where a.empresa = 20
                                    and   a.cod_producto = :cod_prod
                                    and   a.numero_serie = :cod_motor
                                    and   a.cod_bodega = 5
                                    and   a.es_anulado='0'
                                    and   a.debito_credito=1
                                    order by a.fecha asc
                                                """

        cursor = cursor.execute(sql, [cod_prod, cod_motor])
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        data = [dict(zip(columns, row)) for row in results]
        v_meses = data[0]['X']
        cursor.close()

        cursor = db1.cursor()

        sql = """
                        select  
                                count(*) as y
                        from (
                            select a.cod_bodega, a.cod_producto, a.numero_serie, TRUNC(months_between(sysdate,ks_inventario_serie.obt_fecha_produccion_sb(20 ,a.numero_serie ,5 ))) meses , b.cod_estado_producto
                            from 
                                st_inventario_serie  a
                                ,st_producto_serie b
                            where a.empresa=b.empresa
                            and a.cod_producto=b.cod_producto
                            AND b.cod_estado_producto = 'A'
                            and a.numero_serie=b.numero_serie
                            and a.cod_producto=:cod_prod
                            and a.cod_bodega=5
                            and a.empresa=20
                            and not exists
                                  (select '+'
                                  from st_producto_excepcion_edad p
                                  where a.cod_bodega=p.cod_bodega
                                  and p.cod_producto=A.cod_producto
                                  and a.empresa=p.empresa
                                  and p.es_activo=1
                                  and trunc(sysdate) between p.fecha_inicio and p.fecha_final
                                  and nvl(:current_identification,nvl(p.ruc_cliente,'x'))=p.ruc_cliente
                                  )
                            )where meses> :v_meses         
                                                """

        cursor = cursor.execute(sql, [cod_prod, current_identification, v_meses])
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        data = [dict(zip(columns, row)) for row in results]
        v_series_antiguas = data[0]['Y']
        cursor.close()

        cursor = db1.cursor()

        sql = """
                            select  
                                    count(*) as y
                            from (
                                select a.cod_bodega, a.cod_producto, a.numero_serie, TRUNC(months_between(sysdate,ks_inventario_serie.obt_fecha_produccion_sb(20 ,a.numero_serie ,5 ))) meses , b.cod_estado_producto
                                from 
                                    st_inventario_serie  a
                                    ,st_producto_serie b
                                where a.empresa=b.empresa
                                and a.cod_producto=b.cod_producto
                                AND b.cod_estado_producto = 'A'
                                and a.numero_serie=b.numero_serie
                                and a.cod_producto=:cod_producto 
                                and a.cod_bodega=:cod_bodega 
                                and a.empresa=20
                                and not exists
                                      (select '+'
                                      from st_producto_excepcion_edad p
                                      where a.cod_bodega=p.cod_bodega
                                      and p.cod_producto=A.cod_producto
                                      and a.empresa=p.empresa
                                      and p.es_activo=1
                                      and trunc(sysdate) between p.fecha_inicio and p.fecha_final
                                      and nvl(:current_identification,nvl(p.ruc_cliente,'x'))=p.ruc_cliente
                                      )
                                )where meses> :v_meses         
                                                    """

        cursor = cursor.execute(sql, [cod_producto, cod_bodega, current_identification, v_meses])
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        data = [dict(zip(columns, row)) for row in results]
        v_series_antiguas_2 = data[0]['Y']
        cursor.close()
        v_series_antiguas_3 = v_series_antiguas + v_series_antiguas_2

        if cod_bodega != 1:
            cursor = db1.cursor()

            sql = """
                                    select  
                                            count(*) as y
                                    from (
                                        select a.cod_bodega, a.cod_producto, a.numero_serie, TRUNC(months_between(sysdate,ks_inventario_serie.obt_fecha_produccion_sb(20 ,a.numero_serie ,5 ))) meses , b.cod_estado_producto
                                        from 
                                            st_inventario_serie  a
                                            ,st_producto_serie b
                                        where a.empresa=b.empresa
                                        and a.cod_producto=b.cod_producto
                                        AND b.cod_estado_producto = 'A'
                                        and a.numero_serie=b.numero_serie
                                        and a.cod_producto=:cod_producto 
                                        and a.cod_bodega=:cod_bodega 
                                        and a.empresa=20
                                        and not exists
                                              (select '+'
                                              from st_producto_excepcion_edad p
                                              where a.cod_bodega=p.cod_bodega
                                              and p.cod_producto=A.cod_producto
                                              and a.empresa=p.empresa
                                              and p.es_activo=1
                                              and trunc(sysdate) between p.fecha_inicio and p.fecha_final
                                              and nvl(:current_identification,nvl(p.ruc_cliente,'x'))=p.ruc_cliente
                                              )
                                        )where meses> :v_meses         
                                                            """

            cursor = cursor.execute(sql, [cod_producto, '1', current_identification, v_meses])
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()
            data = [dict(zip(columns, row)) for row in results]
            v_series_antiguas_4 = data[0]['Y']
            cursor.close()
            v_series_antiguas_5 = v_series_antiguas_3 + v_series_antiguas_4

        if int(v_series_antiguas_5) > 0:
            return jsonify({"error": 'Existen ' + v_series_antiguas_5 + ' serie(s) mas antigua(s) que la actual. Utilice esa(s) primero.'}), 500

        with db1.cursor() as cur:
            cur.callproc(
                "STOCK.ks_prod_orden_d_proceso.genera_ip_trans",
                [empresa, cod_comprobante, tipo_comprobante, cod_motor, cod_bodega]
            )
        db1.commit()
        db1.close()
        return jsonify({"ok": "Serie asignada correctamente"}), 200

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        return jsonify({"error": error.message}), 500




