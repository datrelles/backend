import io
import json
import logging

import requests
from flask import Blueprint, jsonify, request, Response, send_file
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
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


@bench_rep.route('/exportar_comparacion_xlsx', methods=["POST"])
@jwt_required()
@cross_origin()
def exportar_comparacion_xlsx():
    try:
        data = request.get_json()
        resultado = data.get("resultado")
        modelos = data.get("modelos")

        if not resultado or "base" not in resultado or "comparables" not in resultado:
            return jsonify({"error": "Entrada inválida: faltan datos de comparación"}), 400

        modelo_dict = {m["codigo_modelo_version"]: m for m in modelos}
        base = modelo_dict.get(resultado["base"])
        comparables = [modelo_dict.get(c["modelo_version"]) for c in resultado.get("comparables", []) if modelo_dict.get(c["modelo_version"])]

        if not base or len(comparables) == 0:
            return jsonify({"error": "Debe existir un modelo base y al menos un comparable válido"}), 400

        wb = Workbook()
        ws = wb.active
        ws.title = "Resumen Comparación"

        firebrick_fill = PatternFill(start_color="B22222", end_color="B22222", fill_type="solid")

        header_cells = [
            (14, 1, "CATEGORIA"),
            (14, 2, "CAMPOS"),
            (14, 3, f"{base['nombre_modelo_comercial']} - {base['nombre_marca']}"),
            (2, 2, f"{base['nombre_modelo_comercial']} - {base['nombre_marca']}")
        ]

        for i, comp_modelo in enumerate(comparables):
            header_cells.append((14, 4 + i * 2, f"{comp_modelo['nombre_modelo_comercial']} - {comp_modelo['nombre_marca']}"))
            header_cells.append((14, 5 + i * 2, "COMPARATIVO"))
            header_cells.append((2, 4 + i * 2, f"{comp_modelo['nombre_modelo_comercial']} - {comp_modelo['nombre_marca']}"))

        for row, col, value in header_cells:
            cell = ws.cell(row=row, column=col, value=value)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.fill = firebrick_fill

        def descargar_img(url):
            try:
                if url:
                    res = requests.get(url, timeout=2)
                    if res.ok:
                        return io.BytesIO(res.content)
            except Exception as e:
                print(f"[IMG] Error al descargar: {url} -> {e}")
            return None

        urls = [base.get("path_imagen")] + [
            modelo_dict.get(c["modelo_version"], {}).get("path_imagen")
            for c in resultado.get("comparables", [])
        ]

        with ThreadPoolExecutor() as executor:
            imagenes = list(executor.map(descargar_img, urls))

        if imagenes[0]:
            img = Image(imagenes[0])
            img.width = 250
            img.height = 200
            ws.add_image(img, "B3")

        for i, img_data in enumerate(imagenes[1:]):
            if img_data:
                col = 4 + i * 2
                img = Image(img_data)
                img.width = 200
                img.height = 200
                ws.add_image(img, f"{get_column_letter(col)}3")


        campos_unicos = {}
        for idx, comp in enumerate(resultado.get("comparables", [])):
            detalles_modelo = comp.get("mejor_en", {})
            for categoria, detalles in detalles_modelo.items():
                for det in detalles:
                    clave = (categoria, det["campo"])
                    if clave not in campos_unicos:
                        campos_unicos[clave] = {
                            "categoria": categoria,
                            "campo": det["campo"],
                            "base": det.get("base", ""),
                            "comparables": [("", {"icono": "", "color": "000000"}) for _ in range(len(comparables))]
                        }
                    estado = det.get("estado", "").lower()

                    campos_unicos[clave]["comparables"][idx] = (det.get("comparable", ""), icono)

        gray_border = Border(
            left=Side(border_style="thin", color="808080"),
            right=Side(border_style="thin", color="808080"),
            top=Side(border_style="thin", color="808080"),
            bottom=Side(border_style="thin", color="808080")
        )

        agrupado_por_categoria = defaultdict(list)
        for key in sorted(campos_unicos.keys(), key=lambda k: (k[0], k[1])):
            categoria, campo = key
            agrupado_por_categoria[categoria].append((campo, campos_unicos[key]))

        current_row = 15
        for categoria, campos in agrupado_por_categoria.items():
            inicio_fusion = current_row
            for campo, datos in campos:
                campo_formateado = campo.replace('_', ' ').upper()
                fila = [categoria.upper(), campo_formateado, datos["base"]]
                for val, icono in datos["comparables"]:
                    fila.append(val)
                    fila.append(icono["icono"])
                ws.append(fila)
                row_idx = current_row

                for i, (_, icono) in enumerate(datos["comparables"]):
                    col_idx = 5 + i * 2
                    cell = ws.cell(row=row_idx, column=col_idx)
                    cell.font = Font(bold=True, color=icono["color"])
                    cell.alignment = Alignment(horizontal="center", vertical="center")

                max_col = 3 + len(comparables) * 2
                for col in range(1, max_col + 1):
                    cell = ws.cell(row=row_idx, column=col)
                    cell.border = gray_border
                    if col < 4 or col % 2 == 1:
                        cell.alignment = Alignment(horizontal="left", vertical="center")
                        if cell.value is None:
                            cell.value = ""
                current_row += 1

            if len(campos) >= 1:
                ws.merge_cells(start_row=inicio_fusion, start_column=1, end_row=current_row - 1, end_column=1)
                cell = ws.cell(row=inicio_fusion, column=1)
                cell.alignment = Alignment(vertical="center", horizontal="center")
                cell.font = Font(bold=True)

        ws.column_dimensions[get_column_letter(1)].width = 15
        ws.column_dimensions[get_column_letter(2)].width = 25
        ws.column_dimensions[get_column_letter(3)].width = 32
        for i in range(len(comparables)):
            ws.column_dimensions[get_column_letter(4 + i * 2)].width = 32
            ws.column_dimensions[get_column_letter(5 + i * 2)].width = 15

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        if output.getbuffer().nbytes < 1000:
            return jsonify({"error": "Archivo generado está vacío o corrupto"}), 500

        return send_file(
            output,
            as_attachment=True,
            download_name="comparacion_modelos.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
