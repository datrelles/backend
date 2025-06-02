import io
import logging
from flask import Blueprint, jsonify, request, send_file
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
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


@bench_rep.route('/exportar_modelos_compatibles_xlsx', methods=["POST"])
@jwt_required()
@cross_origin()
def exportar_modelos_compatibles_xlsx():
    try:
        data = request.get_json()
        modelos = data.get("modelos", [])
        nombre_producto = data.get("nombre_producto", "MODELO DESCONOCIDO")

        if not modelos:
            return jsonify({"error": "No hay modelos compatibles para exportar"}), 400

        wb = Workbook()
        ws = wb.active
        ws.title = "Modelos Compatibles"

        rojo = "B22222"
        blanco = "FFFFFF"
        # Borde gris
        gray_border = Border(
            left=Side(border_style="thin", color="808080"),
            right=Side(border_style="thin", color="808080"),
            top=Side(border_style="thin", color="808080"),
            bottom=Side(border_style="thin", color="808080")
        )

        # Fila 1 - Título principal (producto/Repuesto)
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=6)
        for col in range(1, 7):
            cell = ws.cell(row=1, column=col)
            if col == 1:
                cell.value = nombre_producto.upper()
                cell.font = Font(bold=True, size=12)
                cell.alignment = Alignment(horizontal="center")
            cell.border = gray_border

        # Fila 2 - Subtítulo
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)
        for col in range(1, 7):
            cell = ws.cell(row=2, column=col)
            if col == 1:
                cell.value = "MODELOS COMPATIBLES"
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center")
            cell.border = gray_border

        # Fila 3 - Cabecera
        columnas = ["MODELO COMERCIAL", "EMPRESA", "VERSIÓN", "MARCA", "LÍNEA", "SEGMENTO"]
        for col_idx, nombre_col in enumerate(columnas, start=1):
            c = ws.cell(row=3, column=col_idx, value=nombre_col)
            c.border = gray_border
            c.font = Font(bold=True, color=blanco)
            c.fill = PatternFill(start_color=rojo, end_color=rojo, fill_type="solid")
            c.alignment = Alignment(horizontal="center", vertical="center")
            ws.column_dimensions[get_column_letter(col_idx)].width = 25

        # registro de datos
        for i, m in enumerate(modelos, start=4):
            fila = [
                m.get("nombre_modelo_comercial", ""),
                m.get("nombre_empresa", ""),
                m.get("nombre_version", ""),
                m.get("nombre_marca", ""),
                m.get("nombre_linea", ""),
                m.get("nombre_segmento", "")
            ]
            for col_idx, valor in enumerate(fila, start=1):
                c = ws.cell(row=i, column=col_idx, value=valor)
                c.border = gray_border
                c.alignment = Alignment(horizontal="left", vertical="center")

        # Guardado del archivo Excel
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="modelos_compatibles.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500