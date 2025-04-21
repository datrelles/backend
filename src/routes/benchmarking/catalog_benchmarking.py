import logging
import os
from datetime import datetime

import pandas as pd

from flask import request, Blueprint, jsonify
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, and_, text
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from src.config.database import db
from src.models.catalogos_bench import Chasis, DimensionPeso, ElectronicaOtros, Transmision, Imagenes, TipoMotor, Motor, \
    Color, Canal, MarcaRepuesto, ProductoExterno, Linea, Marca, ModeloSRI, ModeloHomologado, MatriculacionMarca, \
    ModeloComercial, Segmento, Version, ModeloVersionRepuesto, ClienteCanal, ModeloVersion, Benchmarking
from src.models.productos import Producto

bench = Blueprint('routes_bench', __name__)
logger = logging.getLogger(__name__)

@bench.route('/insert_chasis', methods=["POST"])
@jwt_required()
@cross_origin()
def insert_chasis():
    try:
        data = request.json
        user = get_jwt_identity()

        nuevo = Chasis(
            aros_rueda_posterior=data.get("aros_rueda_posterior"),
            neumatico_delantero=data.get("neumatico_delantero"),
            neumatico_trasero=data.get("neumatico_trasero"),
            suspension_delantera=data.get("suspension_delantera"),
            suspension_trasera=data.get("suspension_trasera"),
            frenos_delanteros=data.get("frenos_delanteros"),
            frenos_traseros=data.get("frenos_traseros"),
            aros_rueda_delantera=data.get("aros_rueda_delantera"),
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(nuevo)
        db.session.commit()
        return jsonify({"message": "Chasis insertado correctamente", "codigo_chasis": nuevo.codigo_chasis})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_dimension', methods=["POST"])
@jwt_required()
def insert_dimension():
    try:
        data = request.json
        user = get_jwt_identity()

        nuevo = DimensionPeso(
            altura_total=data.get("altura_total"),
            longitud_total=data.get("longitud_total"),
            ancho_total=data.get("ancho_total"),
            peso_seco=data.get("peso_seco"),
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(nuevo)
        db.session.commit()
        db.session.refresh(nuevo)
        return jsonify({"message": "Dimensión/Peso insertado", "codigo_dim_peso": nuevo.codigo_dim_peso})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_electronica_otros', methods=["POST"])
@jwt_required()
def insert_electronica_otros():
    try:
        data = request.json
        user = get_jwt_identity()

        nuevo = ElectronicaOtros(
            capacidad_combustible=data.get("capacidad_combustible"),
            tablero=data.get("tablero"),
            luces_delanteras=data.get("luces_delanteras"),
            luces_posteriores=data.get("luces_posteriores"),
            garantia=data.get("garantia"),
            velocidad_maxima=data.get("velocidad_maxima"),
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(nuevo)
        db.session.commit()
        db.session.refresh(nuevo)
        return jsonify({"message": "Elementos de electronica/otros insertados", "codigo_electronica": nuevo.codigo_electronica})

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

@bench.route('/insert_color', methods=["POST"])
@jwt_required()
def insert_color():
    try:
        data = request.json
        user = get_jwt_identity()

        nombre_color = data.get("nombre_color")
        if not nombre_color:
            return jsonify({"error": "El nombre del color es obligatorio"}), 400

        nombre_existe = db.session.query(Color).filter(
            func.lower(Color.nombre_color) == nombre_color.lower()
        ).first()

        if nombre_existe:
            return jsonify({"error": "Este color ya existe"}), 409

        nuevo = Color(
            nombre_color=nombre_color,
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(nuevo)
        db.session.commit()
        db.session.refresh(nuevo)

        return jsonify({"message": "Color insertado correctamente", "codigo_color": nuevo.codigo_color_bench})

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
        user = get_jwt_identity()

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
        user = get_jwt_identity()

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

#Carga de archivos desde un Excel ----> aun no está :(

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

@bench.route('/upload_modelos_internos', methods=['POST'])
@jwt_required()
def upload_modelos_internos():
    user = get_jwt_identity()

    if 'file' not in request.files:
        return jsonify({"error": "Archivo no enviado"}), 400
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Nombre de archivo vacío"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        try:
            df = pd.read_excel(filepath)
            errores = []

            for index, row in df.iterrows():
                try:
                    row = row.where(pd.notnull(row), None)

                    marca = get_or_create(Marca,
                        nombre_marca=row['marca'],
                        defaults={"estado_marca": 1, "usuario_crea": user}
                    )
                    tipo_motor = get_or_create(TipoMotor,
                        nombre_tipo=row['tipo_motor']
                    )
                    motor = db.session.query(Motor).filter_by(
                        nombre_motor=row['nombre_motor']
                    ).first()
                    if not motor:
                        motor = Motor(
                            nombre_motor=row['nombre_motor'],
                            codigo_tipo_motor=tipo_motor.codigo_tipo_motor,
                            cilindrada=row['cilindrada'],
                            caballos_fuerza=row['caballos_fuerza'],
                            torque_maximo=row['torque_maximo'],
                            sistema_combustible=row['sistema_combustible'],
                            arranque=row['arranque'],
                            sistema_refrigeracion=row['sistema_refrigeracion'],
                            usuario_crea=user
                        )
                        db.session.add(motor)
                        db.session.flush()

                    transmision = get_or_create(Transmision,
                        caja_cambios=row['caja_cambios'],
                        defaults={"usuario_crea": user}
                    )
                    chasis = get_or_create(Chasis,
                        aros_rueda_delantera=row['aros_rueda_delantera'],
                        suspension_delantera=row['suspension_delantera'],
                        neumatico_delantero=row['neumatico_delantero'],
                        aros_rueda_posterior=row['aros_rueda_posterior'],
                        suspension_trasera=row['suspension_trasera'],
                        neumatico_trasero=row['neumatico_trasero'],
                        frenos_delanteros=row['frenos_delanteros'],
                        frenos_traseros=row['frenos_traseros'],
                        defaults={"usuario_crea": user}
                    )
                    dimension = get_or_create(DimensionPeso,
                        altura_total=row['altura_total'],
                        longitud_total=row['longitud_total'],
                        ancho_total=row['ancho_total'],
                        peso_seco=row['peso_seco'],
                        defaults={"usuario_crea": user}
                    )
                    electronica = get_or_create(ElectronicaOtros,
                        capacidad_combustible=row['capacidad_combustible'],
                        tablero=row['tablero'],
                        luces_delanteras=row['luces_delanteras'],
                        luces_posteriores=row['luces_posteriores'],
                        garantia=row['garantia'],
                        velocidad_maxima=row['velocidad_maxima'],
                        defaults={"usuario_crea": user}
                    )
                    color = get_or_create(Color,
                        nombre_color=row['colores_disponibles'],
                        defaults={"usuario_crea": user}
                    )
                    modelo_comercial = get_or_create(ModeloComercial,
                        nombre_modelo=row['nombre_modelo_version'],
                        codigo_marca=marca.codigo_marca,
                        defaults={
                            "anio_modelo": 2025,
                            "estado_modelo": 1,
                            "codigo_modelo_homologado": 1,
                            "usuario_crea": user
                        }
                    )
                    version = get_or_create(Version,
                        nombre_version=row['nombre_modelo_version'],
                        defaults={"estado_version": 1, "usuario_crea": user}
                    )
                    # aseguramos máximo 14 caracteres para codigo_prod_externo
                    codigo_ext = ('I_' + row['nombre_modelo_version'].replace(" ", "_")).upper()[:14]

                    producto_externo = db.session.query(ProductoExterno).filter_by(
                        codigo_prod_externo=codigo_ext
                    ).first()
                    if not producto_externo:
                        producto_externo = ProductoExterno(
                            codigo_prod_externo=codigo_ext,
                            codigo_marca_rep=1,
                            nombre_producto=row['nombre_modelo_version'],
                            estado_prod_externo=1,
                            descripcion_producto="Repuesto interno generado automáticamente",
                            usuario_crea=user,
                            empresa=20
                        )
                        db.session.add(producto_externo)
                        db.session.flush()

                    modelo_version_repuesto = db.session.query(ModeloVersionRepuesto).filter_by(
                        codigo_version=version.codigo_version,
                        codigo_modelo_comercial=modelo_comercial.codigo_modelo_comercial,
                        codigo_marca=marca.codigo_marca,
                        cod_producto=row['nombre_modelo_version'],
                        empresa=20
                    ).first()

                    if not modelo_version_repuesto:
                        modelo_version_repuesto = ModeloVersionRepuesto(
                            codigo_prod_externo=codigo_ext,
                            codigo_version=version.codigo_version,
                            empresa=20,
                            cod_producto=row['nombre_modelo_version'],
                            codigo_modelo_comercial=modelo_comercial.codigo_modelo_comercial,
                            codigo_marca=marca.codigo_marca,
                            descripcion='Repuesto interno autogenerado',
                            precio_producto_modelo=0,
                            precio_venta_distribuidor=0
                        )
                        db.session.add(modelo_version_repuesto)
                        db.session.flush()

                    cliente_canal = db.session.query(ClienteCanal).filter_by(
                        codigo_mod_vers_repuesto=modelo_version_repuesto.codigo_mod_vers_repuesto,
                        empresa=20,
                        cod_producto=row['nombre_modelo_version'],
                        codigo_modelo_comercial=modelo_comercial.codigo_modelo_comercial,
                        codigo_marca=marca.codigo_marca
                    ).first()

                    if not cliente_canal:
                        cliente_canal = ClienteCanal(
                            codigo_canal=1,
                            codigo_mod_vers_repuesto=modelo_version_repuesto.codigo_mod_vers_repuesto,
                            empresa=20,
                            cod_producto=row['nombre_modelo_version'],
                            codigo_modelo_comercial=modelo_comercial.codigo_modelo_comercial,
                            codigo_marca=marca.codigo_marca,
                            descripcion_cliente_canal="Autogenerado en carga de modelo interno"
                        )
                        db.session.add(cliente_canal)
                        db.session.flush()

                    modelo_version = ModeloVersion(
                        nombre_modelo_version=row['nombre_modelo_version'],
                        codigo_modelo_comercial=modelo_comercial.codigo_modelo_comercial,
                        codigo_marca=marca.codigo_marca,
                        codigo_version=version.codigo_version,
                        codigo_motor=motor.codigo_motor,
                        codigo_tipo_motor=tipo_motor.codigo_tipo_motor,
                        codigo_transmision=transmision.codigo_transmision,
                        codigo_chasis=chasis.codigo_chasis,
                        codigo_color_bench=color.codigo_color_bench,
                        codigo_dim_peso=dimension.codigo_dim_peso,
                        codigo_electronica=electronica.codigo_electronica,
                        codigo_imagen=1,
                        cod_producto=row['nombre_modelo_version'],
                        empresa=20,
                        codigo_cliente_canal=cliente_canal.codigo_cliente_canal,
                        codigo_mod_vers_repuesto=modelo_version_repuesto.codigo_mod_vers_repuesto,
                        anio_modelo_version=2025,
                        precio_producto_modelo=0,
                        precio_venta_distribuidor=0
                    )
                    db.session.add(modelo_version)
                except Exception as row_error:
                    errores.append({"fila": index + 2, "error": str(row_error)})
                    db.session.rollback()

            db.session.commit()

            if errores:
                return jsonify({"message": "Carga completada con errores", "detalles": errores}), 207
            return jsonify({"message": "Carga de modelos internos completada exitosamente"})
        except Exception as e:
            return jsonify({"error": f"Error procesando archivo: {str(e)}"}), 500
    return jsonify({"error": "Extensión de archivo no permitida"}), 400


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
        data = request.json
        user = get_jwt_identity()

        dimensiones = db.session.query(DimensionPeso).filter_by(codigo_dim_peso=codigo_dim_peso).first()
        if not dimensiones:
            return jsonify({"error": "Dimensiones y peso no encontrados"}), 404

        dimensiones.altura_total = data.get("altura_total", dimensiones.altura_total)
        dimensiones.longitud_total = data.get("longitud_total", dimensiones.longitud_total)
        dimensiones.ancho_total = data.get("ancho_total", dimensiones.ancho_total)
        dimensiones.peso_seco = data.get("peso_seco", dimensiones.peso_seco)
        dimensiones.usuario_modifica = user
        dimensiones.fecha_modificacion = datetime.now()

        db.session.commit()
        return jsonify({"message": "Dimensiones y peso actualizados correctamente", "codigo_dim_peso": dimensiones.codigo_dim_peso})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500