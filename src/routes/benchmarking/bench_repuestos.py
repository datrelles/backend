import json
import logging

from flask import Blueprint, jsonify, request, Response
from sqlalchemy import text

from src.config.database import db

bench_rep = Blueprint('routes_bench_rep', __name__)
logger = logging.getLogger(__name__)


@bench_rep.route('/repuesto_compatibilidad', methods=['GET'])
def obtener_modelos_compatibles():
    cod_producto = request.args.get('cod_producto')
    empresa = request.args.get('empresa')

    if not cod_producto or not empresa:
        return jsonify({"error": "Parámetros 'cod_producto' y 'empresa' son obligatorios"}), 400

    sql = text("""
        SELECT DISTINCT
            mv.CODIGO_MODELO_VERSION        AS codigo_modelo_version,
            mv.NOMBRE_MODELO_VERSION        AS nombre_modelo_version,
            m.NOMBRE_MARCA                  AS nombre_marca,
            mc.NOMBRE_MODELO                AS nombre_modelo_comercial,
            l.NOMBRE_LINEA                  AS nombre_linea,           
            ls.NOMBRE_SEGMENTO              AS nombre_segmento,         
            im.PATH_IMAGEN                  AS path_imagen,
            v.NOMBRE_VERSION                AS nombre_version,
            e.NOMBRE                        AS NOMBRE_EMPRESA        
        FROM ST_MODELO_VERSION_REPUESTO r
                 JOIN ST_CLIENTE_CANAL cc
                      ON r.CODIGO_MOD_VERS_REPUESTO = cc.CODIGO_MOD_VERS_REPUESTO
                          AND r.COD_PRODUCTO = cc.COD_PRODUCTO
                          AND r.EMPRESA = cc.EMPRESA
                 JOIN ST_MODELO_VERSION mv
                      ON cc.CODIGO_MOD_VERS_REPUESTO = mv.CODIGO_MOD_VERS_REPUESTO
                          AND cc.COD_PRODUCTO = mv.COD_PRODUCTO
                          AND cc.EMPRESA = mv.EMPRESA
                 JOIN ST_MARCA m
                      ON mv.CODIGO_MARCA = m.CODIGO_MARCA
                 JOIN ST_MODELO_COMERCIAL mc
                      ON mv.CODIGO_MODELO_COMERCIAL = mc.CODIGO_MODELO_COMERCIAL
                          AND mv.CODIGO_MARCA = mc.CODIGO_MARCA
                 JOIN ST_SEGMENTO ls
                      ON mc.CODIGO_MODELO_COMERCIAL = ls.CODIGO_MODELO_COMERCIAL
                 JOIN ST_LINEA l
                      ON ls.CODIGO_LINEA = l.CODIGO_LINEA
                JOIN ST_IMAGENES im
                      ON im.CODIGO_IMAGEN= mv.CODIGO_IMAGEN
                JOIN ST_VERSION v
                      ON v.CODIGO_VERSION= mv.CODIGO_VERSION
                JOIN EMPRESA e
                      ON mv.EMPRESA = e.EMPRESA
        WHERE r.COD_PRODUCTO = :cod_producto
          AND r.EMPRESA = :empresa
    """)

    try:
        resultados = db.session.execute(sql, {
            "cod_producto": cod_producto,
            "empresa": empresa
        }).mappings().all()

        salida = [dict(row) for row in resultados]

        return jsonify(salida)

    except Exception as e:
        print(f"[ERROR] repuesto_compatibilidad: {str(e)}")
        return jsonify({"error": "Error interno", "detalle": str(e)}), 500
