import logging
import re
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from sqlalchemy import func

from src.config.database import db
from src.models.catalogos_bench import ModeloVersion, Motor, TipoMotor, Chasis, ElectronicaOtros, DimensionPeso, \
    Transmision, ClienteCanal, Segmento, ModeloComercial, Version, Marca

bench_model = Blueprint('routes_bench_model', __name__)
logger = logging.getLogger(__name__)

@bench_model.route('/comparar_modelos', methods=["POST"])
@jwt_required()
def comparar_modelos():
    try:
        data = request.get_json()
        base_id = data.get("modelo_base")
        comparables_ids = data.get("comparables", [])[:3]

        if not base_id or not comparables_ids:
            return jsonify({"error": "Se requiere modelo base y al menos un modelo comparable"}), 400

        # FUNCIONES DE EXTRACCIÓN NUMÉRICA
        def extract_hp(val):
            match = re.search(r'([\d.]+)\s*hp', str(val).lower())
            return float(match.group(1)) if match else None

        def extract_nm(val):
            match = re.search(r'([\d.]+)\s*nm', str(val).lower())
            return float(match.group(1)) if match else None

        def extract_kmh(val):
            match = re.search(r'([\d.]+)\s*km', str(val).lower())
            return float(match.group(1)) if match else None

        def extract_litros(val):
            match = re.search(r'([\d.]+)\s*litros?', str(val).lower())
            return float(match.group(1)) if match else None

        def extract_cc(val):
            match = re.search(r'([\d.]+)\s*cc', str(val).lower())
            return float(match.group(1)) if match else None

        def extract_garantia_meses(texto):
            texto = texto.upper()
            match_years = re.search(r'(\d+(?:[.,]\d+)?)\s*AÑOS?', texto)
            match_meses = re.search(r'(\d+(?:[.,]\d+)?)\s*MESES?', texto)
            if match_years:
                return float(match_years.group(1)) * 12
            elif match_meses:
                return float(match_meses.group(1))
            return None

        def extract_cambios(val):
            if not val:
                return None
            val = str(val).lower()
            if 'automática' in val:
                return 100
            if 'semi' in val:
                return 50
            match = re.search(r'(\d+)', val)
            return int(match.group(1)) if match else None

        def evaluar_pneumatic(cadena):
            if not cadena:
                return None
            match = re.match(r"(\d+)[/-](\d+)[/-](\d+)", cadena.replace(" ", ""))
            if not match:
                return None
            ancho, relation, rin = map(int, match.groups())
            return 2 * (ancho * (relation / 100)) + (rin * 25.4)

        def evaluar_frenos(val):
            val = (val or "").lower()
            if "disco" in val:
                return 2
            if "tambor" in val:
                return 1
            return 0

        def evaluar_aros(val):
            val = (val or "").lower()
            if "radios" in val:
                return 1
            if "aleación" in val:
                return 2
            if "aluminio" in val:
                return 2
            return 0

        # SEGMENTO
        segmento = db.session.query(Segmento.nombre_segmento).join(ClienteCanal,
            (Segmento.codigo_modelo_comercial == ClienteCanal.codigo_modelo_comercial) &
            (Segmento.codigo_marca == ClienteCanal.codigo_marca))
        segmento = segmento.filter(ClienteCanal.codigo_mod_vers_repuesto == base_id).first()
        segmento_nombre = segmento[0].lower() if segmento else ""

        mejor_si_menor = set()
        mejor_si_mayor = set()

        if segmento_nombre == "cross":
            mejor_si_mayor.update(
                {
                    "cilindrada", "caballos_fuerza",
                    "torque_maximo","altura_total",
                    "ancho_total","longitud_total",
                    "garantia","neumatico_delantero",
                    "capacidad_combustible","neumatico_trasero",
                    "velocidad_maxima","caja_cambios",
                    "frenos_traseros","frenos_delanteros"
                }
            )
        elif segmento_nombre == "scooter":
            mejor_si_menor.update(
                {
                    "cilindrada", "caballos_fuerza",
                    "torque_maximo", "altura_total",
                    "ancho_total", "longitud_total",
                    "peso_seco","frenos_traseros","frenos_delanteros"
                }
            )
            mejor_si_mayor.update(
                {
                    "capacidad_combustible" ,"velocidad_maxima",
                    "garantia", "caja_cambios", "neumatico_delantero",
                    "neumatico_trasero"
                }
            )
        elif segmento_nombre == "advento":
            mejor_si_mayor.update(
                {
                    "cilindrada", "altura_total",
                    "ancho_total", "longitud_total",
                    "garantia","velocidad_maxima"
                }
            )
        elif segmento_nombre == "utilitaria":
            mejor_si_menor.update(
                {
                    "cilindrada", "altura_total",
                    "ancho_total", "longitud_total",
                    "garantia","velocidad_maxima"
                }
            )
        elif segmento_nombre == "deportiva":
            mejor_si_menor.update(
                {
                    "cilindrada", "altura_total",
                    "ancho_total", "longitud_total"
                }
            )
        def evaluar_estado(campo, base_val, comp_val):
            extractores = {
                "caballos_fuerza": extract_hp,
                "torque_maximo": extract_nm,
                "velocidad_maxima": extract_kmh,
                "capacidad_combustible": extract_litros,
                "garantia": extract_garantia_meses,
                "cilindrada": extract_cc,
                "neumatico_delantero": evaluar_pneumatic,
                "neumatico_trasero": evaluar_pneumatic,
                "caja_cambios": extract_cambios,
                "frenos_traseros": evaluar_frenos

            }

            if campo in ["aros_rueda_delantera", "aros_rueda_posterior"]:
                base = evaluar_aros(base_val)
                comp = evaluar_aros(comp_val)

                return (
                    "mejor" if comp > base else
                    "peor" if comp < base else
                    "igual"
                )

            if campo == "frenos_traseros":
                base = evaluar_frenos(base_val)
                comp = evaluar_frenos(comp_val)

                if segmento_nombre == "scooter":
                    return "igual"
                elif segmento_nombre == "croos":
                    return "mejor" if comp > base else "peor" if comp < base else "igual"

            if campo in extractores:
                base = extractores[campo](base_val)
                comp = extractores[campo](comp_val)
            else:
                try:
                    base = float(base_val)
                    comp = float(comp_val)
                except (TypeError, ValueError):
                    base, comp = None, None

            if base is None or comp is None:
                return "igual"

            if isinstance(base, (int, float)) and isinstance(comp, (int, float)):
                if abs(base - comp) < 0.01:
                    return "igual"
            if campo in mejor_si_mayor:
                return "mejor" if comp > base else "peor" if comp < base else "igual"
            if campo in mejor_si_menor:
                return "mejor" if comp < base else "peor" if comp > base else "igual"
            return "igual"

        def cargar_detalles(modelos):
            return {
                "modelo_version": modelos.codigo_modelo_version,
                "nombre_modelo_version": modelos.nombre_modelo_version,
                "motor": db.session.query(Motor).get((modelos.codigo_motor, modelos.codigo_tipo_motor)),
                "tipo_motor": db.session.query(TipoMotor).get(modelos.codigo_tipo_motor),
                "chasis": db.session.query(Chasis).get(modelos.codigo_chasis),
                "electronica": db.session.query(ElectronicaOtros).get(modelos.codigo_electronica),
                "dimensiones": db.session.query(DimensionPeso).get(modelos.codigo_dim_peso),
                "transmision": db.session.query(Transmision).get(modelos.codigo_transmision),
            }

        base_modelo = db.session.query(ModeloVersion).filter_by(codigo_modelo_version=base_id).first()
        if not base_modelo:
            return jsonify({"error": "Modelo base no encontrado"}), 404

        detalles_base = cargar_detalles(base_modelo)
        resultado = []

        for comp_id in comparables_ids:
            modelo = db.session.query(ModeloVersion).filter_by(codigo_modelo_version=comp_id).first()
            if not modelo:
                continue
            detalles_comp = cargar_detalles(modelo)
            mejor_en = {}

            def comparar(campo, val_base, val_comp, grupo):
                estado = evaluar_estado(campo, val_base, val_comp)
                mejor_en.setdefault(grupo, []).append({
                    "campo": campo,
                    "base": val_base,
                    "comparable": val_comp,
                    "estado": estado
                })

            comparar("suspension_delantera",
                     detalles_base["chasis"].suspension_delantera,
                     detalles_comp["chasis"].suspension_delantera, "chasis")
            comparar("suspension_trasera",
                     detalles_base["chasis"].suspension_trasera,
                     detalles_comp["chasis"].suspension_trasera, "chasis")
            comparar("aros_rueda_delantera",
                     detalles_base["chasis"].aros_rueda_delantera,
                     detalles_comp["chasis"].aros_rueda_delantera, "chasis")
            comparar("aros_rueda_posterior",
                     detalles_base["chasis"].aros_rueda_posterior,
                     detalles_comp["chasis"].aros_rueda_posterior, "chasis")
            comparar("neumatico_delantero",
                     detalles_base["chasis"].neumatico_delantero,
                     detalles_comp["chasis"].neumatico_delantero, "chasis")
            comparar("neumatico_trasero",
                     detalles_base["chasis"].neumatico_trasero,
                     detalles_comp["chasis"].neumatico_trasero, "chasis")
            comparar("frenos_traseros",
                     detalles_base["chasis"].frenos_traseros,
                     detalles_comp["chasis"].frenos_traseros, "chasis")
            comparar("frenos_delanteros",
                     detalles_base["chasis"].frenos_delanteros,
                     detalles_comp["chasis"].frenos_delanteros, "chasis")

            comparar("cilindrada",
                     detalles_base["motor"].cilindrada,
                     detalles_comp["motor"].cilindrada, "motor")
            comparar("caballos_fuerza",
                     detalles_base["motor"].caballos_fuerza,
                     detalles_comp["motor"].caballos_fuerza, "motor")
            comparar("torque_maximo",
                     detalles_base["motor"].torque_maximo,
                     detalles_comp["motor"].torque_maximo, "motor")
            comparar("sistema_combustible",
                     detalles_base["motor"].sistema_combustible,
                     detalles_comp["motor"].sistema_combustible, "motor")
            comparar("arranque",
                     detalles_base["motor"].arranque,
                     detalles_comp["motor"].arranque, "motor")
            comparar("sistema_refrigeracion",
                     detalles_base["motor"].sistema_refrigeracion,
                     detalles_comp["motor"].sistema_refrigeracion, "motor")

            comparar("altura_total",
                     detalles_base["dimensiones"].altura_total,
                     detalles_comp["dimensiones"].altura_total, "dimensiones")
            comparar("longitud_total",
                     detalles_base["dimensiones"].longitud_total,
                     detalles_comp["dimensiones"].longitud_total, "dimensiones")
            comparar("ancho_total",
                     detalles_base["dimensiones"].ancho_total,
                     detalles_comp["dimensiones"].ancho_total, "dimensiones")
            comparar("peso_seco",
                     detalles_base["dimensiones"].peso_seco,
                     detalles_comp["dimensiones"].peso_seco, "dimensiones")

            comparar("capacidad_combustible",
                     detalles_base["electronica"].capacidad_combustible,
                     detalles_comp["electronica"].capacidad_combustible, "electronica")
            comparar("tablero",
                     detalles_base["electronica"].tablero, detalles_comp["electronica"].tablero, "electronica")
            comparar("luces_delanteras",
                     detalles_base["electronica"].luces_delanteras,
                     detalles_comp["electronica"].luces_delanteras, "electronica")
            comparar("luces_posteriores",
                     detalles_base["electronica"].luces_posteriores,
                     detalles_comp["electronica"].luces_posteriores, "electronica")
            comparar("garantia",
                     detalles_base["electronica"].garantia,
                     detalles_comp["electronica"].garantia, "electronica")
            comparar("velocidad_maxima",
                     detalles_base["electronica"].velocidad_maxima,
                     detalles_comp["electronica"].velocidad_maxima, "electronica")

            comparar("caja_cambios",
                     detalles_base["transmision"].caja_cambios,
                     detalles_comp["transmision"].caja_cambios, "transmision")

            resultado.append({
                "modelo_version": comp_id,
                "nombre_modelo": modelo.nombre_modelo_version,
                "mejor_en": mejor_en
            })

        return jsonify({"base": base_id, "comparables": resultado})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bench_model.route('/get_modelos_por_linea/<int:codigo_linea>', methods=['GET'])
@jwt_required()
@cross_origin()
def get_modelos_por_linea(codigo_linea):
    try:
        resultados = db.session.query(
            ModeloVersion.codigo_modelo_version,
            ModeloVersion.nombre_modelo_version,
            ModeloVersion.anio_modelo_version,
            ModeloVersion.precio_producto_modelo,
            ModeloComercial.nombre_modelo.label('nombre_modelo_comercial'),
            Motor.nombre_motor
        ).join(ClienteCanal, ModeloVersion.codigo_cliente_canal == ClienteCanal.codigo_cliente_canal) \
         .join(Segmento, (Segmento.codigo_modelo_comercial == ClienteCanal.codigo_modelo_comercial) &
                         (Segmento.codigo_marca == ClienteCanal.codigo_marca)) \
         .join(ModeloComercial, ClienteCanal.codigo_modelo_comercial == ModeloComercial.codigo_modelo_comercial) \
         .join(Motor, ModeloVersion.codigo_motor == Motor.codigo_motor) \
         .filter(Segmento.codigo_linea == codigo_linea) \
         .all()

        modelos = [
            {
                "codigo_modelo_version": r[0],
                "nombre_modelo_version": r[1],
                "anio_modelo_version": r[2],
                "precio_producto_modelo": r[3],
                "nombre_modelo_comercial": r[4],
                "nombre_motor": r[5]
            }
            for r in resultados
        ]

        return jsonify(modelos), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bench_model.route('/get_modelos_por_linea_segmento', methods=['GET'])
@jwt_required()
@cross_origin()
def get_modelos_por_linea_segmento():
    try:
        codigo_linea = request.args.get('codigo_linea', type=int)
        nombre_segmento = request.args.get('nombre_segmento', type=str)

        if not codigo_linea or not nombre_segmento:
            return jsonify({"error": "Parámetros 'codigo_linea' y 'nombre_segmento' requeridos"}), 400

        resultados = db.session.query(
            ModeloVersion.codigo_modelo_version,
            ModeloVersion.nombre_modelo_version,
            ModeloVersion.anio_modelo_version,
            ModeloVersion.precio_producto_modelo,
            ModeloComercial.nombre_modelo.label('nombre_modelo_comercial'),
            Motor.nombre_motor,
            TipoMotor.nombre_tipo,
            Version.nombre_version,
            Marca.nombre_marca,
        ).join(ClienteCanal, ModeloVersion.codigo_cliente_canal == ClienteCanal.codigo_cliente_canal) \
         .join(Segmento, (Segmento.codigo_modelo_comercial == ClienteCanal.codigo_modelo_comercial) &
                         (Segmento.codigo_marca == ClienteCanal.codigo_marca)) \
         .join(ModeloComercial, ClienteCanal.codigo_modelo_comercial == ModeloComercial.codigo_modelo_comercial) \
         .join(Motor, ModeloVersion.codigo_motor == Motor.codigo_motor) \
         .join(TipoMotor, Motor.codigo_tipo_motor == TipoMotor.codigo_tipo_motor) \
         .join(Version, ModeloVersion.codigo_version == Version.codigo_version) \
         .join(Marca, ModeloVersion.codigo_marca == Marca.codigo_marca) \
         .filter(Segmento.codigo_linea == codigo_linea) \
         .filter(func.upper(Segmento.nombre_segmento) == func.upper(nombre_segmento.strip())) \
         .all()

        modelos = [{
            "codigo_modelo_version": r[0],
            "nombre_modelo_version": r[1],
            "anio_modelo_version": r[2],
            "precio_producto_modelo": r[3],
            "nombre_modelo_comercial": r[4],
            "nombre_motor": r[5],
            "nombre_tipo": r[6],
            "nombre_version": r[7],
            "nombre_marca": r[8],
        } for r in resultados]

        return jsonify(modelos), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bench_model.route('/get_segmentos_por_linea/<int:codigo_linea>', methods=['GET'])
@jwt_required()
@cross_origin()
def get_segmentos_por_linea(codigo_linea):
    try:
        segmentos = db.session.query(
            Segmento.nombre_segmento,
            db.func.min(Segmento.codigo_segmento).label('codigo_segmento')
        ).filter(
            Segmento.codigo_linea == codigo_linea,
            Segmento.estado_segmento == 1
        ).group_by(
            Segmento.nombre_segmento
        ).order_by(
            Segmento.nombre_segmento
        ).all()

        return jsonify([
            {
                "codigo_segmento": s.codigo_segmento,
                "nombre_segmento": s.nombre_segmento
            } for s in segmentos
        ]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

from openpyxl import Workbook
from flask import send_file
import io

@bench_model.route('/exportar_comparacion_xlsx', methods=["POST"])
@jwt_required()
@cross_origin()
def exportar_comparacion_xlsx():
    try:
        data = request.get_json()
        resultado = data.get("resultado")
        modelos = data.get("modelos")

        wb = Workbook()
        ws = wb.active
        ws.title = "Resumen Comparación"

        modelo_dict = {
            m["codigo_modelo_version"]: m["nombre_modelo_version"]
            for m in modelos
        }

        for i, modelo in enumerate(resultado.get("comparables", []), start=1):
            nombre_base = modelo_dict.get(resultado["base"], "Modelo Base")
            nombre_comp = modelo_dict.get(modelo["modelo_version"], "Modelo Comparable")

            # Encabezado general
            ws.append([f"COMPARACIÓN: {nombre_base}"])
            ws.merge_cells(start_row=ws.max_row, start_column=1, end_row=ws.max_row, end_column=5)
            header_cell = ws.cell(row=ws.max_row, column=1)
            header_cell.font = Font(size=14, bold=True)
            header_cell.alignment = Alignment(horizontal="center")
            header_cell.fill = PatternFill(start_color="BDD7EE", end_color="BDD7EE", fill_type="solid")

            # Encabezados de tabla
            ws.append(["Categoría", "Campo", nombre_base, nombre_comp, "Estado"])
            header_row = ws.max_row
            for col in range(1, 6):
                cell = ws.cell(row=header_row, column=col)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")

            # Contenido
            mejor_en = modelo.get("mejor_en", {})
            for categoria, campos in mejor_en.items():
                for detalle in campos:
                    fila = [
                        categoria.capitalize(),
                        detalle["campo"],
                        detalle["base"],
                        detalle["comparable"],
                        detalle["estado"]
                    ]
                    ws.append(fila)

                    estado_valor = detalle.get("estado", "").lower()
                    estado_cell = ws.cell(row=ws.max_row, column=5)

                    if estado_valor == "mejor":
                        estado_cell.font = Font(color="006100", bold=True)
                        estado_cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                    elif estado_valor == "peor":
                        estado_cell.font = Font(color="9C0006", bold=True)
                        estado_cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
                    elif estado_valor == "igual":
                        estado_cell.font = Font(color="1F1F1F")
                        estado_cell.fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")

            ws.append([])

        # Ajustar ancho de columnas
        for col in range(1, 6):
            ws.column_dimensions[get_column_letter(col)].width = 25

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="comparacion_modelos.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
