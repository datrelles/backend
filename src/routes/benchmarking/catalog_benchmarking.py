import logging
import os
from datetime import datetime

import pandas as pd
import unicodedata

from flask import request, Blueprint, jsonify
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, text
from unidecode import unidecode
from sqlalchemy.exc import IntegrityError
from src.config.database import db
from src.models.catalogos_bench import Chasis, DimensionPeso, ElectronicaOtros, Transmision, Imagenes, TipoMotor, Motor, \
    Color, Canal, MarcaRepuesto, ProductoExterno, Linea, Marca, ModeloSRI, ModeloHomologado, MatriculacionMarca, \
    ModeloComercial, Segmento, Version, ModeloVersionRepuesto, ClienteCanal, ModeloVersion, Benchmarking
from src.models.productos import Producto

bench = Blueprint('routes_bench', __name__)
logger = logging.getLogger(__name__)


def normalize(value):
    if not value:
        return ''
    value = value.strip().lower()
    return ''.join(
        c for c in unicodedata.normalize('NFD', value)
        if unicodedata.category(c) != 'Mn'
    )
@bench.route('/insert_chasis', methods=["POST"])
@jwt_required()
def insert_chasis():
    try:
        user = get_jwt_identity()
        data = request.get_json()

        if isinstance(data, dict) and "chasis" in data:
            data = data["chasis"]
        elif isinstance(data, dict):
            data = [data]

        duplicados = []
        insertados = 0

        registros = db.session.query(Chasis).all()

        for item in data:
            existe = any(
                normalize(r.aros_rueda_delantera) == normalize(item.get("aros_rueda_delantera")) and
                normalize(r.aros_rueda_posterior) == normalize(item.get("aros_rueda_posterior")) and
                normalize(r.neumatico_delantero) == normalize(item.get("neumatico_delantero")) and
                normalize(r.neumatico_trasero) == normalize(item.get("neumatico_trasero")) and
                normalize(r.suspension_delantera) == normalize(item.get("suspension_delantera")) and
                normalize(r.suspension_trasera) == normalize(item.get("suspension_trasera")) and
                normalize(r.frenos_delanteros) == normalize(item.get("frenos_delanteros")) and
                normalize(r.frenos_traseros) == normalize(item.get("frenos_traseros"))
                for r in registros
            )

            if existe:
                duplicados.append(item)
                continue

            chasis = Chasis(
                aros_rueda_delantera=item.get("aros_rueda_delantera"),
                aros_rueda_posterior=item.get("aros_rueda_posterior"),
                neumatico_delantero=item.get("neumatico_delantero"),
                neumatico_trasero=item.get("neumatico_trasero"),
                suspension_delantera=item.get("suspension_delantera"),
                suspension_trasera=item.get("suspension_trasera"),
                frenos_delanteros=item.get("frenos_delanteros"),
                frenos_traseros=item.get("frenos_traseros"),
                usuario_crea=user,
                fecha_creacion=datetime.now()
            )
            db.session.add(chasis)
            insertados += 1

        db.session.commit()

        if duplicados and len(duplicados) == len(data):
            return jsonify({"error": "Todos los registros ya existen. No se insertó ninguno"}), 409
        elif duplicados:
            return jsonify({
                "message": f"{len(data) - len(duplicados)} registro(s) insertado(s), {len(duplicados)} duplicado(s) omitido(s)"
            }), 201
        else:
            return jsonify({"message": "Chasis insertado correctamente"}), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Registro duplicado: ya existe un chasis con estos datos"
        }), 409

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_dimension', methods=["POST"])
@jwt_required()
@cross_origin()
def insert_dimension():
    def safe_float(value):
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    try:
        data = request.json
        user = get_jwt_identity()

        if isinstance(data, dict) and "dimension" in data:
            data = data["dimension"]
        elif isinstance(data, dict):
            data = [data]

        if not isinstance(data, list):
            return jsonify({"error": "Formato de datos inválido"}), 400

        registros_insertados = 0
        registros_omitidos = []

        for item in data:
            # Validación de duplicados
            existe = db.session.query(DimensionPeso).filter_by(
                altura_total=safe_float(item.get("altura_total")),
                longitud_total=safe_float(item.get("longitud_total")),
                ancho_total=safe_float(item.get("ancho_total")),
                peso_seco=safe_float(item.get("peso_seco"))
            ).first()

            if existe:
                registros_omitidos.append(item)
                continue

            nuevo = DimensionPeso(
                altura_total=safe_float(item.get("altura_total")),
                longitud_total=safe_float(item.get("longitud_total")),
                ancho_total=safe_float(item.get("ancho_total")),
                peso_seco=safe_float(item.get("peso_seco")),
                usuario_crea=user,
                fecha_creacion=datetime.now()
            )

            db.session.add(nuevo)
            registros_insertados += 1

        db.session.commit()

        if registros_insertados == 0:
            return jsonify({"error": "No se insertaron registros. Todos eran duplicados."}), 409

        return jsonify({
            "message": f"{registros_insertados} dimensión(es) insertada(s)",
            "omitidos": len(registros_omitidos)
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bench.route('/insert_electronica_otros', methods=["POST"])
@jwt_required()
@cross_origin()
def insert_electronica_otros():
    try:
        user = get_jwt_identity()
        data = request.get_json()

        if isinstance(data, dict) and "electronica" in data:
            data = data["electronica"]
        elif isinstance(data, dict):
            data = [data]

        duplicados = []
        insertados = 0

        registros = db.session.query(ElectronicaOtros).all()

        for item in data:
            existe = any(
                normalize(r.capacidad_combustible) == normalize(item.get("capacidad_combustible")) and
                normalize(r.tablero) == normalize(item.get("tablero")) and
                normalize(r.luces_delanteras) == normalize(item.get("luces_delanteras")) and
                normalize(r.luces_posteriores) == normalize(item.get("luces_posteriores")) and
                normalize(r.garantia) == normalize(item.get("garantia")) and
                normalize(r.velocidad_maxima) == normalize(item.get("velocidad_maxima"))
                for r in registros
            )

            if existe:
                duplicados.append(item)
                continue

            nuevo = ElectronicaOtros(
                capacidad_combustible=item.get("capacidad_combustible"),
                tablero=item.get("tablero"),
                luces_delanteras=item.get("luces_delanteras"),
                luces_posteriores=item.get("luces_posteriores"),
                garantia=item.get("garantia"),
                velocidad_maxima=item.get("velocidad_maxima"),
                usuario_crea=user,
                fecha_creacion=datetime.now()
            )

            db.session.add(nuevo)
            insertados += 1

        db.session.commit()

        if duplicados and len(duplicados) == len(data):
            return jsonify({"error": "Todos los registros ya existen. No se insertó ninguno"}), 409
        elif duplicados:
            return jsonify({
                "message": f"{len(data) - len(duplicados)} registro(s) insertado(s), {len(duplicados)} duplicado(s) omitido(s)"
            }), 201
        else:
            return jsonify({"message": "Elementos de electrónica/otros insertados correctamente"}), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Registro duplicado: ya existe un registro de electrónica con estos datos"
        }), 409

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_transmision', methods=["POST"])
@jwt_required()
def insert_transmision():
    try:
        data = request.json
        user = get_jwt_identity()

        nuevo = Transmision(
            caja_cambios=data.get("caja_cambios"),
            descripcion_transmision=data.get("descripcion_transmision"),
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(nuevo)
        db.session.commit()
        db.session.refresh(nuevo)
        return jsonify({"message": "Transmision insertada", "codigo_transmision": nuevo.codigo_transmision})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_path_imagen', methods=["POST"])
@jwt_required()
def insert_path_imagen():
    try:
        data = request.json
        user = get_jwt_identity()

        path = data.get("path_imagen")
        if not path:
            return jsonify({"error": "El campo 'path_imagen' es obligatorio"}), 400

        path_existe = db.session.query(Imagenes).filter_by(path_imagen=path).first()
        if path_existe:
            return jsonify({"error": "Ya existe una imagen registrada con ese path_imagen"}), 409

        nuevo = Imagenes(
            path_imagen=path,
            descripcion_imagen=data.get("descripcion_imagen"),
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(nuevo)
        db.session.commit()
        db.session.refresh(nuevo)
        return jsonify({"message": "Path de imagen insertado", "codigo_imagen": nuevo.codigo_imagen})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_tipo_motor', methods=["POST"])
@jwt_required()
def insert_tipo_motor():
    try:
        data = request.json

        nombre = data.get("nombre_tipo")
        if not nombre:
            return jsonify({"error": "El campo 'nombre_tipo' es obligatorio"}), 400

        tipo_existe = db.session.query(TipoMotor).filter(
            func.lower(TipoMotor.nombre_tipo) == nombre.lower()
        ).first()

        if tipo_existe:
            return jsonify({"error": "Ya existe un tipo de motor con ese nombre"}), 409

        nuevo = TipoMotor(
            nombre_tipo=nombre,
            descripcion_tipo_motor=data.get("descripcion_tipo_motor")
        )

        db.session.add(nuevo)
        db.session.commit()
        db.session.refresh(nuevo)
        return jsonify({"message": "Tipo de motor insertado", "codigo_tipo_motor": nuevo.codigo_tipo_motor})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bench.route('/insert_motor', methods=['POST'])
@jwt_required()
@cross_origin()
def insert_motor():
    try:
        user = get_jwt_identity()
        data = request.get_json()

        if isinstance(data, dict) and "motor" in data:
            data = data["motor"]
        elif isinstance(data, dict):
            data = [data]

        def normalize(text):
            if not text:
                return ''
            return unidecode(text.strip().lower())

        insertados = 0
        duplicados = []

        for item in data:
            nombre_tipo_motor = item.get("tipo_motor_nombre")
            if not nombre_tipo_motor:
                duplicados.append(item)
                continue

            tipo_motor = db.session.query(TipoMotor).filter(
                func.lower(func.trim(TipoMotor.nombre_tipo)) == normalize(nombre_tipo_motor)
            ).first()

            if not tipo_motor:
                tipo_motor = TipoMotor(
                    nombre_tipo=nombre_tipo_motor,
                    descripcion_tipo_motor=item.get("descripcion_tipo_motor")
                )
                db.session.add(tipo_motor)
                db.session.flush()  # obtiene el nuevo ID sin commit

            existe = db.session.query(Motor).filter(
                Motor.codigo_tipo_motor == tipo_motor.codigo_tipo_motor,
                func.lower(func.trim(Motor.nombre_motor)) == normalize(item.get("nombre_motor")),
                func.lower(func.trim(Motor.cilindrada)) == normalize(item.get("cilindrada")),
                func.lower(func.trim(Motor.caballos_fuerza)) == normalize(item.get("caballos_fuerza")),
                func.lower(func.trim(Motor.torque_maximo)) == normalize(item.get("torque_maximo")),
                func.lower(func.trim(Motor.sistema_combustible)) == normalize(item.get("sistema_combustible")),
                func.lower(func.trim(Motor.arranque)) == normalize(item.get("arranque")),
                func.lower(func.trim(Motor.sistema_refrigeracion)) == normalize(item.get("sistema_refrigeracion")),
                func.lower(func.trim(Motor.descripcion_motor)) == normalize(item.get("descripcion_motor"))
            ).first()

            if existe:
                duplicados.append(item)
                continue

            nuevo_motor = Motor(
                codigo_tipo_motor=tipo_motor.codigo_tipo_motor,
                nombre_motor=item.get("nombre_motor"),
                cilindrada=item.get("cilindrada"),
                caballos_fuerza=item.get("caballos_fuerza"),
                torque_maximo=item.get("torque_maximo"),
                sistema_combustible=item.get("sistema_combustible"),
                arranque=item.get("arranque"),
                sistema_refrigeracion=item.get("sistema_refrigeracion"),
                descripcion_motor=item.get("descripcion_motor"),
                usuario_crea=user,
                fecha_creacion=datetime.now()
            )
            db.session.add(nuevo_motor)
            insertados += 1

        db.session.commit()

        if duplicados and len(duplicados) == len(data):
            return jsonify({"error": "Todos los registros ya existen. No se insertó ninguno"}), 409
        elif duplicados:
            return jsonify({
                "message": f"{len(data) - len(duplicados)} registro(s) insertado(s), {len(duplicados)} duplicado(s) omitido(s)"
            }), 201
        else:
            return jsonify({"message": "Motor insertado correctamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bench.route('/insert_color', methods=["POST"])
@jwt_required()
def insert_color():
    try:
        user = get_jwt_identity()
        data = request.get_json()

        if isinstance(data, dict) and "color" in data:
            data = data["color"]
        elif isinstance(data, dict):
            data = [data]

        if not isinstance(data, list):
            return jsonify({"error": "Formato de datos inválido. Se esperaba una lista o un objeto con 'color'."}), 400

        # Validar campos obligatorios y duplicados en base de datos
        nombres_color = [item.get("nombre_color", "").strip().lower() for item in data]
        if not all(nombres_color):
            return jsonify({"error": "Todos los registros deben tener 'nombre_color'"}), 400

        if len(nombres_color) != len(set(nombres_color)):
            return jsonify({"error": "Existen colores duplicados en la carga"}), 409

        existentes = db.session.query(Color.nombre_color).filter(
            func.lower(Color.nombre_color).in_(nombres_color)
        ).all()
        duplicados = [row[0] for row in existentes]

        if duplicados:
            return jsonify({"error": f"Los siguientes colores ya existen: {', '.join(duplicados)}"}), 409

        # Insertar todos
        for item in data:
            nuevo = Color(
                nombre_color=item["nombre_color"].strip(),
                usuario_crea=user,
                fecha_creacion=datetime.now()
            )
            db.session.add(nuevo)

        db.session.commit()
        return jsonify({"message": "Colores insertados correctamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bench.route('/insert_canal', methods=["POST"])
@jwt_required()
def insert_canal():
    try:
        data = request.json
        user = get_jwt_identity()

        nombre_canal = data.get("nombre_canal")
        if not nombre_canal:
            return jsonify({"error": "El nombre del canal es obligatorio"}), 400

        nombre_existe = db.session.query(Canal).filter(
            func.lower(Canal.nombre_canal) == nombre_canal.lower()
        ).first()

        if nombre_existe:
            return jsonify({"error": "Este canal ya existe"}), 409

        nuevo = Canal(
            nombre_canal=nombre_canal,
            estado_canal=data.get("estado_canal"),
            descripcion_canal=data.get("descripcion_canal"),
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(nuevo)
        db.session.commit()
        db.session.refresh(nuevo)

        return jsonify({"message": "Canal insertado correctamente", "codigo_canal": nuevo.codigo_canal})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_marca_repuestos', methods=["POST"])
@jwt_required()
def insert_marca_repuestos():
    try:
        data = request.json
        user = get_jwt_identity()

        nombre_comercial = data.get("nombre_comercial")
        estado = data.get("estado_marca_rep")
        nombre_fabricante = data.get("nombre_fabricante")

        if not nombre_comercial or estado not in [0, 1]:
            return jsonify({"error": "Campos 'nombre_comercial' y 'estado_marca_rep' (0 o 1) son obligatorios"}), 400

        if nombre_fabricante:
            existe = db.session.query(MarcaRepuesto).filter(
                func.lower(MarcaRepuesto.nombre_fabricante) == nombre_fabricante.lower()
            ).first()
            if existe:
                return jsonify({"error": "Ya existe una marca con ese nombre de fabricante"}), 409

        nuevo = MarcaRepuesto(
            nombre_comercial=nombre_comercial,
            estado_marca_rep=estado,
            nombre_fabricante=nombre_fabricante,
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(nuevo)
        db.session.commit()
        db.session.refresh(nuevo)

        return jsonify({
            "message": "Marca de repuesto insertada correctamente",
            "codigo_marca_rep": nuevo.codigo_marca_rep
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_producto_externo', methods=["POST"])
@jwt_required()
def insert_producto_externo():
    try:
        data = request.json
        user = get_jwt_identity()

        codigo = data.get("codigo_prod_externo")
        marca_id = data.get("codigo_marca_rep")
        nombre = data.get("nombre_producto")
        estado = data.get("estado_prod_externo")
        empresa = data.get("empresa")

        # Validaciones obligatorias
        if not all([codigo, marca_id, nombre, empresa]):
            return jsonify({
                "error": "Los campos 'codigo_prod_externo', 'codigo_marca_rep', 'nombre_producto' y 'empresa' son obligatorios"
            }), 400

        if estado not in [0, 1, None]:
            return jsonify({"error": "El campo 'estado_prod_externo' debe ser 0 o 1"}), 400

        # Validar existencia de empresa
        existe_empresa = db.session.execute(
            text("SELECT 1 FROM empresa WHERE empresa = :empresa"),
            {"empresa": empresa}
        ).fetchone()

        if not existe_empresa:
            return jsonify({"error": f"La empresa '{empresa}' no existe en la tabla EMPRESA"}), 404

        # Validar unicidad combinada (case-insensitive)
        existe = db.session.query(ProductoExterno).filter(
            func.lower(ProductoExterno.nombre_producto) == nombre.lower(),
            ProductoExterno.codigo_marca_rep == marca_id,
            ProductoExterno.empresa == empresa
        ).first()

        if existe:
            return jsonify({
                "error": "Ya existe un producto con ese nombre para la misma marca y empresa"
            }), 409

        nuevo = ProductoExterno(
            codigo_prod_externo=codigo,
            codigo_marca_rep=marca_id,
            nombre_producto=nombre,
            estado_prod_externo=estado if estado is not None else 1,
            descripcion_producto=data.get("descripcion_producto"),
            usuario_crea=user,
            empresa=empresa,
            fecha_creacion=datetime.now()
        )

        db.session.add(nuevo)
        db.session.commit()
        db.session.refresh(nuevo)

        return jsonify({"message": "Producto externo insertado", "codigo": nuevo.codigo_prod_externo})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_linea', methods=["POST"])
@jwt_required()
def insert_linea():
    try:
        data = request.json
        user = get_jwt_identity()

        nombre = data.get("nombre_linea")
        estado = data.get("estado_linea")
        padre_id = data.get("codigo_linea_padre")

        if not nombre or estado not in [0, 1]:
            return jsonify({"error": "Los campos 'nombre_linea' y 'estado_linea' (0 o 1) son obligatorios"}), 400

        # Validar nombre único (case-insensitive)
        existe = db.session.query(Linea).filter(
            func.lower(Linea.nombre_linea) == nombre.lower()
        ).first()
        if existe:
            return jsonify({"error": "Ya existe una línea con ese nombre"}), 409

        nueva_linea = Linea(
            nombre_linea=nombre,
            estado_linea=estado,
            descripcion_linea=data.get("descripcion_linea"),
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(nueva_linea)
        db.session.flush()

        if not padre_id:
            nueva_linea.codigo_linea_padre = nueva_linea.codigo_linea
        else:
            padre = db.session.query(Linea).filter_by(codigo_linea=padre_id).first()
            if not padre:
                return jsonify({"error": "La línea padre no existe"}), 404
            nueva_linea.codigo_linea_padre = padre_id

        db.session.commit()
        return jsonify({"message": "Línea insertada correctamente", "codigo_linea": nueva_linea.codigo_linea})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_marca', methods=["POST"])
@jwt_required()
def insert_marca():
    try:
        data = request.json
        user = get_jwt_identity()

        nombre = data.get("nombre_marca")
        estado = data.get("estado_marca")

        if not nombre or estado not in [0, 1]:
            return jsonify({"error": "Los campos 'nombre_marca' y 'estado_marca' (0 o 1) son obligatorios"}), 400

        # Validación de nombre único (case-insensitive)
        existe = db.session.query(Marca).filter(
            func.lower(Marca.nombre_marca) == nombre.lower()
        ).first()
        if existe:
            return jsonify({"error": "Ya existe una marca con ese nombre"}), 409

        nueva = Marca(
            nombre_marca=nombre,
            estado_marca=estado,
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(nueva)
        db.session.commit()
        db.session.refresh(nueva)

        return jsonify({
            "message": "Marca insertada correctamente",
            "codigo_marca": nueva.codigo_marca
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_benchmarking', methods=['POST'])
@jwt_required()
def insert_benchmarking():
    try:
        data = request.json

        empresa = data.get('empresa')
        ram_inicial = data.get('ram_inicial')
        ram_final = data.get('ram_final')
        codigo_marca = data.get('codigo_marca')

        if not empresa or not ram_inicial:
            return jsonify({"error": "Campos 'empresa' y 'ram_inicial' son obligatorios"}), 400

        # Obtener siguiente valor de secuencia
        result = db.session.execute(text("SELECT stock.seq_st_benchmarking.NEXTVAL FROM dual"))
        codigo_benchmarking = result.scalar()

        nuevo = Benchmarking(
            empresa=empresa,
            ram_inicial=ram_inicial,
            ram_final=ram_final,
            codigo_marca=codigo_marca,
            codigo_benchmarking=codigo_benchmarking
        )

        db.session.add(nuevo)
        db.session.commit()

        return jsonify({"message": "Benchmarking registrado", "codigo": codigo_benchmarking})

    except IntegrityError as ie:
        db.session.rollback()
        return jsonify({"error": "Error de integridad", "detalle": str(ie)}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_modelo_sri', methods=["POST"])
@jwt_required()
def insert_modelo_sri():
    try:
        data = request.json
        user = get_jwt_identity()

        nombre = data.get("nombre_modelo")
        anio = data.get("anio_modelo")
        estado = data.get("estado_modelo")

        if not nombre or estado not in [0, 1] or not (1950 <= int(anio) <= 2100):
            return jsonify({
                "error": "Campos requeridos: nombre_modelo (string), anio_modelo (1950-2100), estado_modelo (0 o 1)"
            }), 400

        # Validación de nombre único (case-insensitive)
        existe = db.session.query(ModeloSRI).filter(
            func.lower(ModeloSRI.nombre_modelo) == nombre.lower()
        ).first()
        if existe:
            return jsonify({"error": "Ya existe un modelo con ese nombre"}), 409

        nuevo = ModeloSRI(
            nombre_modelo=nombre,
            anio_modelo=anio,
            estado_modelo=estado,
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(nuevo)
        db.session.commit()
        db.session.refresh(nuevo)

        return jsonify({
            "message": "Modelo SRI insertado correctamente",
            "codigo_modelo_sri": nuevo.codigo_modelo_sri
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_modelo_homologado', methods=["POST"])
@jwt_required()
def insert_modelo_homologado():
    try:
        data = request.json
        user = get_jwt_identity()

        codigo_sri = data.get("codigo_modelo_sri")
        descripcion = data.get("descripcion_homologacion")

        if not codigo_sri:
            return jsonify({"error": "El campo 'codigo_modelo_sri' es obligatorio"}), 400

        # Validar existencia del modelo SRI
        modelo_sri = db.session.query(ModeloSRI).filter_by(codigo_modelo_sri=codigo_sri).first()
        if not modelo_sri:
            return jsonify({"error": "El código de modelo SRI no existe"}), 404

        nuevo = ModeloHomologado(
            codigo_modelo_sri=codigo_sri,
            descripcion_homologacion=descripcion,
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(nuevo)
        db.session.commit()
        db.session.refresh(nuevo)

        return jsonify({
            "message": "Modelo homologado insertado correctamente",
            "codigo_modelo_homologado": nuevo.codigo_modelo_homologado
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_matriculacion_marca', methods=["POST"])
@jwt_required()
def insert_matriculacion_marca():
    try:
        data = request.json
        user = get_jwt_identity()

        codigo_homologado = data.get("codigo_modelo_homologado")
        placa = data.get("placa")
        detalle = data.get("detalle_matriculacion")

        if not codigo_homologado or not placa:
            return jsonify({"error": "Los campos 'codigo_modelo_homologado' y 'placa' son obligatorios"}), 400

        # Validar existencia de modelo homologado
        existe_modelo = db.session.query(ModeloHomologado).filter_by(
            codigo_modelo_homologado=codigo_homologado
        ).first()
        if not existe_modelo:
            return jsonify({"error": "El código de modelo homologado no existe"}), 404

        # Validar placa única (case-insensitive)
        existe_placa = db.session.query(MatriculacionMarca).filter(
            func.upper(MatriculacionMarca.placa) == placa.upper()
        ).first()
        if existe_placa:
            return jsonify({"error": "Ya existe una matrícula con esa placa"}), 409

        nueva = MatriculacionMarca(
            codigo_modelo_homologado=codigo_homologado,
            placa=placa,
            detalle_matriculacion=detalle,
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(nueva)
        db.session.commit()
        db.session.refresh(nueva)

        return jsonify({
            "message": "Matrícula registrada correctamente",
            "codigo_matricula_marca": nueva.codigo_matricula_marca
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_modelo_comercial', methods=["POST"])
@jwt_required()
def insert_modelo_comercial():
    try:
        data = request.json
        user = get_jwt_identity()

        nombre = data.get("nombre_modelo")
        anio = data.get("anio_modelo")
        estado = data.get("estado_modelo")
        marca = data.get("codigo_marca")
        homologado = data.get("codigo_modelo_homologado")

        # Validaciones obligatorias
        if not all([nombre, anio, estado is not None, marca, homologado]):
            return jsonify({"error": "Todos los campos son obligatorios"}), 400
        if not (1950 <= int(anio) <= 2100):
            return jsonify({"error": "El año debe estar entre 1950 y 2100"}), 400
        if estado not in [0, 1]:
            return jsonify({"error": "El estado debe ser 0 o 1"}), 400

        # Validar existencia de marca
        if not db.session.query(Marca).filter_by(codigo_marca=marca).first():
            return jsonify({"error": "La marca no existe"}), 404

        # Validar existencia de modelo homologado
        if not db.session.query(ModeloHomologado).filter_by(codigo_modelo_homologado=homologado).first():
            return jsonify({"error": "El modelo homologado no existe"}), 404

        # Validar unicidad de nombre
        existe = db.session.query(ModeloComercial).filter(
            func.lower(ModeloComercial.nombre_modelo) == nombre.lower()
        ).first()
        if existe:
            return jsonify({"error": "Ya existe un modelo con ese nombre"}), 409

        nuevo = ModeloComercial(
            codigo_marca=marca,
            codigo_modelo_homologado=homologado,
            nombre_modelo=nombre,
            anio_modelo=anio,
            estado_modelo=estado,
            uusuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(nuevo)
        db.session.commit()
        db.session.refresh(nuevo)

        return jsonify({
            "message": "Modelo comercial insertado correctamente",
            "codigo_modelo_comercial": nuevo.codigo_modelo_comercial
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_segmento', methods=["POST"])
@jwt_required()
def insert_segmento():
    try:
        data = request.json
        user = get_jwt_identity()

        nombre = data.get("nombre_segmento")
        estado = data.get("estado_segmento")
        linea = data.get("codigo_linea")
        modelo = data.get("codigo_modelo_comercial")
        marca = data.get("codigo_marca")
        descripcion = data.get("descripcion_segmento")

        if not all([nombre, estado in [0, 1], linea, modelo, marca]):
            return jsonify({"error": "Todos los campos obligatorios deben ser enviados"}), 400

        # Validar claves foráneas
        if not db.session.query(Linea).filter_by(codigo_linea=linea).first():
            return jsonify({"error": "La línea no existe"}), 404

        if not db.session.query(Marca).filter_by(codigo_marca=marca).first():
            return jsonify({"error": "La marca no existe"}), 404

        if not db.session.query(ModeloComercial).filter_by(
            codigo_modelo_comercial=modelo, codigo_marca=marca
        ).first():
            return jsonify({"error": "El modelo comercial no existe para esa marca"}), 404

        existe = db.session.query(Segmento).filter(
            func.lower(Segmento.nombre_segmento) == nombre.lower(),
            Segmento.codigo_modelo_comercial == modelo
        ).first()
        if existe:
            return jsonify({"error": "Ya existe un segmento con ese nombre para ese modelo"}), 409

        nuevo = Segmento(
            codigo_linea=linea,
            codigo_modelo_comercial=modelo,
            codigo_marca=marca,
            nombre_segmento=nombre,
            estado_segmento=estado,
            descripcion_segmento=descripcion,
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(nuevo)
        db.session.commit()
        db.session.refresh(nuevo)

        return jsonify({
            "message": "Segmento insertado correctamente",
            "codigo_segmento": nuevo.codigo_segmento
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_version', methods=["POST"])
@jwt_required()
def insert_version():
    try:
        data = request.json
        user = get_jwt_identity()

        nombre = data.get("nombre_version")
        descripcion = data.get("descripcion_version")
        estado = data.get("estado_version")

        if not nombre or estado not in [0, 1]:
            return jsonify({
                "error": "Los campos 'nombre_version' y 'estado_version' (0 o 1) son obligatorios"
            }), 400

        existe = db.session.query(Version).filter(
            func.lower(Version.nombre_version) == nombre.lower()
        ).first()
        if existe:
            return jsonify({"error": "Ya existe una versión con ese nombre"}), 409

        nueva = Version(
            nombre_version=nombre,
            descripcion_version=descripcion,
            estado_version=estado,
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(nueva)
        db.session.commit()
        db.session.refresh(nueva)

        return jsonify({
            "message": "Versión insertada correctamente",
            "codigo_version": nueva.codigo_version
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_modelo_version_repuesto', methods=["POST"])
@jwt_required()
def insert_modelo_version_repuesto():
    try:
        data = request.json

        required_fields = [
            "codigo_prod_externo", "codigo_version", "empresa", "cod_producto",
            "codigo_modelo_comercial", "codigo_marca", "precio_producto_modelo",
            "precio_venta_distribuidor"
        ]
        if not all(data.get(f) is not None for f in required_fields):
            return jsonify({"error": f"Faltan campos requeridos: {required_fields}"}), 400

        # Validar claves foráneas
        if not db.session.query(ProductoExterno).filter_by(codigo_prod_externo=data["codigo_prod_externo"]).first():
            return jsonify({"error": "Producto externo no existe"}), 404

        if not db.session.query(Version).filter_by(codigo_version=data["codigo_version"]).first():
            return jsonify({"error": "Versión no existe"}), 404

        if not db.session.query(ModeloComercial).filter_by(
            codigo_modelo_comercial=data["codigo_modelo_comercial"],
            codigo_marca=data["codigo_marca"]
        ).first():
            return jsonify({"error": "Modelo comercial no existe para esa marca"}), 404

        if not db.session.query(Producto).filter_by(
            empresa=data["empresa"],
            cod_producto=data["cod_producto"]
        ).first():
            return jsonify({"error": "Producto no existe en esa empresa"}), 404

        nuevo = ModeloVersionRepuesto(
            codigo_prod_externo=data["codigo_prod_externo"],
            codigo_version=data["codigo_version"],
            empresa=data["empresa"],
            cod_producto=data["cod_producto"],
            codigo_modelo_comercial=data["codigo_modelo_comercial"],
            codigo_marca=data["codigo_marca"],
            descripcion=data.get("descripcion"),
            precio_producto_modelo=data["precio_producto_modelo"],
            precio_venta_distribuidor=data["precio_venta_distribuidor"]
        )

        db.session.add(nuevo)
        db.session.commit()
        db.session.refresh(nuevo)

        return jsonify({
            "message": "Repuesto relacionado con versión insertado correctamente",
            "codigo_mod_vers_repuesto": nuevo.codigo_mod_vers_repuesto
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_cliente_canal', methods=["POST"])
@jwt_required()
def insert_cliente_canal():
    try:
        data = request.json

        campos = [
            "codigo_canal", "codigo_mod_vers_repuesto", "empresa",
            "cod_producto", "codigo_modelo_comercial", "codigo_marca"
        ]

        if not all(data.get(c) is not None for c in campos):
            return jsonify({"error": f"Campos requeridos: {campos}"}), 400

        # Validar canal
        canal = db.session.query(Canal).filter_by(codigo_canal=data["codigo_canal"]).first()
        if not canal:
            return jsonify({"error": "El código de canal no existe"}), 404

        # Validar existencia en modelo_version_repuesto
        mvr = db.session.query(ModeloVersionRepuesto).filter_by(
            codigo_mod_vers_repuesto=data["codigo_mod_vers_repuesto"],
            empresa=data["empresa"],
            cod_producto=data["cod_producto"],
            codigo_modelo_comercial=data["codigo_modelo_comercial"],
            codigo_marca=data["codigo_marca"]
        ).first()
        if not mvr:
            return jsonify({"error": "La combinación del modelo de versión y producto no existe"}), 404

        nuevo = ClienteCanal(
            codigo_canal=data["codigo_canal"],
            codigo_mod_vers_repuesto=data["codigo_mod_vers_repuesto"],
            empresa=data["empresa"],
            cod_producto=data["cod_producto"],
            codigo_modelo_comercial=data["codigo_modelo_comercial"],
            codigo_marca=data["codigo_marca"],
            descripcion_cliente_canal=data.get("descripcion_cliente_canal")
        )

        db.session.add(nuevo)
        db.session.commit()
        db.session.refresh(nuevo)

        return jsonify({
            "message": "Cliente canal insertado correctamente",
            "codigo_cliente_canal": nuevo.codigo_cliente_canal
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_modelo_version', methods=["POST"])
@jwt_required()
def insert_modelo_version():
    try:
        data = request.json
        campos_requeridos = [
            "codigo_dim_peso", "codigo_imagen", "codigo_electronica", "codigo_motor", "codigo_tipo_motor",
            "codigo_transmision", "codigo_color_bench", "codigo_chasis",
            "codigo_modelo_comercial", "codigo_marca", "codigo_cliente_canal", "codigo_mod_vers_repuesto",
            "empresa", "cod_producto", "codigo_version",
            "nombre_modelo_version", "anio_modelo_version",
            "precio_producto_modelo", "precio_venta_distribuidor"
        ]
        faltantes = [campo for campo in campos_requeridos if data.get(campo) is None]
        if faltantes:
            return jsonify({"error": f"Faltan campos obligatorios: {faltantes}"}), 400

        if not (1950 <= int(data["anio_modelo_version"]) <= 2100):
            return jsonify({"error": "Año de modelo fuera de rango (1950-2100)"}), 400

        nombre_existente = db.session.query(ModeloVersion).filter(
            func.lower(ModeloVersion.nombre_modelo_version) == data["nombre_modelo_version"].lower()
        ).first()
        if nombre_existente:
            return jsonify({"error": "Ya existe un modelo con ese nombre"}), 409

        def validar_existencia(model, **kwargs):
            return db.session.query(model).filter_by(**kwargs).first() is not None

        if not validar_existencia(DimensionPeso, codigo_dim_peso=data["codigo_dim_peso"]): return jsonify(
            {"error": "Dimensión/peso no encontrado"}), 404
        if not validar_existencia(Imagenes, codigo_imagen=data["codigo_imagen"]): return jsonify(
            {"error": "Imagen no encontrada"}), 404
        if not validar_existencia(ElectronicaOtros, codigo_electronica=data["codigo_electronica"]): return jsonify(
            {"error": "Electrónica no encontrada"}), 404
        if not validar_existencia(Motor, codigo_motor=data["codigo_motor"],
                                  codigo_tipo_motor=data["codigo_tipo_motor"]): return jsonify(
            {"error": "Motor/tipo no encontrado"}), 404
        if not validar_existencia(Transmision, codigo_transmision=data["codigo_transmision"]): return jsonify(
            {"error": "Transmisión no encontrada"}), 404
        if not validar_existencia(Color, codigo_color_bench=data["codigo_color_bench"]): return jsonify(
            {"error": "Color no encontrado"}), 404
        if not validar_existencia(Chasis, codigo_chasis=data["codigo_chasis"]): return jsonify(
            {"error": "Chasis no encontrado"}), 404
        if not validar_existencia(Version, codigo_version=data["codigo_version"]): return jsonify(
            {"error": "Versión no encontrada"}), 404
        if not validar_existencia(ModeloComercial, codigo_modelo_comercial=data["codigo_modelo_comercial"],
                                  codigo_marca=data["codigo_marca"]): return jsonify(
            {"error": "Modelo comercial no válido"}), 404

        if not validar_existencia(
                ClienteCanal,
                codigo_cliente_canal=data["codigo_cliente_canal"],
                codigo_mod_vers_repuesto=data["codigo_mod_vers_repuesto"],
                empresa=data["empresa"],
                cod_producto=data["cod_producto"],
                codigo_modelo_comercial=data["codigo_modelo_comercial"],
                codigo_marca=data["codigo_marca"]
        ):
            return jsonify({"error": "Cliente-canal no válido"}), 404
        nuevo = ModeloVersion(
            codigo_dim_peso=data["codigo_dim_peso"],
            codigo_imagen=data["codigo_imagen"],
            codigo_electronica=data["codigo_electronica"],
            codigo_motor=data["codigo_motor"],
            codigo_tipo_motor=data["codigo_tipo_motor"],
            codigo_transmision=data["codigo_transmision"],
            codigo_color_bench=data["codigo_color_bench"],
            codigo_chasis=data["codigo_chasis"],
            codigo_modelo_comercial=data["codigo_modelo_comercial"],
            codigo_marca=data["codigo_marca"],
            codigo_cliente_canal=data["codigo_cliente_canal"],
            codigo_mod_vers_repuesto=data["codigo_mod_vers_repuesto"],
            empresa=data["empresa"],
            cod_producto=data["cod_producto"],
            codigo_version=data["codigo_version"],
            nombre_modelo_version=data["nombre_modelo_version"],
            anio_modelo_version=data["anio_modelo_version"],
            precio_producto_modelo=data["precio_producto_modelo"],
            precio_venta_distribuidor=data["precio_venta_distribuidor"]
        )

        db.session.add(nuevo)
        db.session.commit()
        db.session.refresh(nuevo)

        return jsonify({
            "message": "Modelo versión insertado correctamente",
            "codigo_modelo_version": nuevo.codigo_modelo_version
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#Repuestos compatibles con un modelo externo

@bench.route("/modelo_version/repuestos_compatibles", methods=["GET"])
@jwt_required()
def get_repuestos_by_nombre():
    try:
        nombre = request.args.get("nombre")
        if not nombre:
            return jsonify({"error": "Parámetro 'nombre' es requerido"}), 400

        mv = ModeloVersion
        cc = ClienteCanal
        mvr = ModeloVersionRepuesto
        pe = ProductoExterno
        mr = MarcaRepuesto

        resultado = db.session.query(
            pe.nombre_producto.label("nombre_repuesto"),
            pe.descripcion_producto,
            mvr.precio_producto_modelo,
            mvr.precio_venta_distribuidor,
            mr.nombre_comercial.label("marca_repuesto"),
            mv.nombre_modelo_version.label("modelo")
        ).select_from(mv).join(
            cc,
            (mv.codigo_cliente_canal == cc.codigo_cliente_canal) &
            (mv.codigo_mod_vers_repuesto == cc.codigo_mod_vers_repuesto) &
            (mv.empresa == cc.empresa) &
            (mv.cod_producto == cc.cod_producto) &
            (mv.codigo_modelo_comercial == cc.codigo_modelo_comercial) &
            (mv.codigo_marca == cc.codigo_marca)
        ).join(
            mvr,
            (cc.codigo_mod_vers_repuesto == mvr.codigo_mod_vers_repuesto) &
            (cc.empresa == mvr.empresa) &
            (cc.cod_producto == mvr.cod_producto) &
            (cc.codigo_modelo_comercial == mvr.codigo_modelo_comercial) &
            (cc.codigo_marca == mvr.codigo_marca)
        ).join(
            pe,
            pe.codigo_prod_externo == mvr.codigo_prod_externo
        ).join(
            mr,
            mr.codigo_marca_rep == pe.codigo_marca_rep
        ).filter(
            func.lower(mv.nombre_modelo_version).like(f"%{nombre.lower()}%")
        ).all()

        return jsonify([dict(row._mapping) for row in resultado])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Carga de archivos desde un Excel ---->

ALLOWED_EXTENSIONS = {'xlsx'}
UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_or_create(model, defaults=None, **kwargs):
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        params = dict((k, v) for k, v in kwargs.items())
        if defaults:
            params.update(defaults)
        instance = model(**params)
        db.session.add(instance)
        db.session.flush()
        return instance

#METODOS GET CATALOGO BENCH

@bench.route('/get_chasis', methods=["GET"])
@jwt_required()
def get_chasis():
    try:
        chasis_list = db.session.query(Chasis).all()

        resultado = []
        for ch in chasis_list:
            resultado.append({
                "codigo_chasis": ch.codigo_chasis,
                "aros_rueda_posterior": ch.aros_rueda_posterior,
                "neumatico_delantero": ch.neumatico_delantero,
                "neumatico_trasero": ch.neumatico_trasero,
                "suspension_delantera": ch.suspension_delantera,
                "suspension_trasera": ch.suspension_trasera,
                "frenos_delanteros": ch.frenos_delanteros,
                "frenos_traseros": ch.frenos_traseros,
                "aros_rueda_delantera": ch.aros_rueda_delantera,
                "usuario_crea": ch.usuario_crea,
                "usuario_modifica": ch.usuario_modifica,
                "fecha_creacion": ch.fecha_creacion.isoformat() if ch.fecha_creacion else None,
                "fecha_modificacion": ch.fecha_modificacion.isoformat() if ch.fecha_modificacion else None
            })

        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bench.route('/get_dimensiones', methods=["GET"])
@jwt_required()
def get_dimensiones():
    try:
        dimensiones = db.session.query(DimensionPeso).all()

        resultado = []
        for dim in dimensiones:
            resultado.append({
                "codigo_dim_peso": dim.codigo_dim_peso,
                "altura_total": dim.altura_total,
                "longitud_total": dim.longitud_total,
                "ancho_total": dim.ancho_total,
                "peso_seco": dim.peso_seco,
                "usuario_crea": dim.usuario_crea,
                "usuario_modifica": dim.usuario_modifica,
                "fecha_creacion": dim.fecha_creacion.isoformat() if dim.fecha_creacion else None,
                "fecha_modificacion": dim.fecha_modificacion.isoformat() if dim.fecha_modificacion else None
            })

        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bench.route('/get_electronica', methods=["GET"])
@jwt_required()
def get_electronica():
    try:
        electronica = db.session.query(ElectronicaOtros).all()

        resultado = []
        for elect in electronica:
            resultado.append({
                "codigo_electronica": elect.codigo_electronica,
                "capacidad_combustible": elect.capacidad_combustible,
                "tablero": elect.tablero,
                "luces_delanteras": elect.luces_delanteras,
                "luces_posteriores": elect.luces_posteriores,
                "garantia": elect.garantia,
                "velocidad_maxima": elect.velocidad_maxima,
                "usuario_crea": elect.usuario_crea,
                "usuario_modifica": elect.usuario_modifica,
                "fecha_creacion": elect.fecha_creacion.isoformat() if elect.fecha_creacion else None,
                "fecha_modificacion": elect.fecha_modificacion.isoformat() if elect.fecha_modificacion else None
            })

        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bench.route('/get_tipo_motor', methods=["GET"])
@jwt_required()
def get_tipo_motor():
    try:
        tipo_motor = db.session.query(TipoMotor).all()

        resultado = []
        for tipo in tipo_motor:
            resultado.append({
                "codigo_tipo_motor": tipo.codigo_tipo_motor,
                "nombre_tipo": tipo.nombre_tipo,
                "descripcion_tipo_motor": tipo.descripcion_tipo_motor
            })

        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bench.route('/get_motores', methods=["GET"])
@jwt_required()
def get_motores():
    try:
        motores = db.session.query(Motor).all()

        resultado = []
        for m in motores:
            resultado.append({
                "codigo_motor": m.codigo_motor,
                "codigo_tipo_motor": m.codigo_tipo_motor,
                "nombre_tipo_motor": m.tipo_motor.nombre_tipo if m.tipo_motor else None,
                "nombre_motor": m.nombre_motor,
                "cilindrada": m.cilindrada,
                "caballos_fuerza": m.caballos_fuerza,
                "torque_maximo": m.torque_maximo,
                "sistema_combustible": m.sistema_combustible,
                "arranque": m.arranque,
                "sistema_refrigeracion": m.sistema_refrigeracion,
                "descripcion_motor": m.descripcion_motor,
                "usuario_crea": m.usuario_crea,
                "usuario_modifica": m.usuario_modifica,
                "fecha_creacion": m.fecha_creacion.isoformat() if m.fecha_creacion else None,
                "fecha_modificacion": m.fecha_modificacion.isoformat() if m.fecha_modificacion else None
            })

        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bench.route('/get_color', methods=["GET"])
@jwt_required()
def get_color():
    try:
        color = db.session.query(Color).all()

        resultado = []
        for c in color:
            resultado.append({
                "codigo_color_bench": c.codigo_color_bench,
                "nombre_color": c.nombre_color,
                "usuario_crea": c.usuario_crea,
                "usuario_modifica": c.usuario_modifica,
                "fecha_creacion": c.fecha_creacion.isoformat() if c.fecha_creacion else None,
                "fecha_modificacion": c.fecha_modificacion.isoformat() if c.fecha_modificacion else None
            })

        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ACTUALIZAR/ MODIFICAR DATOS

@bench.route('/update_chasis/<int:codigo_chasis>', methods=["PUT"])
@jwt_required()
def update_chasis(codigo_chasis):
    try:
        data = request.json
        user = get_jwt_identity()

        chasis = db.session.query(Chasis).filter_by(codigo_chasis=codigo_chasis).first()
        if not chasis:
            return jsonify({"error": "Chasis no encontrado"}), 404

        chasis.aros_rueda_posterior = data.get("aros_rueda_posterior", chasis.aros_rueda_posterior)
        chasis.neumatico_delantero = data.get("neumatico_delantero", chasis.neumatico_delantero)
        chasis.neumatico_trasero = data.get("neumatico_trasero", chasis.neumatico_trasero)
        chasis.suspension_delantera = data.get("suspension_delantera", chasis.suspension_delantera)
        chasis.suspension_trasera = data.get("suspension_trasera", chasis.suspension_trasera)
        chasis.frenos_delanteros = data.get("frenos_delanteros", chasis.frenos_delanteros)
        chasis.frenos_traseros = data.get("frenos_traseros", chasis.frenos_traseros)
        chasis.aros_rueda_delantera = data.get("aros_rueda_delantera", chasis.aros_rueda_delantera)
        chasis.usuario_modifica = user
        chasis.fecha_modificacion = datetime.now()

        db.session.commit()
        return jsonify({"message": "Chasis actualizado correctamente", "codigo_chasis": chasis.codigo_chasis})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/update_dimensiones/<int:codigo_dim_peso>', methods=["PUT"])
@jwt_required()
def update_dimensiones(codigo_dim_peso):
    try:
        def normalize_float(value):
            if isinstance(value, str):
                value = value.strip()
            return float(value) if value not in (None, '', ' ') else None

        data = request.json
        user = get_jwt_identity()

        dimension = db.session.query(DimensionPeso).filter_by(codigo_dim_peso=codigo_dim_peso).first()
        if not dimension:
            return jsonify({"error": "Registro no encontrado"}), 404

        dimension.altura_total = normalize_float(data.get("altura_total"))
        dimension.longitud_total = normalize_float(data.get("longitud_total"))
        dimension.ancho_total = normalize_float(data.get("ancho_total"))
        dimension.peso_seco = normalize_float(data.get("peso_seco"))
        dimension.usuario_modifica = user
        dimension.fecha_modificacion = datetime.now()

        db.session.commit()
        return jsonify({"message": "Dimensión/Peso actualizado correctamente", "codigo_dim_peso": dimension.codigo_dim_peso})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bench.route('/update_electronica/<int:codigo_electronica>', methods=["PUT"])
@jwt_required()
def update_electronica_otros(codigo):
    try:
        user = get_jwt_identity()
        data = request.json

        def normalize(value):
            return (value or '').strip().lower()

        registro = db.session.query(ElectronicaOtros).get(codigo)
        if not registro:
            return jsonify({"error": "Registro no encontrado"}), 404

        # Verificar si los nuevos datos duplican otro registro existente
        with db.session.no_autoflush:
            duplicado = db.session.query(ElectronicaOtros).filter(
                func.lower(func.trim(ElectronicaOtros.capacidad_combustible)) == normalize(data.get("capacidad_combustible")),
                func.lower(func.trim(ElectronicaOtros.tablero)) == normalize(data.get("tablero")),
                func.lower(func.trim(ElectronicaOtros.luces_delanteras)) == normalize(data.get("luces_delanteras")),
                func.lower(func.trim(ElectronicaOtros.luces_posteriores)) == normalize(data.get("luces_posteriores")),
                func.lower(func.trim(ElectronicaOtros.garantia)) == normalize(data.get("garantia")),
                func.lower(func.trim(ElectronicaOtros.velocidad_maxima)) == normalize(data.get("velocidad_maxima")),
                ElectronicaOtros.codigo_electronica != codigo
            ).first()

        if duplicado:
            return jsonify({"error": "Ya existe un registro con los mismos datos"}), 409

        # Actualizar campos
        registro.capacidad_combustible = data.get("capacidad_combustible")
        registro.tablero = data.get("tablero")
        registro.luces_delanteras = data.get("luces_delanteras")
        registro.luces_posteriores = data.get("luces_posteriores")
        registro.garantia = data.get("garantia")
        registro.velocidad_maxima = data.get("velocidad_maxima")
        registro.usuario_modifica = user
        registro.fecha_modificacion = datetime.now()

        db.session.commit()
        return jsonify({"message": "Registro actualizado correctamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/update_motor/<int:codigo_motor>', methods=["PUT"])
@jwt_required()
def update_motor(codigo_motor):
    try:
        data = request.get_json()
        user = get_jwt_identity()

        motor = db.session.query(Motor).filter_by(codigo_motor=codigo_motor).first()
        if not motor:
            return jsonify({"error": "Motor no encontrado"}), 404

        motor.codigo_tipo_motor = data.get("codigo_tipo_motor", motor.codigo_tipo_motor)
        motor.nombre_motor = data.get("nombre_motor", motor.nombre_motor)
        motor.cilindrada = data.get("cilindrada", motor.cilindrada)
        motor.caballos_fuerza = data.get("caballos_fuerza", motor.caballos_fuerza)
        motor.torque_maximo = data.get("torque_maximo", motor.torque_maximo)
        motor.sistema_combustible = data.get("sistema_combustible", motor.sistema_combustible)
        motor.arranque = data.get("arranque", motor.arranque)
        motor.sistema_refrigeracion = data.get("sistema_refrigeracion", motor.sistema_refrigeracion)
        motor.descripcion_motor = data.get("descripcion_motor", motor.descripcion_motor)

        motor.usuario_modifica = user
        motor.fecha_modificacion = datetime.now()

        db.session.commit()
        return jsonify({"message": "Motor actualizado correctamente", "codigo_motor": motor.codigo_motor})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/update_color/<int:codigo_color_bench>', methods=["PUT"])
@jwt_required()
def update_color(codigo_color_bench):
    try:
        data = request.json
        user = get_jwt_identity()

        color = db.session.query(Color).filter_by(codigo_color_bench=codigo_color_bench).first()
        if not color:
            return jsonify({"error": "Datos de color no encontrados"}), 404

        color.nombre_color = data.get("nombre_color", color.nombre_color)
        color.usuario_modifica = user
        color.fecha_modificacion = datetime.now()

        db.session.commit()
        return jsonify({"message": "Datos de color actualizados correctamente", "codigo_color_bench": color.codigo_color_bench})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# registros masivos mediante plantilla excel
@bench.route('/upload_chasis_excel', methods=['POST'])
@jwt_required()
def upload_chasis_excel():
    try:
        user = get_jwt_identity()

        if 'file' not in request.files:
            return jsonify({'error': 'Archivo no enviado'}), 400

        file = request.files['file']
        df = pd.read_excel(file)

        required_columns = [
            'aros_rueda_delantera', 'aros_rueda_posterior',
            'neumatico_delantero', 'neumatico_trasero',
            'suspension_delantera', 'suspension_trasera',
            'frenos_delanteros', 'frenos_traseros'
        ]

        for col in required_columns:
            if col not in df.columns:
                return jsonify({'error': f'Falta la columna requerida: {col}'}), 400

        inserted = 0
        for _, row in df.iterrows():
            nuevo = Chasis(
                aros_rueda_delantera=row['aros_rueda_delantera'],
                aros_rueda_posterior=row['aros_rueda_posterior'],
                neumatico_delantero=row['neumatico_delantero'],
                neumatico_trasero=row['neumatico_trasero'],
                suspension_delantera=row['suspension_delantera'],
                suspension_trasera=row['suspension_trasera'],
                frenos_delanteros=row['frenos_delanteros'],
                frenos_traseros=row['frenos_traseros'],
                usuario_crea=user,
                fecha_creacion=datetime.now()
            )
            db.session.add(nuevo)
            inserted += 1

        db.session.commit()
        return jsonify({'message': f'{inserted} registros insertados correctamente'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bench.route('/upload_color_excel', methods=['POST'])
@jwt_required()
def upload_color_excel():
    try:
        user = get_jwt_identity()

        if 'file' not in request.files:
            return jsonify({'error': 'Archivo no enviado'}), 400

        file = request.files['file']
        df = pd.read_excel(file)

        required_columns = [
            'nombre_color'
        ]

        for col in required_columns:
            if col not in df.columns:
                return jsonify({'error': f'Falta la columna requerida: {col}'}), 400

        inserted = 0
        for _, row in df.iterrows():
            nuevo = Color(
                nombre_color=row['nombre_color'],
                usuario_crea=user,
                fecha_creacion=datetime.now()
            )
            db.session.add(nuevo)
            inserted += 1

        db.session.commit()
        return jsonify({'message': f'{inserted} registros insertados correctamente'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bench.route('/upload_dimension_excel', methods=['POST'])
@jwt_required()
def upload_dimension_excel():
    try:
        user = get_jwt_identity()

        if 'file' not in request.files:
            return jsonify({'error': 'Archivo no enviado'}), 400

        file = request.files['file']
        df = pd.read_excel(file)

        required_columns = [
            'altura_total', 'longitud_total', 'ancho_total','peso_seco'
        ]

        for col in required_columns:
            if col not in df.columns:
                return jsonify({'error': f'Falta la columna requerida: {col}'}), 400

        inserted = 0
        for _, row in df.iterrows():
            nuevo = DimensionPeso(
                altura_total=row['altura_total'],
                longitud_total=row['longitud_total'],
                ancho_total=row['ancho_total'],
                peso_seco=row['peso_seco'],
                usuario_crea=user,
                fecha_creacion=datetime.now()
            )
            db.session.add(nuevo)
            inserted += 1

        db.session.commit()
        return jsonify({'message': f'{inserted} registros insertados correctamente'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bench.route('/upload_electronica_excel', methods=['POST'])
@jwt_required()
def upload_electronica_excel():
    try:
        user = get_jwt_identity()

        if 'file' not in request.files:
            return jsonify({'error': 'Archivo no enviado'}), 400

        file = request.files['file']
        df = pd.read_excel(file)

        required_columns = [
            'capacidad_combustible', 'tablero', 'luces_delanteras','luces_posteriores',
            'garantia', 'velocidad_maxima'
        ]

        for col in required_columns:
            if col not in df.columns:
                return jsonify({'error': f'Falta la columna requerida: {col}'}), 400

        inserted = 0
        for _, row in df.iterrows():
            nuevo = ElectronicaOtros(
                capacidad_combustible=row['capacidad_combustible'],
                tablero=row['tablero'],
                luces_delanteras=row['luces_delanteras'],
                luces_posteriores=row['luces_posteriores'],
                garantia=row['garantia'],
                velocidad_maxima=row['velocidad_maxima'],
                usuario_crea=user,
                fecha_creacion=datetime.now()
            )
            db.session.add(nuevo)
            inserted += 1

        db.session.commit()
        return jsonify({'message': f'{inserted} registros insertados correctamente'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bench.route('/upload_motor_excel', methods=['POST'])
@jwt_required()
def upload_motor_excel():
    try:
        user = get_jwt_identity()

        if 'file' not in request.files:
            return jsonify({'error': 'Archivo no enviado'}), 400

        file = request.files['file']
        df = pd.read_excel(file)

        required_columns = [
            'tipo_motor_nombre', 'nombre_motor', 'cilindrada', 'caballos_fuerza',
            'torque_maximo', 'sistema_combustible', 'arranque',
            'sistema_refrigeracion', 'descripcion_motor'
        ]

        for col in required_columns:
            if col not in df.columns:
                return jsonify({'error': f'Falta la columna requerida: {col}'}), 400

        from unidecode import unidecode

        def normalize(value):
            return unidecode(str(value).strip().lower()) if value else ""

        insertados = 0
        duplicados = []

        for _, row in df.iterrows():
            tipo_motor_nombre = normalize(row['tipo_motor_nombre'])
            tipo_motor = db.session.query(TipoMotor).filter(
                func.lower(func.replace(TipoMotor.nombre_tipo, 'á', 'a')) == tipo_motor_nombre
            ).first()

            if not tipo_motor:
                duplicados.append({'error': 'Tipo de motor no encontrado', 'row': row.to_dict()})
                continue

            existe = db.session.query(Motor).filter(
                func.lower(Motor.nombre_motor) == normalize(row['nombre_motor']),
                func.lower(Motor.cilindrada) == normalize(row['cilindrada']),
                func.lower(Motor.caballos_fuerza) == normalize(row['caballos_fuerza']),
                func.lower(Motor.torque_maximo) == normalize(row['torque_maximo']),
                func.lower(Motor.sistema_combustible) == normalize(row['sistema_combustible']),
                func.lower(Motor.arranque) == normalize(row['arranque']),
                func.lower(Motor.sistema_refrigeracion) == normalize(row['sistema_refrigeracion']),
                func.lower(Motor.descripcion_motor) == normalize(row['descripcion_motor']),
                Motor.codigo_tipo_motor == tipo_motor.codigo_tipo_motor
            ).first()

            if existe:
                duplicados.append(row.to_dict())
                continue

            nuevo = Motor(
                nombre_motor=row['nombre_motor'],
                cilindrada=row['cilindrada'],
                caballos_fuerza=row['caballos_fuerza'],
                torque_maximo=row['torque_maximo'],
                sistema_combustible=row['sistema_combustible'],
                arranque=row['arranque'],
                sistema_refrigeracion=row['sistema_refrigeracion'],
                descripcion_motor=row['descripcion_motor'],
                codigo_tipo_motor=tipo_motor.codigo_tipo_motor,
                usuario_crea=user,
                fecha_creacion=datetime.now()
            )

            db.session.add(nuevo)
            insertados += 1

        db.session.commit()

        if insertados == 0:
            return jsonify({
                "error": "Todos los registros ya existen. No se insertó ninguno",
                "omitidos": len(duplicados)
            }), 409

        return jsonify({
            "message": f"{insertados} registro(s) insertado(s). {len(duplicados)} duplicado(s) omitido(s).",
            "omitidos": len(duplicados)
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
