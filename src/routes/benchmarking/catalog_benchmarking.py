import logging
import os
from datetime import datetime

import unicodedata
from flask import request, Blueprint, jsonify
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased

from src.config.database import db
from src.models.catalogos_bench import Chasis, DimensionPeso, ElectronicaOtros, Transmision, Imagenes, TipoMotor, Motor, \
    Color, Canal, MarcaRepuesto, ProductoExterno, Linea, Marca, ModeloSRI, ModeloHomologado, MatriculacionMarca, \
    ModeloComercial, Segmento, Version, ModeloVersionRepuesto, ClienteCanal, ModeloVersion, Benchmarking
from src.models.productos import Producto
from src.models.proveedores import TgModeloItem
from src.models.users import Empresa

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
        user = get_jwt_identity()
        data = request.get_json()

        if isinstance(data, dict) and "transmision" in data:
            data = data["transmision"]
        elif isinstance(data, dict):
            data = [data]

        duplicados = []
        insertados = 0

        registros = db.session.query(Transmision).all()

        for item in data:
            existe = any(
                normalize(r.caja_cambios) == normalize(item.get("caja_cambios")) and
                normalize(r.descripcion_transmision) == normalize(item.get("descripcion_transmision"))
                for r in registros
            )

            if existe:
                duplicados.append(item)
                continue

            nuevo = Transmision(
                caja_cambios=item.get("caja_cambios"),
                descripcion_transmision=item.get("descripcion_transmision"),
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
            return jsonify({"message": "Elementos insertados correctamente"}), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Registro duplicado: ya existe un registro de electrónica con estos datos"
        }), 409

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

        insertados = 0
        duplicados = []

        registros_actuales = db.session.query(Motor).join(TipoMotor).all()

        for item in data:
            nombre_tipo_motor = item.get("tipo_motor_nombre")
            if not nombre_tipo_motor:
                duplicados.append(item)
                continue

            tipo_motor = db.session.query(TipoMotor).filter(
                func.lower(func.replace(func.replace(
                    func.replace(func.replace(func.replace(TipoMotor.nombre_tipo, 'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó',
                    'o'), 'ú', 'u')) ==
                normalize(nombre_tipo_motor)
            ).first()

            if not tipo_motor:
                tipo_motor = TipoMotor(
                    nombre_tipo=nombre_tipo_motor.strip(),
                    descripcion_tipo_motor=item.get("descripcion_tipo_motor")
                )
                db.session.add(tipo_motor)
                db.session.flush()

            existe = any(
                r.codigo_tipo_motor == tipo_motor.codigo_tipo_motor and
                normalize(r.nombre_motor) == normalize(item.get("nombre_motor")) and
                normalize(r.cilindrada) == normalize(item.get("cilindrada")) and
                normalize(r.caballos_fuerza) == normalize(item.get("caballos_fuerza")) and
                normalize(r.torque_maximo) == normalize(item.get("torque_maximo")) and
                normalize(r.sistema_combustible) == normalize(item.get("sistema_combustible")) and
                normalize(r.arranque) == normalize(item.get("arranque")) and
                normalize(r.sistema_refrigeracion) == normalize(item.get("sistema_refrigeracion")) and
                normalize(r.descripcion_motor) == normalize(item.get("descripcion_motor"))
                for r in registros_actuales
            )

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
        user = get_jwt_identity()
        data = request.get_json()

        if isinstance(data, dict) and "canal" in data:
            data = data["canal"]
        elif isinstance(data, dict):
            data = [data]

        duplicados = []
        insertados = 0

        registros = db.session.query(Canal).all()

        for item in data:
            estado = item.get("estado_canal")

            if isinstance(estado, str):
                estado_normalizado = estado.strip().lower()
                if estado_normalizado == "activo":
                    estado = 1
                elif estado_normalizado == "inactivo":
                    estado = 0
                else:
                    return jsonify({'error': f"Estado inválido en el registro: {estado}"}), 400

            existe = any(
                normalize(r.nombre_canal) == normalize(item.get("nombre_canal")) and
                normalize(str(r.estado_canal)) == normalize(str(estado)) and
                normalize(r.descripcion_canal) == normalize(item.get("descripcion_canal"))
                for r in registros
            )

            if existe:
                duplicados.append(item)
                continue

            nuevo = Canal(
                nombre_canal=item.get("nombre_canal"),
                estado_canal=estado,
                descripcion_canal=item.get("descripcion_canal"),
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
            return jsonify({"message": "Elementos insertados correctamente"}), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Registro duplicado: ya existe un registro de canal con estos datos"
        }), 409

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_marca_repuestos', methods=["POST"])
@jwt_required()
def insert_marca_repuestos():
    try:
        data = request.get_json()
        user = get_jwt_identity()

        if isinstance(data, dict):
            data = [data]

        registros_existentes = db.session.query(MarcaRepuesto).all()

        duplicados = []
        insertados = 0

        for item in data:
            nombre_comercial = item.get("nombre_comercial")
            estado = item.get("estado_marca_rep")
            nombre_fabricante = item.get("nombre_fabricante")

            if not nombre_comercial or estado is None:
                duplicados.append(item)
                continue

            # Normalizar estado
            if isinstance(estado, str):
                estado_normalizado = estado.strip().lower()
                if estado_normalizado == "activo":
                    estado = 1
                elif estado_normalizado == "inactivo":
                    estado = 0
                else:
                    duplicados.append(item)
                    continue

            if nombre_fabricante:
                existe = any(
                    r.nombre_fabricante and r.nombre_fabricante.lower() == nombre_fabricante.lower()
                    for r in registros_existentes
                )
                if existe:
                    duplicados.append(item)
                    continue

            nuevo = MarcaRepuesto(
                nombre_comercial=nombre_comercial,
                estado_marca_rep=estado,
                nombre_fabricante=nombre_fabricante,
                usuario_crea=user,
                fecha_creacion=datetime.now()
            )

            db.session.add(nuevo)
            insertados += 1

        if insertados == 0:
            db.session.rollback()
            return jsonify({"error": "No se insertó ningún registro válido"}), 409

        db.session.commit()

        return jsonify({
            "message": f"{insertados} registro(s) insertado(s), {len(duplicados)} duplicado(s) omitido(s)"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_producto_externo', methods=["POST"])
@jwt_required()
def insert_producto_externo():
    try:
        data = request.get_json()
        user = get_jwt_identity()

        if isinstance(data, dict):
            data = [data]

        registros_existentes = db.session.query(ProductoExterno).all()

        ultimo_codigo = db.session.query(ProductoExterno.codigo_prod_externo)\
            .order_by(ProductoExterno.codigo_prod_externo.desc()).first()

        if ultimo_codigo and ultimo_codigo[0].startswith('PE'):
            numero_actual = int(ultimo_codigo[0][2:])
        else:
            numero_actual = 0

        insertados = 0
        duplicados = []

        for item in data:
            codigo_marca_rep = item.get("codigo_marca_rep")
            nombre_producto = item.get("nombre_producto")
            estado = item.get("estado_prod_externo")
            descripcion_producto = item.get("descripcion_producto")
            empresa = item.get("empresa")

            if not codigo_marca_rep or not nombre_producto or empresa is None:
                duplicados.append(item)
                continue

            if isinstance(estado, str):
                estado_normalizado = estado.strip().lower()
                if estado_normalizado == "activo":
                    estado = 1
                elif estado_normalizado == "inactivo":
                    estado = 0
                else:
                    duplicados.append(item)
                    continue

            existe = any(
                r.nombre_producto.lower() == nombre_producto.lower() and
                r.codigo_marca_rep == codigo_marca_rep
                for r in registros_existentes
            )
            if existe:
                duplicados.append(item)
                continue

            numero_actual += 1
            nuevo_codigo = f"PE{str(numero_actual).zfill(5)}"

            nuevo = ProductoExterno(
                codigo_prod_externo=nuevo_codigo,
                codigo_marca_rep=codigo_marca_rep,
                nombre_producto=nombre_producto,
                estado_prod_externo=estado,
                descripcion_producto=descripcion_producto,
                empresa=empresa,
                usuario_crea=user,
                fecha_creacion=datetime.now()
            )

            db.session.add(nuevo)
            insertados += 1

        if not insertados:
            return jsonify({"error": "Registros duplicados detectados, no se insertó nada."}), 409

        db.session.commit()

        return jsonify({
            "message": f"{insertados} registro(s) insertado(s), {len(duplicados)} duplicado(s) omitido(s)"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_linea', methods=["POST"])
@jwt_required()
def insert_linea():
    try:
        data = request.json
        user = get_jwt_identity()

        if isinstance(data, list):
            nuevas_lineas = []
            errores = []
            for i, item in enumerate(data):
                nombre = item.get("nombre_linea")
                estado = item.get("estado_linea")
                descripcion = item.get("descripcion_linea", "")
                padre_nombre = item.get("nombre_linea_padre")

                if not nombre or estado not in [0, 1]:
                    errores.append(f"Fila {i + 2}: Campos obligatorios faltantes")
                    continue

                existe = db.session.query(Linea).filter(
                    func.lower(func.trim(Linea.nombre_linea)) == func.lower(nombre.strip())
                ).first()
                if existe:
                    errores.append(f"Fila {i + 2}: Línea '{nombre}' ya existe")
                    continue

                nueva = Linea(
                    nombre_linea=nombre.strip(),
                    estado_linea=estado,
                    descripcion_linea=descripcion.strip(),
                    usuario_crea=user,
                    fecha_creacion=datetime.now()
                )
                db.session.add(nueva)
                db.session.flush()

                if padre_nombre:
                    padre = db.session.query(Linea).filter(
                        func.lower(func.trim(Linea.nombre_linea)) == func.lower(padre_nombre.strip())
                    ).first()
                    if padre:
                        nueva.codigo_linea_padre = padre.codigo_linea
                    else:
                        nueva.codigo_linea_padre = nueva.codigo_linea
                else:
                    nueva.codigo_linea_padre = nueva.codigo_linea

                nuevas_lineas.append(nueva)

            db.session.commit()
            if errores and not nuevas_lineas:
                return jsonify({"error": "No se insertó ningún registro válido", "detalles": errores}), 400
            elif errores:
                return jsonify({"message": "Se insertaron algunas líneas con errores", "detalles": errores}), 206
            return jsonify({"message": f"{len(nuevas_lineas)} líneas insertadas correctamente"})

        # Inserción individual desde formulario
        nombre = data.get("nombre_linea")
        estado = data.get("estado_linea")
        descripcion = data.get("descripcion_linea", "")
        padre_codigo = data.get("codigo_linea_padre")

        if not nombre or estado not in [0, 1]:
            return jsonify({"error": "Los campos 'nombre_linea' y 'estado_linea' son obligatorios"}), 400

        existe = db.session.query(Linea).filter(
            func.lower(func.trim(Linea.nombre_linea)) == func.lower(nombre.strip())
        ).first()
        if existe:
            return jsonify({"error": f"Ya existe una línea con el nombre '{nombre}'"}), 409

        nueva_linea = Linea(
            nombre_linea=nombre.strip(),
            estado_linea=estado,
            descripcion_linea=descripcion.strip(),
            usuario_crea=user,
            fecha_creacion=datetime.now()
        )

        db.session.add(nueva_linea)
        db.session.flush()

        if padre_codigo:
            padre = db.session.query(Linea).filter_by(codigo_linea=padre_codigo).first()
            nueva_linea.codigo_linea_padre = padre.codigo_linea if padre else nueva_linea.codigo_linea
        else:
            nueva_linea.codigo_linea_padre = nueva_linea.codigo_linea

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
        data = request.get_json()
        user = get_jwt_identity()

        if isinstance(data, dict):
            data = [data]

        registros_existentes = db.session.query(ModeloSRI).all()
        nombres_existentes = {r.nombre_modelo.lower() for r in registros_existentes}

        duplicados = []
        insertados = 0

        for item in data:
            nombre = item.get("nombre_modelo")
            anio = item.get("anio_modelo")
            estado = item.get("estado_modelo")

            if not nombre or estado not in [0, 1] or not (1950 <= int(anio) <= 2100):
                duplicados.append(item)
                continue

            if nombre.lower() in nombres_existentes:
                duplicados.append(item)
                continue

            nuevo = ModeloSRI(
                nombre_modelo=nombre,
                anio_modelo=anio,
                estado_modelo=estado,
                usuario_crea=user,
                fecha_creacion=datetime.now()
            )

            db.session.add(nuevo)
            nombres_existentes.add(nombre.lower())
            insertados += 1

        if insertados == 0:
            db.session.rollback()
            return jsonify({"error": "No se insertó ningún registro válido"}), 409

        db.session.commit()

        return jsonify({
            "message": f"{insertados} modelo(s) insertado(s), {len(duplicados)} duplicado(s) omitido(s)"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_modelo_homologado', methods=["POST"])
@jwt_required()
def insert_modelo_homologado():
    try:
        data = request.get_json()
        user = get_jwt_identity()

        if isinstance(data, dict):
            data = [data]

        insertados, errores = 0, []

        for item in data:
            codigo_sri = item.get("codigo_modelo_sri")
            nombre_modelo = item.get("nombre_modelo_sri", "").strip().lower()
            descripcion = item.get("descripcion_homologacion", "").strip()

            modelo_sri = None

            if not codigo_sri and nombre_modelo:
                modelo_sri = db.session.query(ModeloSRI).filter(
                    func.lower(func.trim(func.replace(ModeloSRI.nombre_modelo, '\u00A0', ' '))) == nombre_modelo
                ).first()
                if modelo_sri:
                    codigo_sri = modelo_sri.codigo_modelo_sri
            elif codigo_sri:
                modelo_sri = db.session.query(ModeloSRI).filter_by(codigo_modelo_sri=codigo_sri).first()

            if not modelo_sri:
                errores.append({**item, "error": "Modelo SRI no encontrado"})
                continue

            ya_existe = db.session.query(ModeloHomologado).filter_by(
                codigo_modelo_sri=modelo_sri.codigo_modelo_sri
            ).first()

            if ya_existe:
                errores.append({**item, "error": "Ya existe homologación para este modelo"})
                continue

            nuevo = ModeloHomologado(
                codigo_modelo_sri=modelo_sri.codigo_modelo_sri,
                descripcion_homologacion=descripcion,
                usuario_crea=user,
                fecha_creacion=datetime.now()
            )

            db.session.add(nuevo)
            insertados += 1

        if insertados == 0:
            db.session.rollback()
            return jsonify({
                "error": "No se insertó ningún registro válido",
                "detalles": errores
            }), 409

        db.session.commit()
        return jsonify({
            "message": f"{insertados} homologación(es) insertada(s), {len(errores)} con error(es)",
            "errores": errores
        }), 201

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

        existe_modelo = db.session.query(ModeloHomologado).filter_by(
            codigo_modelo_homologado=codigo_homologado
        ).first()
        if not existe_modelo:
            return jsonify({"error": "El código de modelo homologado no existe"}), 404

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

@bench.route('/insert_modelo_comercial', methods=['POST'])
@jwt_required()
@cross_origin()
def insert_modelo_comercial():
    try:
        user = get_jwt_identity()
        data = request.get_json()

        if isinstance(data, dict) and "modelo" in data:
            data = [data["modelo"]]
        elif isinstance(data, dict):
            data = [data]

        insertados = 0
        duplicados = []

        for item in data:
            nombre_marca = item.get("nombre_marca")
            nombre_modelo = item.get("nombre_modelo")
            codigo_modelo_homologado = item.get("codigo_modelo_homologado")
            anio_modelo = item.get("anio_modelo")
            estado_modelo = item.get("estado_modelo")

            if not nombre_marca or not nombre_modelo or not codigo_modelo_homologado or not anio_modelo:
                duplicados.append({**item, "error": "Faltan campos obligatorios"})
                continue

            homologado = db.session.query(ModeloHomologado).filter_by(codigo_modelo_homologado=codigo_modelo_homologado).first()
            if not homologado:
                duplicados.append({**item, "error": "Modelo homologado no encontrado"})
                continue

            marca = db.session.query(Marca).filter(
                func.lower(func.replace(func.trim(Marca.nombre_marca), '\u00A0', ' ')) == normalize(nombre_marca)
            ).first()

            if not marca:
                marca = Marca(
                    nombre_marca=nombre_marca.strip(),
                    estado_marca=estado_modelo.strip(),
                    usuario_crea=user,
                    fecha_creacion=datetime.now()
                )
                db.session.add(marca)
                db.session.flush()

            existe = db.session.query(ModeloComercial).filter(
                ModeloComercial.codigo_marca == marca.codigo_marca,
                func.lower(func.replace(func.trim(ModeloComercial.nombre_modelo), '\u00A0', ' ')) == normalize(nombre_modelo),
                ModeloComercial.codigo_modelo_homologado == codigo_modelo_homologado,
                ModeloComercial.anio_modelo == int(anio_modelo)
            ).first()

            if existe:
                duplicados.append({**item, "error": "Ya existe este modelo comercial para esa marca"})
                continue

            nuevo = ModeloComercial(
                codigo_marca=marca.codigo_marca,
                codigo_modelo_homologado=codigo_modelo_homologado,
                nombre_modelo=nombre_modelo.strip(),
                anio_modelo=int(anio_modelo),
                estado_modelo=int(estado_modelo) if estado_modelo in [0, 1] else 1,
                usuario_crea=user,
                fecha_creacion=datetime.now()
            )
            db.session.add(nuevo)
            insertados += 1

        db.session.commit()

        if insertados == 0 and duplicados:
            return jsonify({"error": "Todos los registros ya existen", "detalles": duplicados}), 409
        elif duplicados:
            return jsonify({
                "message": f"{insertados} insertado(s), {len(duplicados)} duplicado(s) omitido(s)",
                "detalles": duplicados
            }), 201
        else:
            return jsonify({"message": "Modelo(s) comercial(es) insertado(s) correctamente"}), 200

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Ya existe un modelo comercial con los mismos datos.", "details": str(e)}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_segmento', methods=["POST"])
@jwt_required()
def insert_segmento():
    try:
        data = request.json
        user = get_jwt_identity()

        nombre = data.get("nombre_segmento", "").strip()
        estado = data.get("estado_segmento")
        linea = data.get("codigo_linea")
        modelo = data.get("codigo_modelo_comercial")
        marca = data.get("codigo_marca")
        descripcion = data.get("descripcion_segmento", "").strip()

        if not nombre or estado not in [0, 1] or not all([linea, modelo, marca]):
            return jsonify({"error": "Todos los campos obligatorios deben ser enviados"}), 400

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

        max_codigo = db.session.query(func.max(Segmento.codigo_segmento)).scalar() or 0
        nuevo_codigo = max_codigo + 1

        nuevo = Segmento(
            codigo_segmento=nuevo_codigo,
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

        return jsonify({
            "message": "Segmento insertado correctamente",
            "codigo_segmento": nuevo.codigo_segmento
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_version', methods=["POST"])
@jwt_required()
def insert_version():
    try:
        data = request.get_json()
        user = get_jwt_identity()

        if isinstance(data, dict):
            data = [data]

        registros_existentes = db.session.query(Version).all()

        duplicados = []
        insertados = 0

        for item in data:
            nombre_version = item.get("nombre_version")
            estado = item.get("estado_version")
            descripcion_version = item.get("descripcion_version")

            if not nombre_version or estado is None:
                duplicados.append(item)
                continue

            # Normalizar estado
            if isinstance(estado, str):
                estado_normalizado = estado.strip().lower()
                if estado_normalizado == "activo":
                    estado = 1
                elif estado_normalizado == "inactivo":
                    estado = 0
                else:
                    duplicados.append(item)
                    continue

            if nombre_version:
                existe = any(
                    r.nombre_version and r.nombre_version.lower() == nombre_version.lower()
                    for r in registros_existentes
                )
                if existe:
                    duplicados.append(item)
                    continue

            nuevo = Version(
                nombre_version=nombre_version,
                estado_version=estado,
                descripcion_version=descripcion_version,
                usuario_crea=user,
                fecha_creacion=datetime.now()
            )

            db.session.add(nuevo)
            insertados += 1

        if insertados == 0:
            db.session.rollback()
            return jsonify({"error": "No se insertó, registro inválido o duplicado"}), 409

        db.session.commit()

        return jsonify({
            "message": f"{insertados} registro(s) insertado(s), {len(duplicados)} duplicado(s) omitido(s)"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/insert_modelo_version_repuesto', methods=['POST'])
@jwt_required()
@cross_origin()
def insert_modelo_version_repuesto():
    try:
        data = request.get_json()

        if isinstance(data, dict) and "repuestos" in data:
            data = data["repuestos"]
        elif isinstance(data, dict):
            data = [data]

        insertados = 0
        errores = []
        duplicados = []

        for item in data:
            cod_producto = item.get("cod_producto")
            empresa = item.get("empresa")
            codigo_prod_externo = item.get("codigo_prod_externo")
            codigo_modelo_comercial = item.get("codigo_modelo_comercial")
            codigo_marca = item.get("codigo_marca")
            codigo_version = item.get("codigo_version")

            if not cod_producto or not empresa:
                if item.get("nombre_producto"):
                    prod = db.session.query(Producto).filter_by(nombre=item["nombre_producto"]).first()
                    if prod:
                        cod_producto = prod.cod_producto
                        empresa = prod.empresa

                    else:
                        errores.append({"error": "Producto no encontrado", "repuestos": item})
                        continue

            if not codigo_prod_externo and item.get("nombre_producto_externo"):
                ext = db.session.query(ProductoExterno).filter_by(nombre_producto=item["nombre_producto_externo"]).first()
                if ext:
                    codigo_prod_externo = ext.codigo_prod_externo
                else:
                    errores.append({"error": "Producto externo no encontrado", "repuestos": item})
                    continue

            if not codigo_modelo_comercial or not codigo_marca:
                if item.get("nombre_modelo_comercial"):
                    modelo = db.session.query(ModeloComercial).filter_by(nombre_modelo=item["nombre_modelo_comercial"]).first()
                    if modelo:
                        codigo_modelo_comercial = modelo.codigo_modelo_comercial
                        codigo_marca = modelo.codigo_marca
                    else:
                        errores.append({"error": "Modelo comercial no encontrado", "repuestos": item})
                        continue

            if not codigo_version and item.get("nombre_version"):
                version = db.session.query(Version).filter_by(nombre_version=item["nombre_version"]).first()
                if version:
                    codigo_version = version.codigo_version
                else:
                    errores.append({"error": "Versión no encontrada", "repuestos": item})
                    continue

            descripcion = item.get("descripcion") or item.get("descripción")
            precio_producto_modelo = item.get("precio_producto_modelo")
            precio_venta_distribuidor = item.get("precio_venta_distribuidor")

            campos_obligatorios = [
                cod_producto, empresa, codigo_prod_externo,
                codigo_modelo_comercial, codigo_marca, codigo_version,
                precio_producto_modelo, precio_venta_distribuidor
            ]

            if any(c is None or c == "" for c in campos_obligatorios):
                errores.append({"error": "Faltan campos obligatorios", "repuestos": item})
                continue

            existe = db.session.query(ModeloVersionRepuesto).filter_by(
                cod_producto=cod_producto,
                codigo_modelo_comercial=codigo_modelo_comercial,
                codigo_marca=codigo_marca,
                empresa=empresa
            ).first()
            if existe:
                duplicados.append({"error": "Registro duplicado", "repuestos": item})
                continue

            nuevo = ModeloVersionRepuesto(
                codigo_prod_externo=codigo_prod_externo,
                codigo_version=codigo_version,
                empresa=empresa,
                cod_producto=cod_producto,
                codigo_modelo_comercial=codigo_modelo_comercial,
                codigo_marca=codigo_marca,
                descripcion=descripcion,
                precio_producto_modelo=precio_producto_modelo,
                precio_venta_distribuidor=precio_venta_distribuidor
            )
            db.session.add(nuevo)
            insertados += 1

        db.session.commit()

        if insertados == 0:
            return jsonify({"error": "No se insertó ningún registro", "detalles": errores + duplicados}), 409

        return jsonify({
            "message": f"{insertados} registro(s) insertado(s)",
            "errores": errores,
            "duplicados": duplicados
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

@bench.route('/insert_cliente_canal', methods=['POST'])
@jwt_required()
@cross_origin()
def insert_cliente_canal():
    try:
        data = request.get_json()

        if isinstance(data, dict) and "clientes" in data:
            data = data["clientes"]
        elif isinstance(data, dict):
            data = [data]

        insertados = 0
        errores = []

        for item in data:
            codigo_canal = item.get("codigo_canal")
            descripcion = item.get("descripcion_cliente_canal")
            cod_modelo_vers_repuesto = item.get("codigo_mod_vers_repuesto")
            cod_producto = item.get("cod_producto")
            empresa = item.get("empresa")
            codigo_modelo_comercial = item.get("codigo_modelo_comercial")
            codigo_marca = item.get("codigo_marca")

            if not all([cod_modelo_vers_repuesto, cod_producto, empresa, codigo_modelo_comercial, codigo_marca]):
                nombre_producto = item.get("nombre_producto")
                nombre_modelo = item.get("nombre_modelo_comercial")
                nombre_version = item.get("nombre_version")

                modelo = (
                    db.session.query(ModeloVersionRepuesto)
                    .join(Producto, (ModeloVersionRepuesto.cod_producto == Producto.cod_producto) & (ModeloVersionRepuesto.empresa == Producto.empresa))
                    .join(ModeloComercial, ModeloVersionRepuesto.codigo_modelo_comercial == ModeloComercial.codigo_modelo_comercial)
                    .join(Version, ModeloVersionRepuesto.codigo_version == Version.codigo_version)
                    .filter(
                        Producto.nombre == nombre_producto,
                        ModeloComercial.nombre_modelo == nombre_modelo,
                        Version.nombre_version == nombre_version
                    ).first()
                )

                if modelo:
                    cod_modelo_vers_repuesto = modelo.codigo_mod_vers_repuesto
                    cod_producto = modelo.cod_producto
                    empresa = modelo.empresa
                    codigo_modelo_comercial = modelo.codigo_modelo_comercial
                    codigo_marca = modelo.codigo_marca
                else:
                    errores.append({"error": "No se pudo resolver modelo_version_repuesto", "cliente": item})
                    continue

            campos_obligatorios = [codigo_canal, cod_modelo_vers_repuesto, cod_producto, empresa, codigo_modelo_comercial, codigo_marca]
            if any(c is None or c == '' for c in campos_obligatorios):
                errores.append({"error": "Faltan campos obligatorios", "cliente": item})
                continue

            nuevo = ClienteCanal(
                codigo_canal=codigo_canal,
                codigo_mod_vers_repuesto=cod_modelo_vers_repuesto,
                empresa=empresa,
                cod_producto=cod_producto,
                codigo_modelo_comercial=codigo_modelo_comercial,
                codigo_marca=codigo_marca,
                descripcion_cliente_canal=descripcion
            )
            db.session.add(nuevo)
            insertados += 1

        if insertados:
            db.session.commit()
            return jsonify({"message": "Registros insertados correctamente", "insertados": insertados}), 201
        else:
            db.session.rollback()
            return jsonify({"error": "No se insertó ningún registro", "detalles": errores}), 409

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500

@bench.route('/insert_modelo_version', methods=["POST"])
@jwt_required()
def insert_modelo_version():
    try:
        data = request.json

        campos_requeridos = [
            "codigo_imagen",
            "codigo_dim_peso",
            "codigo_electronica",
            "codigo_motor",
            "codigo_tipo_motor",
            "codigo_transmision",
            "codigo_color_bench",
            "codigo_chasis",
            "codigo_modelo_comercial",
            "codigo_marca",
            "codigo_version",
            "codigo_cliente_canal",
            "empresa",
            "cod_producto",
            "codigo_mod_vers_repuesto",
            "nombre_modelo_version",
            "anio_modelo_version",
            "precio_producto_modelo",
            "precio_venta_distribuidor"
        ]

        faltantes = [campo for campo in campos_requeridos if data.get(campo) in [None, ""]]
        if faltantes:
            return jsonify({
                "error": "No se insertó ningún registro",
                "detalles": [{
                    "error": "Faltan campos obligatorios",
                    "repuestos": data
                }]
            }), 400

        if not (1950 <= int(data["anio_modelo_version"]) <= 2100):
            return jsonify({"error": "Año de modelo fuera de rango (1950-2100)"}), 400

        nombre_existente = db.session.query(ModeloVersion).filter(
            func.lower(ModeloVersion.nombre_modelo_version) == data["nombre_modelo_version"].lower()
        ).first()
        if nombre_existente:
            return jsonify({"error": "Ya existe un modelo con ese nombre"}), 409

        imagen = db.session.query(Imagenes).filter_by(codigo_imagen=data["codigo_imagen"]).first()
        motor = db.session.query(Motor).filter_by(codigo_motor=data["codigo_motor"]).first()
        color = db.session.query(Color).filter_by(codigo_color_bench=data["codigo_color_bench"]).first()
        modelo = db.session.query(ModeloComercial).filter_by(codigo_modelo_comercial=data["codigo_modelo_comercial"]).first()
        version = db.session.query(Version).filter_by(codigo_version=data["codigo_version"]).first()

        if not imagen:
            return jsonify({"error": "Imagen no encontrada"}), 404
        if not motor:
            return jsonify({"error": "Motor no encontrado"}), 404
        if not color:
            return jsonify({"error": "Color no encontrado"}), 404
        if not modelo or modelo.codigo_marca != data["codigo_marca"]:
            return jsonify({"error": "Modelo comercial o marca inválida"}), 404
        if not version:
            return jsonify({"error": "Versión no encontrada"}), 404

        def validar_existencia(model, **kwargs):
            return db.session.query(model).filter_by(**kwargs).first() is not None

        validaciones = [
            (DimensionPeso, {"codigo_dim_peso": data["codigo_dim_peso"]}),
            (ElectronicaOtros, {"codigo_electronica": data["codigo_electronica"]}),
            (Transmision, {"codigo_transmision": data["codigo_transmision"]}),
            (Chasis, {"codigo_chasis": data["codigo_chasis"]}),
            (ClienteCanal, {
                "codigo_cliente_canal": data["codigo_cliente_canal"],
                "codigo_mod_vers_repuesto": data["codigo_mod_vers_repuesto"],
                "empresa": data["empresa"],
                "cod_producto": data["cod_producto"],
                "codigo_modelo_comercial": data["codigo_modelo_comercial"],
                "codigo_marca": data["codigo_marca"]
            })
        ]

        for model, filtro in validaciones:
            if not validar_existencia(model, **filtro):
                return jsonify({"error": f"Entidad no encontrada: {model.__name__}"}), 404

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
        db.session.flush()
        db.session.commit()

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

#METODOS GET CATALOGO BENCH ------------------------------------------------------------------------------>

@bench.route('/get_chasis', methods=["GET"])
@jwt_required()
def get_chasis():
    try:
        chasis_list = db.session.query(Chasis).order_by(Chasis.codigo_chasis.asc()).all()

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
        dimensiones = db.session.query(DimensionPeso).order_by(DimensionPeso.codigo_dim_peso.asc()).all()

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
        #electronica = db.session.query(ElectronicaOtros).all()
        electronica = db.session.query(ElectronicaOtros).order_by(ElectronicaOtros.codigo_electronica.asc()).all()

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
        #motores = db.session.query(Motor).all()
        motores = db.session.query(Motor).order_by(Motor.codigo_motor.asc()).all()

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

@bench.route('/get_imagenes', methods=["GET"])
@jwt_required()
def get_imagenes():
    try:
        #img = db.session.query(Imagenes).all()
        img = db.session.query(Imagenes).order_by(Imagenes.codigo_imagen.asc()).all()

        resultado = []
        for im in img:
            resultado.append({
                "codigo_imagen": im.codigo_imagen,
                "path_imagen": im.path_imagen,
                "descripcion_imagen": im.descripcion_imagen,
                "usuario_crea": im.usuario_crea,
                "usuario_modifica": im.usuario_modifica,
                "fecha_creacion": im.fecha_creacion.isoformat() if im.fecha_creacion else None,
                "fecha_modificacion": im.fecha_modificacion.isoformat() if im.fecha_modificacion else None
            })

        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bench.route('/get_transmision', methods=["GET"])
@jwt_required()
def get_transmision():
    try:
        #trans = db.session.query(Transmision).all()
        trans = db.session.query(Transmision).order_by(Transmision.caja_cambios.asc()).all()

        resultado = []
        for tr in trans:
            resultado.append({
                "codigo_transmision": tr.codigo_transmision,
                "caja_cambios": tr.caja_cambios,
                "descripcion_transmision": tr.descripcion_transmision,
                "usuario_crea": tr.usuario_crea,
                "usuario_modifica": tr.usuario_modifica,
                "fecha_creacion": tr.fecha_creacion.isoformat() if tr.fecha_creacion else None,
                "fecha_modificacion": tr.fecha_modificacion.isoformat() if tr.fecha_modificacion else None
            })

        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bench.route('/get_canal', methods=["GET"])
@jwt_required()
def get_canal():
    try:
        #canal = db.session.query(Canal).all()
        canal = db.session.query(Canal).order_by(Canal.codigo_canal.asc()).all()

        resultado = []
        for c in canal:
            resultado.append({
                "codigo_canal": c.codigo_canal,
                "nombre_canal": c.nombre_canal,
                "estado_canal": c.estado_canal,
                "descripcion_canal": c.descripcion_canal,
                "usuario_crea": c.usuario_crea,
                "usuario_modifica": c.usuario_modifica,
                "fecha_creacion": c.fecha_creacion.isoformat() if c.fecha_creacion else None,
                "fecha_modificacion": c.fecha_modificacion.isoformat() if c.fecha_modificacion else None
            })

        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bench.route('/get_lineas', methods=["GET"])
@jwt_required()
def get_lineas():
    try:
        #lineas = db.session.query(Linea).all()
        lineas = db.session.query(Linea).order_by(Linea.codigo_linea.asc()).all()

        resultado = []
        for l in lineas:
            padre = next((p.nombre_linea for p in lineas if p.codigo_linea == l.codigo_linea_padre), None)

            resultado.append({
                "codigo_linea": l.codigo_linea,
                "codigo_linea_padre": l.codigo_linea_padre,
                "nombre_linea": l.nombre_linea,
                "nombre_linea_padre": padre if padre and padre != l.nombre_linea else None,
                "estado_linea": l.estado_linea,
                "descripcion_linea": l.descripcion_linea,
                "usuario_crea": l.usuario_crea,
                "usuario_modifica": l.usuario_modifica,
                "fecha_creacion": l.fecha_creacion.isoformat() if l.fecha_creacion else None,
                "fecha_modificacion": l.fecha_modificacion.isoformat() if l.fecha_modificacion else None
            })

        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bench.route('/get_marca_repuestos', methods=["GET"])
@jwt_required()
def get_marca_repuestos():
    try:
        registros = db.session.query(MarcaRepuesto).order_by(MarcaRepuesto.nombre_comercial).all()

        resultado = []
        for r in registros:
            resultado.append({
                "codigo_marca_rep": r.codigo_marca_rep,
                "nombre_comercial": r.nombre_comercial,
                "estado_marca_rep": r.estado_marca_rep,
                "nombre_fabricante": r.nombre_fabricante,
                "usuario_crea": r.usuario_crea,
                "usuario_modifica": r.usuario_modifica,
                "fecha_creacion": r.fecha_creacion.isoformat() if r.fecha_creacion else None,
                "fecha_modificacion": r.fecha_modificacion.isoformat() if r.fecha_modificacion else None
            })

        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bench.route('/get_productos_externos', methods=["GET"])
@jwt_required()
def get_productos_externos():
    try:
        registros = db.session.query(ProductoExterno).order_by(ProductoExterno.nombre_producto).all()

        resultado = []
        for r in registros:
            resultado.append({
                "codigo_prod_externo": r.codigo_prod_externo,
                "codigo_marca_rep": r.codigo_marca_rep,
                "nombre_producto": r.nombre_producto,
                "estado_prod_externo": r.estado_prod_externo,
                "descripcion_producto": r.descripcion_producto,
                "empresa": r.empresa,
                "usuario_crea": r.usuario_crea,
                "usuario_modifica": r.usuario_modifica,
                "fecha_creacion": r.fecha_creacion.isoformat() if r.fecha_creacion else None,
                "fecha_modificacion": r.fecha_modificacion.isoformat() if r.fecha_modificacion else None
            })

        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bench.route('/get_version', methods=["GET"])
@jwt_required()
def get_version():
    try:
        registros = db.session.query(Version).order_by(Version.nombre_version).all()

        resultado = []
        for r in registros:
            resultado.append({
                "codigo_version": r.codigo_version,
                "nombre_version": r.nombre_version,
                "estado_version": r.estado_version,
                "descripcion_version": r.descripcion_version,
                "usuario_crea": r.usuario_crea,
                "usuario_modifica": r.usuario_modifica,
                "fecha_creacion": r.fecha_creacion.isoformat() if r.fecha_creacion else None,
                "fecha_modificacion": r.fecha_modificacion.isoformat() if r.fecha_modificacion else None
            })

        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bench.route('/get_modelos_sri', methods=["GET"])
@jwt_required()
def get_modelos_sri():
    try:
        modelos = db.session.query(ModeloSRI).order_by(ModeloSRI.codigo_modelo_sri.desc()).all()
        resultado = [
            {
                "codigo_modelo_sri": m.codigo_modelo_sri,
                "nombre_modelo": m.nombre_modelo,
                "anio_modelo": m.anio_modelo,
                "estado_modelo": m.estado_modelo,
                "usuario_crea": m.usuario_crea,
                "usuario_modifica": m.usuario_modifica,
                "fecha_creacion": m.fecha_creacion.isoformat() if m.fecha_creacion else None,
                "fecha_modificacion": m.fecha_modificacion.isoformat() if m.fecha_modificacion else None
            }
            for m in modelos
        ]
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bench.route('/get_modelos_homologados', methods=["GET"])
@jwt_required()
def get_modelos_homologados():
    try:
        homologados = db.session.query(ModeloHomologado).join(ModeloSRI).all()
        resultado = [
            {
                "codigo_modelo_homologado": h.codigo_modelo_homologado,
                "codigo_modelo_sri": h.codigo_modelo_sri,
                "nombre_modelo_sri": h.modelo_sri.nombre_modelo if h.modelo_sri else None,
                "descripcion_homologacion": h.descripcion_homologacion,
                "usuario_crea": h.usuario_crea,
                "usuario_modifica": h.usuario_modifica,
                "fecha_creacion": h.fecha_creacion.isoformat() if h.fecha_creacion else None,
                "fecha_modificacion": h.fecha_modificacion.isoformat() if h.fecha_modificacion else None
            }
            for h in homologados
        ]
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bench.route('/get_marca', methods=["GET"])
@jwt_required()
def get_marca():
    try:
        marca = db.session.query(Marca).all()

        resultado = []
        for m in marca:
            resultado.append({
                "codigo_marca": m.codigo_marca,
                "nombre_marca": m.nombre_marca,
                "estado_marca": m.estado_marca
            })

        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bench.route('/get_modelos_comerciales', methods=['GET'])
@jwt_required()
def get_modelos_comerciales():
    try:
        registros = db.session.query(ModeloComercial).order_by(ModeloComercial.nombre_modelo.asc()).all()
        resultados = []

        for modelo in registros:
            resultados.append({
                "codigo_modelo_comercial": modelo.codigo_modelo_comercial,
                "nombre_marca": modelo.marca.nombre_marca,
                "nombre_modelo_homologado": modelo.modelo_homologado.modelo_sri.nombre_modelo,
                "codigo_modelo_homologado": modelo.codigo_modelo_homologado,
                "codigo_marca": modelo.codigo_marca,
                "nombre_modelo": modelo.nombre_modelo,
                "anio_modelo": modelo.anio_modelo,
                "estado_modelo": modelo.estado_modelo,
                "usuario_crea": modelo.usuario_crea,
                "fecha_creacion": modelo.fecha_creacion.isoformat() if modelo.fecha_creacion else None,
                "fecha_modificacion": modelo.fecha_modificacion.isoformat() if modelo.fecha_modificacion else None
            })

        return jsonify(resultados), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bench.route('/get_modelos_version_repuesto', methods=['GET'])
@jwt_required()
@cross_origin()
def get_modelos_version_repuesto():
    try:
        ModeloItemAlias = aliased(TgModeloItem)

        resultados = db.session.query(
            ModeloVersionRepuesto.codigo_mod_vers_repuesto,
            ModeloVersionRepuesto.codigo_modelo_comercial,
            ModeloVersionRepuesto.codigo_marca,
            ModeloVersionRepuesto.codigo_version,
            ModeloVersionRepuesto.empresa,
            ModeloVersionRepuesto.codigo_prod_externo,
            Producto.cod_producto,
            Producto.nombre.label("nombre_producto"),
            ProductoExterno.nombre_producto.label("nombre_producto_externo"),
            ModeloComercial.nombre_modelo.label("nombre_modelo_comercial"),
            Marca.nombre_marca.label("nombre_marca"),
            Version.nombre_version,
            Empresa.nombre.label("nombre_empresa"),
            ModeloItemAlias.nombre.label("nombre_item"),
            ModeloVersionRepuesto.precio_producto_modelo,
            ModeloVersionRepuesto.precio_venta_distribuidor,
            ModeloVersionRepuesto.descripcion
        ).join(Producto, (ModeloVersionRepuesto.cod_producto == Producto.cod_producto) & (ModeloVersionRepuesto.empresa == Producto.empresa))\
         .join(ProductoExterno, ModeloVersionRepuesto.codigo_prod_externo == ProductoExterno.codigo_prod_externo)\
         .join(ModeloComercial, ModeloVersionRepuesto.codigo_modelo_comercial == ModeloComercial.codigo_modelo_comercial)\
         .join(Marca, ModeloVersionRepuesto.codigo_marca == Marca.codigo_marca)\
         .join(Version, ModeloVersionRepuesto.codigo_version == Version.codigo_version)\
         .join(Empresa, ModeloVersionRepuesto.empresa == Empresa.empresa)\
         .join(ModeloItemAlias, (Producto.empresa == ModeloItemAlias.empresa) & (Producto.cod_modelo == ModeloItemAlias.cod_modelo) & (Producto.cod_item == ModeloItemAlias.cod_item))\
         .all()

        return jsonify([{
            "codigo_mod_vers_repuesto": r.codigo_mod_vers_repuesto,
            "cod_producto": r.cod_producto,
            "codigo_modelo_comercial": r.codigo_modelo_comercial,
            "codigo_marca": r.codigo_marca,
            "codigo_version": r.codigo_version,
            "empresa": r.empresa,
            "codigo_prod_externo": r.codigo_prod_externo,
            "nombre_producto": r.nombre_producto,
            "nombre_producto_externo": r.nombre_producto_externo,
            "nombre_modelo_comercial": r.nombre_modelo_comercial,
            "nombre_marca": r.nombre_marca,
            "nombre_version": r.nombre_version,
            "nombre_empresa": r.nombre_empresa,
            "nombre_item": r.nombre_item,
            "precio_producto_modelo": r.precio_producto_modelo,
            "precio_venta_distribuidor": r.precio_venta_distribuidor,
            "descripcion": r.descripcion
        } for r in resultados]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bench.route('/get_cliente_canal', methods=['GET'])
@jwt_required()
@cross_origin()
def get_cliente_canal():
    try:
        #registros = db.session.query(ClienteCanal).all()
        registros = db.session.query(ClienteCanal).order_by(ClienteCanal.codigo_cliente_canal.asc()).all()
        resultados = []

        for cliente in registros:
            modelo = db.session.query(ModeloComercial).filter_by(
                codigo_modelo_comercial=cliente.codigo_modelo_comercial,
                codigo_marca=cliente.codigo_marca
            ).first()

            producto = db.session.query(Producto).filter_by(
                cod_producto=cliente.cod_producto,
                empresa=cliente.empresa
            ).first()

            canal = db.session.query(Canal).filter_by(
                codigo_canal=cliente.codigo_canal
            ).first()

            modelo_version = db.session.query(ModeloVersionRepuesto).filter_by(
                codigo_mod_vers_repuesto=cliente.codigo_mod_vers_repuesto
            ).first()

            version = db.session.query(Version).filter_by(
                codigo_version=modelo_version.codigo_version
            ).first() if modelo_version else None

            empresa_data = db.session.query(Empresa).filter_by(
                empresa=cliente.empresa
            ).first()

            resultados.append({
                "codigo_cliente_canal": cliente.codigo_cliente_canal,
                "codigo_canal": cliente.codigo_canal,
                "nombre_canal": canal.nombre_canal if canal else None,
                "codigo_mod_vers_repuesto": cliente.codigo_mod_vers_repuesto,
                "descripcion_cliente_canal": cliente.descripcion_cliente_canal,
                "cod_producto": cliente.cod_producto,
                "empresa": cliente.empresa,
                "nombre_empresa": empresa_data.nombre if empresa_data else None,
                "nombre_producto": producto.nombre if producto else None,
                "codigo_modelo_comercial": cliente.codigo_modelo_comercial,
                "nombre_modelo_comercial": modelo.nombre_modelo if modelo else None,
                "codigo_marca": cliente.codigo_marca,
                "nombre_marca": modelo.marca.nombre_marca if modelo and modelo.marca else None,
                "codigo_version": cliente.codigo_mod_vers_repuesto,
                "nombre_version": version.nombre_version if version else None
            })

        return jsonify(resultados), 200

    except Exception as e:
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500

@bench.route('/get_productos', methods=['GET'])
@jwt_required()
@cross_origin()
def get_productos():
    try:
        EmpresaAlias = aliased(Empresa)
        ModeloItemAlias = aliased(TgModeloItem)

        productos = db.session.query(
            Producto.cod_producto,
            Producto.cod_modelo,
            Producto.cod_item,
            ModeloItemAlias.nombre.label("nombre_item"),
            Producto.nombre.label("nombre_producto"),
            Producto.empresa,
            EmpresaAlias.nombre.label("nombre_empresa")
        ).join(
            EmpresaAlias, Producto.empresa == EmpresaAlias.empresa
        ).join(
            ModeloItemAlias,
            (Producto.empresa == ModeloItemAlias.empresa) &
            (Producto.cod_modelo == ModeloItemAlias.cod_modelo) &
            (Producto.cod_item == ModeloItemAlias.cod_item)
        ).filter(
            Producto.activo == 'S'
        ).all()

        resultado = [
            {
                "cod_producto": p.cod_producto,
                "cod_modelo": p.cod_modelo,
                "cod_item": p.cod_item,
                "nombre_item": p.nombre_item.strip(),
                "nombre_producto": p.nombre_producto.strip(),
                "empresa": int(p.empresa),
                "nombre_empresa": p.nombre_empresa
            }
            for p in productos
        ]

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bench.route('/get_segmentos', methods=['GET'])
@jwt_required()
@cross_origin()
def get_segmentos():
    try:
        #segmentos = db.session.query(Segmento).all()
        segmentos = db.session.query(Segmento).order_by(Segmento.nombre_segmento.asc()).all()
        resultados = []

        for seg in segmentos:
            modelo = db.session.query(ModeloComercial).filter_by(
                codigo_modelo_comercial=seg.codigo_modelo_comercial,
                codigo_marca=seg.codigo_marca
            ).first()

            marca = db.session.query(Marca).filter_by(codigo_marca=seg.codigo_marca).first()
            linea = db.session.query(Linea).filter_by(codigo_linea=seg.codigo_linea).first()
            linea_padre = db.session.query(Linea).filter_by(codigo_linea=linea.codigo_linea_padre).first() if linea and linea.codigo_linea_padre else None

            resultados.append({
                "codigo_segmento": seg.codigo_segmento,
                "codigo_linea": seg.codigo_linea,
                "nombre_linea": linea.nombre_linea if linea else None,
                "codigo_linea_padre": linea.codigo_linea_padre if linea else None,
                "nombre_linea_padre": linea_padre.nombre_linea if linea_padre else None,
                "codigo_modelo_comercial": seg.codigo_modelo_comercial,
                "nombre_modelo_comercial": modelo.nombre_modelo if modelo else None,
                "codigo_marca": seg.codigo_marca,
                "nombre_marca": marca.nombre_marca if marca else None,
                "nombre_segmento": seg.nombre_segmento,
                "estado_segmento": seg.estado_segmento,
                "descripcion_segmento": seg.descripcion_segmento,
                "usuario_crea": seg.usuario_crea,
                "fecha_creacion": seg.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if seg.fecha_creacion else None,
                "usuario_modifica": seg.usuario_modifica,
                "fecha_modificacion": seg.fecha_modificacion.strftime('%Y-%m-%d %H:%M:%S') if seg.fecha_modificacion else None
            })

        return jsonify(resultados), 200

    except Exception as e:
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500

@bench.route('/get_modelo_version', methods=['GET'])
@jwt_required()
def get_modelo_version():
    try:
        resultados = db.session.query(
            ModeloVersion.codigo_modelo_version,
            ModeloVersion.nombre_modelo_version,
            ModeloVersion.anio_modelo_version,
            ModeloVersion.precio_producto_modelo,
            ModeloVersion.precio_venta_distribuidor,
            DimensionPeso.codigo_dim_peso,
            Imagenes.path_imagen,
            ElectronicaOtros.codigo_electronica,
            Motor.nombre_motor,
            Motor.codigo_motor,
            Motor.codigo_tipo_motor,
            TipoMotor.nombre_tipo.label("nombre_tipo"),
            Transmision.codigo_transmision,
            Transmision.caja_cambios,
            Color.nombre_color,
            Chasis.codigo_chasis,
            ModeloComercial.nombre_modelo.label("nombre_modelo_comercial"),
            Marca.nombre_marca,
            ClienteCanal.codigo_cliente_canal,
            Canal.nombre_canal,
            ClienteCanal.cod_producto,
            Producto.nombre.label("nombre_producto"),
            ClienteCanal.empresa,
            Empresa.nombre.label("nombre_empresa"),
            Version.nombre_version
        ).join(DimensionPeso, ModeloVersion.codigo_dim_peso == DimensionPeso.codigo_dim_peso) \
         .join(Imagenes, ModeloVersion.codigo_imagen == Imagenes.codigo_imagen) \
         .join(ElectronicaOtros, ModeloVersion.codigo_electronica == ElectronicaOtros.codigo_electronica) \
         .join(Motor, (ModeloVersion.codigo_motor == Motor.codigo_motor) & (ModeloVersion.codigo_tipo_motor == Motor.codigo_tipo_motor)) \
         .join(TipoMotor, Motor.codigo_tipo_motor == TipoMotor.codigo_tipo_motor) \
         .join(Transmision, ModeloVersion.codigo_transmision == Transmision.codigo_transmision) \
         .join(Color, ModeloVersion.codigo_color_bench == Color.codigo_color_bench) \
         .join(Chasis, ModeloVersion.codigo_chasis == Chasis.codigo_chasis) \
         .join(ModeloComercial, (ModeloVersion.codigo_modelo_comercial == ModeloComercial.codigo_modelo_comercial) &
                                (ModeloVersion.codigo_marca == ModeloComercial.codigo_marca)) \
         .join(Marca, ModeloVersion.codigo_marca == Marca.codigo_marca) \
         .join(ClienteCanal, (ModeloVersion.codigo_cliente_canal == ClienteCanal.codigo_cliente_canal) &
                             (ModeloVersion.codigo_mod_vers_repuesto == ClienteCanal.codigo_mod_vers_repuesto) &
                             (ModeloVersion.empresa == ClienteCanal.empresa) &
                             (ModeloVersion.cod_producto == ClienteCanal.cod_producto) &
                             (ModeloVersion.codigo_modelo_comercial == ClienteCanal.codigo_modelo_comercial) &
                             (ModeloVersion.codigo_marca == ClienteCanal.codigo_marca)) \
         .join(Canal, ClienteCanal.codigo_cliente_canal == Canal.codigo_canal) \
         .join(Producto, (ClienteCanal.cod_producto == Producto.cod_producto) & (ClienteCanal.empresa == Producto.empresa)) \
         .join(Empresa, ClienteCanal.empresa == Empresa.empresa) \
         .join(Version, ModeloVersion.codigo_version == Version.codigo_version) \
         .all()

        return jsonify([{
            "codigo_modelo_version": r.codigo_modelo_version,
            "nombre_modelo_version": r.nombre_modelo_version,
            "anio_modelo_version": r.anio_modelo_version,
            "precio_producto_modelo": r.precio_producto_modelo,
            "precio_venta_distribuidor": r.precio_venta_distribuidor,
            "codigo_dim_peso": r.codigo_dim_peso,
            "path_imagen": r.path_imagen,
            "codigo_electronica": r.codigo_electronica,
            "nombre_motor": r.nombre_motor,
            "codigo_motor": r.codigo_motor,
            "codigo_tipo_motor": r.codigo_tipo_motor,
            "nombre_tipo_motor": r.nombre_tipo,
            "codigo_transmision": r.codigo_transmision,
            "caja_cambios": r.caja_cambios,
            "nombre_color": r.nombre_color,
            "codigo_chasis": r.codigo_chasis,
            "nombre_modelo_comercial": r.nombre_modelo_comercial,
            "nombre_marca": r.nombre_marca,
            "codigo_cliente_canal": r.codigo_cliente_canal,
            "nombre_canal": r.nombre_canal,
            "cod_producto": r.cod_producto,
            "nombre_producto": r.nombre_producto,
            "empresa": r.empresa,
            "nombre_empresa": r.nombre_empresa,
            "nombre_version": r.nombre_version
        } for r in resultados]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ACTUALIZAR/ MODIFICAR DATOS -------------------------------------------------------------------------->

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

@bench.route('/update_imagen/<int:codigo_imagen>', methods=["PUT"])
@jwt_required()
def update_imagen(codigo_imagen):
    try:
        data = request.json
        user = get_jwt_identity()

        imagen = db.session.query(Imagenes).filter_by(codigo_imagen=codigo_imagen).first()
        if not imagen:
            return jsonify({"error": "Datos de imágenes no encontrados"}), 404

        imagen.path_imagen = data.get("path_imagen", imagen.path_imagen)
        imagen.descripcion_imagen = data.get("descripcion_imagen", imagen.descripcion_imagen)
        imagen.usuario_modifica = user
        imagen.fecha_modificacion = datetime.now()

        db.session.commit()
        return jsonify({"message": "Datos de path/ruta imagen actualizados correctamente", "codigo_imagen": imagen.codigo_imagen})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/update_transmision/<int:codigo_transmision>', methods=["PUT"])
@jwt_required()
def update_transmision(codigo_transmision):
    try:
        data = request.json
        user = get_jwt_identity()

        trans = db.session.query(Transmision).filter_by(codigo_transmision=codigo_transmision).first()
        if not trans:
            return jsonify({"error": "Datos no encontrados"}), 404

        trans.caja_cambios = data.get("caja_cambios", trans.caja_cambios)
        trans.descripcion_transmision = data.get("descripcion_transmision", trans.descripcion_transmision)
        trans.usuario_modifica = user
        trans.fecha_modificacion = datetime.now()

        db.session.commit()
        return jsonify({"message": "Datos actualizados correctamente", "codigo_transmision": trans.codigo_transmision})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/update_canal/<int:codigo_canal>', methods=["PUT"])
@jwt_required()
def update_canal(codigo_canal):
    try:
        data = request.json
        user = get_jwt_identity()

        canal = db.session.query(Canal).filter_by(codigo_canal=codigo_canal).first()
        if not canal:
            return jsonify({"error": "Datos no encontrados"}), 404

        canal.nombre_canal = data.get("nombre_canal", canal.nombre_canal)
        canal.estado_canal = data.get("estado_canal", canal.estado_canal)
        canal.descripcion_canal = data.get("descripcion_canal", canal.descripcion_canal)
        canal.usuario_modifica = user
        canal.fecha_modificacion = datetime.now()

        db.session.commit()
        return jsonify({"message": "Datos actualizados correctamente", "codigo_canal": canal.codigo_canal})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/update_marca_repuesto/<int:codigo_marca_rep>', methods=["PUT"])
@jwt_required()
def update_marca_repuesto(codigo_marca_rep):
    try:
        data = request.get_json()
        user = get_jwt_identity()

        registro = db.session.query(MarcaRepuesto).filter_by(codigo_marca_rep=codigo_marca_rep).first()

        if not registro:
            return jsonify({"error": "Marca de repuesto no encontrada"}), 404

        nombre_comercial = data.get("nombre_comercial", registro.nombre_comercial)
        estado = data.get("estado_marca_rep", registro.estado_marca_rep)
        nombre_fabricante = data.get("nombre_fabricante", registro.nombre_fabricante)

        if isinstance(estado, str):
            estado_normalizado = estado.strip().lower()
            if estado_normalizado == "activo":
                estado = 1
            elif estado_normalizado == "inactivo":
                estado = 0
            else:
                return jsonify({"error": f"Estado inválido: {estado}"}), 400

        if nombre_fabricante and nombre_fabricante.lower() != (registro.nombre_fabricante or '').lower():
            existe = db.session.query(MarcaRepuesto).filter(
                func.lower(MarcaRepuesto.nombre_fabricante) == nombre_fabricante.lower(),
                MarcaRepuesto.codigo_marca_rep != codigo_marca_rep
            ).first()
            if existe:
                return jsonify({"error": "Ya existe una marca con ese nombre de fabricante"}), 409

        registro.nombre_comercial = nombre_comercial
        registro.estado_marca_rep = estado
        registro.nombre_fabricante = nombre_fabricante
        registro.usuario_modifica = user
        registro.fecha_modificacion = datetime.now()

        db.session.commit()

        return jsonify({"message": "Marca de repuesto actualizada correctamente"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/update_producto_externo/<string:codigo_prod_externo>', methods=["PUT"])
@jwt_required()
def update_producto_externo(codigo_prod_externo):
    try:
        data = request.get_json()
        user = get_jwt_identity()

        registro = db.session.query(ProductoExterno).filter_by(codigo_prod_externo=codigo_prod_externo).first()

        if not registro:
            return jsonify({"error": "Producto externo no encontrado"}), 404

        nombre_producto = data.get("nombre_producto", registro.nombre_producto)
        estado = data.get("estado_prod_externo", registro.estado_prod_externo)
        descripcion_producto = data.get("descripcion_producto", registro.descripcion_producto)
        empresa = data.get("empresa", registro.empresa)

        if isinstance(estado, str):
            estado_normalizado = estado.strip().lower()
            if estado_normalizado == "activo":
                estado = 1
            elif estado_normalizado == "inactivo":
                estado = 0
            else:
                return jsonify({"error": f"Estado inválido: {estado}"}), 400

        nuevo_nombre = nombre_producto.lower()
        nueva_marca = data.get("codigo_marca_rep", registro.codigo_marca_rep)

        if (nuevo_nombre != registro.nombre_producto.lower()) or (nueva_marca != registro.codigo_marca_rep):
            existe = db.session.query(ProductoExterno).filter(
                ProductoExterno.nombre_producto.ilike(nombre_producto),
                ProductoExterno.codigo_marca_rep == nueva_marca,
                ProductoExterno.codigo_prod_externo != codigo_prod_externo
            ).first()
            if existe:
                return jsonify({"error": "Ya existe un producto con ese nombre en la misma marca"}), 409

        registro.nombre_producto = nombre_producto
        registro.estado_prod_externo = estado
        registro.descripcion_producto = descripcion_producto
        registro.empresa = empresa
        registro.usuario_modifica = user
        registro.fecha_modificacion = datetime.now()

        db.session.commit()

        return jsonify({"message": "Producto externo actualizado correctamente"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/update_version/<int:codigo_version>', methods=["PUT"])
@jwt_required()
def update_version(codigo_version):
    try:
        data = request.get_json()
        user = get_jwt_identity()

        registro = db.session.query(Version).filter_by(codigo_version=codigo_version).first()

        if not registro:
            return jsonify({"error": "Versión no encontrada"}), 404

        nombre_version = data.get("nombre_version", registro.nombre_version)
        estado = data.get("estado_version", registro.estado_version)
        descripcion_version = data.get("descripcion_version", registro.descripcion_version)

        if isinstance(estado, str):
            estado_normalizado = estado.strip().lower()
            if estado_normalizado == "activo":
                estado = 1
            elif estado_normalizado == "inactivo":
                estado = 0
            else:
                return jsonify({"error": f"Estado inválido: {estado}"}), 400

        if nombre_version and nombre_version.lower() != (registro.nombre_version or '').lower():
            existe = db.session.query(Version).filter(
                func.lower(Version.nombre_version) == nombre_version.lower(),
                Version.codigo_version != codigo_version
            ).first()
            if existe:
                return jsonify({"error": "Ya existe una marca con ese nombre de fabricante"}), 409

        registro.nombre_version = nombre_version
        registro.estado_version = estado
        registro.descripcion_version = descripcion_version
        registro.usuario_modifica = user
        registro.fecha_modificacion = datetime.now()

        db.session.commit()

        return jsonify({"message": "Versión actualizada correctamente"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/update_linea/<int:codigo_linea>', methods=["PUT"])
@jwt_required()
def update_linea(codigo_linea):
    try:
        data = request.json
        user = get_jwt_identity()

        linea = db.session.query(Linea).filter_by(codigo_linea=codigo_linea).first()
        if not linea:
            return jsonify({"error": "Línea no encontrada"}), 404

        nuevo_nombre = data.get("nombre_linea")
        if nuevo_nombre and nuevo_nombre.lower() != linea.nombre_linea.lower():
            existe = db.session.query(Linea).filter(
                func.lower(Linea.nombre_linea) == nuevo_nombre.lower(),
                Linea.codigo_linea != codigo_linea
            ).first()
            if existe:
                return jsonify({"error": "Ya existe una línea con ese nombre"}), 409
            linea.nombre_linea = nuevo_nombre

        linea.estado_linea = data.get("estado_linea", linea.estado_linea)
        linea.descripcion_linea = data.get("descripcion_linea", linea.descripcion_linea)
        linea.usuario_modifica = user
        linea.fecha_modificacion = datetime.now()

        codigo_padre = data.get("codigo_linea_padre")
        if codigo_padre:
            if codigo_padre == codigo_linea:
                return jsonify({"error": "Una línea no puede ser su propio padre"}), 400
            padre = db.session.query(Linea).filter_by(codigo_linea=codigo_padre).first()
            if not padre:
                return jsonify({"error": "La línea padre no existe"}), 404
            linea.codigo_linea_padre = codigo_padre

        db.session.commit()
        return jsonify({"message": "Línea actualizada correctamente"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/update_modelo_sri/<int:codigo_modelo_sri>', methods=["PUT"])
@jwt_required()
def update_modelo_sri(codigo_modelo_sri):
    try:
        data = request.get_json()
        user = get_jwt_identity()

        modelo = db.session.query(ModeloSRI).filter_by(codigo_modelo_sri=codigo_modelo_sri).first()
        if not modelo:
            return jsonify({"error": "Modelo no encontrado"}), 404

        nombre = data.get("nombre_modelo")
        anio = data.get("anio_modelo")
        estado = data.get("estado_modelo")

        if nombre:
            existe_nombre = db.session.query(ModeloSRI).filter(
                func.lower(ModeloSRI.nombre_modelo) == nombre.lower(),
                ModeloSRI.codigo_modelo_sri != codigo_modelo_sri
            ).first()
            if existe_nombre:
                return jsonify({"error": "Ya existe otro modelo con ese nombre"}), 409
            modelo.nombre_modelo = nombre

        if anio and (1950 <= int(anio) <= 2100):
            modelo.anio_modelo = int(anio)

        if estado in [0, 1]:
            modelo.estado_modelo = estado

        modelo.usuario_modifica = user
        modelo.fecha_modificacion = datetime.now()

        db.session.commit()

        return jsonify({"message": "Modelo actualizado correctamente"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/update_modelo_homologado/<int:codigo>', methods=["PUT"])
@jwt_required()
def update_modelo_homologado(codigo):
    try:
        data = request.get_json()
        user = get_jwt_identity()

        modelo = db.session.query(ModeloHomologado).filter_by(codigo_modelo_homologado=codigo).first()
        if not modelo:
            return jsonify({"error": "Registro no encontrado"}), 404

        nuevo_codigo_sri = data.get("codigo_modelo_sri")
        descripcion = data.get("descripcion_homologacion")

        if nuevo_codigo_sri:
            existe = db.session.query(ModeloSRI).filter_by(codigo_modelo_sri=nuevo_codigo_sri).first()
            if not existe:
                return jsonify({"error": "Código modelo SRI inválido"}), 400
            modelo.codigo_modelo_sri = nuevo_codigo_sri

        if descripcion is not None:
            modelo.descripcion_homologacion = descripcion

        modelo.usuario_modifica = user
        modelo.fecha_modificacion = datetime.now()

        db.session.commit()
        return jsonify({"message": "Homologación actualizada correctamente"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/update_modelo_comercial/<int:codigo>', methods=['PUT'])
@jwt_required()
@cross_origin()
def update_modelo_comercial(codigo):
    try:
        user = get_jwt_identity()
        data = request.get_json()

        nombre_marca = data.get("nombre_marca")
        codigo_modelo_homologado = data.get("codigo_modelo_homologado")
        nombre_modelo = data.get("nombre_modelo")
        anio_modelo = data.get("anio_modelo")
        estado_modelo = data.get("estado_modelo")

        if not nombre_marca or not nombre_modelo or not codigo_modelo_homologado or not anio_modelo:
            return jsonify({"error": "Faltan campos obligatorios"}), 400

        marca = db.session.query(Marca).filter(
            func.lower(func.replace(func.trim(Marca.nombre_marca), '\u00A0', ' ')) == normalize(nombre_marca)
        ).first()

        if not marca:
            marca = Marca(
                nombre_marca=nombre_marca.strip(),
                usuario_crea=user,
                fecha_creacion=datetime.now()
            )
            db.session.add(marca)
            db.session.flush()

        modelo = db.session.query(ModeloComercial).filter_by(codigo_modelo_comercial=codigo).first()

        if not modelo:
            return jsonify({"error": "Modelo comercial no encontrado"}), 404

        modelo.codigo_marca = marca.codigo_marca
        modelo.codigo_modelo_homologado = codigo_modelo_homologado
        modelo.nombre_modelo = nombre_modelo.strip()
        modelo.anio_modelo = int(anio_modelo)
        modelo.estado_modelo = int(estado_modelo)
        modelo.usuario_modifica = user
        modelo.fecha_modificacion = datetime.now()

        db.session.commit()
        return jsonify({"message": "Modelo comercial actualizado correctamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/update_modelo_version_repuesto/<int:codigo>', methods=['PUT', 'OPTIONS'])
@jwt_required()
@cross_origin(methods=["PUT", "OPTIONS"])
def update_modelo_version_repuesto(codigo):
    try:
        data = request.get_json()

        required_fields = ["cod_producto", "codigo_marca", "codigo_modelo_comercial", "empresa",
                           "codigo_version", "codigo_prod_externo", "descripcion",
                           "precio_producto_modelo", "precio_venta_distribuidor"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo obligatorio faltante: {field}"}), 400

        registro = db.session.query(ModeloVersionRepuesto).filter_by(codigo_mod_vers_repuesto=codigo).first()
        if not registro:
            return jsonify({"error": "Registro no encontrado"}), 404

        producto = db.session.query(Producto).filter_by(empresa=data["empresa"], cod_producto=data["cod_producto"]).first()
        modelo = db.session.query(ModeloComercial).filter_by(
            codigo_modelo_comercial=data["codigo_modelo_comercial"],
            codigo_marca=data["codigo_marca"]
        ).first()
        version = db.session.query(Version).filter_by(codigo_version=data["codigo_version"]).first()
        prod_ext = db.session.query(ProductoExterno).filter_by(codigo_prod_externo=data["codigo_prod_externo"]).first()

        if not all([producto, modelo, version, prod_ext]):
            return jsonify({"error": "Alguna FK referenciada no existe"}), 409

        registro.cod_producto = data["cod_producto"]
        registro.codigo_marca = data["codigo_marca"]
        registro.codigo_modelo_comercial = data["codigo_modelo_comercial"]
        registro.empresa = data["empresa"]
        registro.codigo_version = data["codigo_version"]
        registro.codigo_prod_externo = data["codigo_prod_externo"]
        registro.descripcion = data["descripcion"]
        registro.precio_producto_modelo = data["precio_producto_modelo"]
        registro.precio_venta_distribuidor = data["precio_venta_distribuidor"]

        db.session.commit()
        return jsonify({"message": "Registro actualizado correctamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/update_cliente_canal/<int:codigo>', methods=['PUT'])
@jwt_required()
@cross_origin()
def update_cliente_canal(codigo):
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Datos JSON no proporcionados"}), 400

        cliente = db.session.query(ClienteCanal).filter_by(codigo_cliente_canal=codigo).first()

        if not cliente:
            return jsonify({"error": f"Cliente canal con ID {codigo} no encontrado"}), 404

        campos_obligatorios = ['codigo_canal', 'codigo_mod_vers_repuesto', 'cod_producto', 'empresa']
        for campo in campos_obligatorios:
            if campo not in data:
                return jsonify({"error": f"Campo obligatorio '{campo}' faltante"}), 400

        cliente.codigo_canal = data.get('codigo_canal')
        cliente.codigo_mod_vers_repuesto = data.get('codigo_mod_vers_repuesto')
        cliente.cod_producto = data.get('cod_producto')
        cliente.empresa = data.get('empresa')
        cliente.codigo_modelo_comercial = data.get('codigo_modelo_comercial')
        cliente.codigo_marca = data.get('codigo_marca')
        cliente.codigo_version = data.get('codigo_version')  # si corresponde en tu modelo
        cliente.descripcion_cliente_canal = data.get('descripcion_cliente_canal', '')

        db.session.commit()

        return jsonify({"mensaje": "Registro actualizado correctamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar: {str(e)}"}), 500

@bench.route('/update_segmento/<int:codigo_segmento>', methods=['PUT'])
@jwt_required()
def update_segmento(codigo_segmento):
    data = request.get_json()

    segmento = db.session.query(Segmento).filter_by(codigo_segmento=codigo_segmento).first()
    if not segmento:
        return jsonify({"error": "Segmento no encontrado"}), 404

    try:
        segmento.codigo_linea = data.get('codigo_linea')
        segmento.codigo_linea_padre = data.get('codigo_linea_padre')
        segmento.codigo_modelo_comercial = data.get('codigo_modelo_comercial')
        segmento.codigo_marca = data.get('codigo_marca')
        segmento.nombre_segmento = data.get('nombre_segmento')
        segmento.descripcion_segmento = data.get('descripcion_segmento', '')
        segmento.estado_segmento = data.get('estado_segmento')

        segmento.fecha_modificacion = datetime.now()
        segmento.usuario_modifica = get_jwt_identity()

        db.session.commit()
        return jsonify({"message": "Segmento actualizado correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bench.route('/update_modelo_version/<int:codigo_modelo_version>', methods=["PUT"])
@jwt_required()
def update_modelo_version(codigo_modelo_version):
    try:
        data = request.json
        modelo_version = db.session.query(ModeloVersion).filter_by(codigo_modelo_version=codigo_modelo_version).first()
        if not modelo_version:
            return jsonify({"error": "Modelo versión no encontrado"}), 404

        imagen = db.session.query(Imagenes).filter_by(descripcion_imagen=data["descripcion_imagen"]).first()
        motor = db.session.query(Motor).filter_by(nombre_motor=data["nombre_motor"]).first()
        color = db.session.query(Color).filter_by(nombre_color=data["nombre_color"]).first()
        modelo = db.session.query(ModeloComercial).filter_by(nombre_modelo=data["nombre_modelo_comercial"]).first()
        version = db.session.query(Version).filter_by(nombre_version=data["nombre_version"]).first()

        modelo_version.codigo_dim_peso = data["codigo_dim_peso"]
        modelo_version.codigo_imagen = imagen.codigo_imagen
        modelo_version.codigo_electronica = data["codigo_electronica"]
        modelo_version.codigo_motor = motor.codigo_motor
        modelo_version.codigo_tipo_motor = data["codigo_tipo_motor"]
        modelo_version.codigo_transmision = data["codigo_transmision"]
        modelo_version.codigo_color_bench = color.codigo_color_bench
        modelo_version.codigo_chasis = data["codigo_chasis"]
        modelo_version.codigo_modelo_comercial = modelo.codigo_modelo_comercial
        modelo_version.codigo_marca = modelo.codigo_marca
        modelo_version.codigo_cliente_canal = data["codigo_cliente_canal"]
        modelo_version.codigo_mod_vers_repuesto = data["codigo_mod_vers_repuesto"]
        modelo_version.empresa = data["empresa"]
        modelo_version.cod_producto = data["cod_producto"]
        modelo_version.codigo_version = version.codigo_version
        modelo_version.nombre_modelo_version = data["nombre_modelo_version"]
        modelo_version.anio_modelo_version = data["anio_modelo_version"]
        modelo_version.precio_producto_modelo = data["precio_producto_modelo"]
        modelo_version.precio_venta_distribuidor = data["precio_venta_distribuidor"]

        db.session.commit()

        return jsonify({"message": "Modelo versión actualizado correctamente"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500