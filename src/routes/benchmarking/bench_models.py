import logging
import re
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from src.config.database import db
from src.models.catalogos_bench import ModeloVersion, Motor, TipoMotor, Chasis, ElectronicaOtros, DimensionPeso, \
    Transmision, ClienteCanal, Segmento, ModeloComercial, Marca, Linea

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

        def extract_garantia_meses(texto):
            texto = texto.upper()
            match_anos = re.search(r'(\d+(?:[\.,]\d+)?)\s*AÑOS?', texto)
            match_meses = re.search(r'(\d+(?:[\.,]\d+)?)\s*MESES?', texto)

            if match_anos:
                return float(match_anos.group(1)) * 12
            elif match_meses:
                return float(match_meses.group(1))
            else:
                return None

        mejor_si_menor = {"peso_seco"}
        mejor_si_diferente = {"frenos_traseros", "caja_cambios"}
        mejor_si_mayor = {"caballos_fuerza", "torque_maximo", "velocidad_maxima", "cilindrada", "garantia", "capacidad_combustible"}

        def evaluar_estado(campo, valor_base, valor_comp):
            if campo == "caballos_fuerza":
                base = extract_hp(valor_base)
                comp = extract_hp(valor_comp)
            elif campo == "torque_maximo":
                base = extract_nm(valor_base)
                comp = extract_nm(valor_comp)
            elif campo == "velocidad_maxima":
                base = extract_kmh(valor_base)
                comp = extract_kmh(valor_comp)
            elif campo == "capacidad_combustible":
                base = extract_litros(valor_base)
                comp = extract_litros(valor_comp)

            elif campo == "garantia":
                base = extract_garantia_meses(valor_base)
                comp = extract_garantia_meses(valor_comp)

            elif campo in {"peso_seco", "cilindrada"}:
                try:
                    base = float(valor_base)
                    comp = float(valor_comp)
                except:
                    return "igual"
            else:
                base, comp = valor_base, valor_comp

            if base is None or comp is None:
                return "igual"

            if campo in mejor_si_mayor:
                return "mejor" if comp > base else "peor" if comp < base else "igual"
            elif campo in mejor_si_menor:
                return "mejor" if comp < base else "peor" if comp > base else "igual"
            elif campo in mejor_si_diferente:
                return "mejor" if base != comp else "igual"
            else:
                return "igual"

        def cargar_detalles(modelo):
            return {
                "modelo_version": modelo.codigo_modelo_version,
                "nombre_modelo_version": modelo.nombre_modelo_version,
                "motor": db.session.query(Motor).get((modelo.codigo_motor, modelo.codigo_tipo_motor)),
                "tipo_motor": db.session.query(TipoMotor).get(modelo.codigo_tipo_motor),
                "chasis": db.session.query(Chasis).get(modelo.codigo_chasis),
                "electronica": db.session.query(ElectronicaOtros).get(modelo.codigo_electronica),
                "dimensiones": db.session.query(DimensionPeso).get(modelo.codigo_dim_peso),
                "transmision": db.session.query(Transmision).get(modelo.codigo_transmision),
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

            def comparar(campo, valor_base, valor_comp, seccion):
                estado = evaluar_estado(campo, valor_base, valor_comp)
                mejor_en.setdefault(seccion, []).append({
                    "campo": campo,
                    "base": valor_base,
                    "comparable": valor_comp,
                    "estado": estado
                })

            comparar("suspension_delantera", detalles_base["chasis"].suspension_delantera,detalles_comp["chasis"].suspension_delantera, "chasis")
            comparar("suspension_trasera", detalles_base["chasis"].suspension_trasera,detalles_comp["chasis"].suspension_trasera, "chasis")
            comparar("aros_rueda_delantera", detalles_base["chasis"].aros_rueda_delantera,detalles_comp["chasis"].aros_rueda_delantera, "chasis")
            comparar("aros_rueda_posterior", detalles_base["chasis"].aros_rueda_posterior,detalles_comp["chasis"].aros_rueda_posterior, "chasis")
            comparar("neumatico_delantero", detalles_base["chasis"].neumatico_delantero,detalles_comp["chasis"].neumatico_delantero, "chasis")
            comparar("neumatico_trasero", detalles_base["chasis"].neumatico_trasero,detalles_comp["chasis"].neumatico_trasero, "chasis")
            comparar("frenos_traseros", detalles_base["chasis"].frenos_traseros,detalles_comp["chasis"].frenos_traseros, "chasis")
            comparar("frenos_delanteros", detalles_base["chasis"].frenos_delanteros,detalles_comp["chasis"].frenos_delanteros, "chasis")

            comparar("cilindrada", detalles_base["motor"].cilindrada, detalles_comp["motor"].cilindrada, "motor")
            comparar("caballos_fuerza", detalles_base["motor"].caballos_fuerza, detalles_comp["motor"].caballos_fuerza, "motor")
            comparar("torque_maximo", detalles_base["motor"].torque_maximo, detalles_comp["motor"].torque_maximo, "motor")
            comparar("sistema_combustible", detalles_base["motor"].sistema_combustible, detalles_comp["motor"].sistema_combustible, "motor")
            comparar("arranque", detalles_base["motor"].arranque, detalles_comp["motor"].arranque, "motor")
            comparar("arranque", detalles_base["motor"].sistema_refrigeracion, detalles_comp["motor"].sistema_refrigeracion, "motor")

            comparar("altura_total", detalles_base["dimensiones"].altura_total, detalles_comp["dimensiones"].altura_total, "dimensiones")
            comparar("longitud_total", detalles_base["dimensiones"].longitud_total, detalles_comp["dimensiones"].longitud_total, "dimensiones")
            comparar("ancho_total", detalles_base["dimensiones"].ancho_total, detalles_comp["dimensiones"].ancho_total, "dimensiones")
            comparar("peso_seco", detalles_base["dimensiones"].peso_seco, detalles_comp["dimensiones"].peso_seco, "dimensiones")

            comparar("capacidad_combustible", detalles_base["electronica"].capacidad_combustible, detalles_comp["electronica"].capacidad_combustible, "electronica")
            comparar("tablero", detalles_base["electronica"].tablero, detalles_comp["electronica"].tablero, "electronica")
            comparar("luces_delanteras", detalles_base["electronica"].luces_delanteras, detalles_comp["electronica"].luces_delanteras, "electronica")
            comparar("luces_posteriores", detalles_base["electronica"].luces_posteriores, detalles_comp["electronica"].luces_posteriores, "electronica")
            comparar("garantia", detalles_base["electronica"].garantia, detalles_comp["electronica"].garantia, "electronica")
            comparar("velocidad_maxima", detalles_base["electronica"].velocidad_maxima, detalles_comp["electronica"].velocidad_maxima, "electronica")



            comparar("caja_cambios", detalles_base["transmision"].caja_cambios, detalles_comp["transmision"].caja_cambios, "transmision")

            resultado.append({
                "modelo_version": comp_id,
                "nombre_modelo": modelo.nombre_modelo_version,
                "mejor_en": mejor_en
            })

        return jsonify({
            "base": base_id,
            "comparables": resultado
        })

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

