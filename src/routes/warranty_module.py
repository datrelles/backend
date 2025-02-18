from flask_jwt_extended import jwt_required
from flask import Blueprint, jsonify, request
from src import oracle
from src.models.postVenta import ar_taller_servicio_tecnico, ADprovincias, ADcantones, ar_duracion_reparacion, st_casos_postventa, ar_taller_servicio_usuario
from src.models.clientes import Cliente
from src.models.users import Usuario, tg_rol_usuario
from sqlalchemy import (and_)
import cx_Oracle
from os import getenv
import json
from datetime import datetime, date
from src.config.database import db
#here modules

import logging

rmwa = Blueprint('routes_module_warranty', __name__)

#check information by engine code
@rmwa.route('/check_info_bye_engine_code', methods=['GET'])
@jwt_required()
def check_info_bye_engine_code():
    engine_code = request.args.get('engine_code')
    if not engine_code:
        return jsonify({'error': 'El parámetro engine_code es requerido.'}), 400

    info_moto = oracle.infoMotor(engine_code)

    dict_info_motor = {
                            "RUC_DISTRIBUIDOR": info_moto[0],
                            "COD_PRODUCTO": info_moto[1],
                            "COD_CHASIS":info_moto[2],
                            "IMPORTACION":info_moto[3],
                            "NOMBRE_DISTRIBUIDOR": info_moto[4],
                            "COD_MOTOR": engine_code
                      }
    return jsonify(dict_info_motor)

@rmwa.route('/get_info_active_talleres', methods=['GET'])
@jwt_required()
def get_talleres_authorized_warranty():
    status = int(request.args.get('active'))
    enterprise = request.args.get('enterprise')

    if status == 1:
        status = 'N'
    elif status == 0:
        status = 'S'
    else:
        return jsonify({'error': 'The active parameter can only be 1 or 0.'}), 400

    # Using ar_taller_servicio_tecnico.query without explicit db.session
    query = (
        ar_taller_servicio_tecnico.query()
        .join(
            ADprovincias,
            and_(
                ar_taller_servicio_tecnico.cod_provincia == ADprovincias.codigo_provincia,
                ar_taller_servicio_tecnico.cod_nacion == ADprovincias.codigo_nacion
            )
        )
        .join(
            ADcantones,
            and_(
                ar_taller_servicio_tecnico.cod_provincia == ADcantones.codigo_provincia,
                ar_taller_servicio_tecnico.cod_nacion == ADcantones.codigo_nacion,
                ar_taller_servicio_tecnico.cod_canton == ADcantones.codigo_canton
            )
        )
        .filter(ar_taller_servicio_tecnico.anulado == status)
        .filter(ar_taller_servicio_tecnico.codigo_empresa == enterprise)
        .with_entities(
            ar_taller_servicio_tecnico.codigo.label('codigo'),
            ar_taller_servicio_tecnico.descripcion.label('taller'),
            ADprovincias.descripcion.label('provincia'),
            ADcantones.descripcion.label('canton'),
            ADcantones.codigo_canton.label('codigo_canton'),
            ADcantones.codigo_provincia.label('codigo_provincia')
        )
    )

    results = query.all()

    data = []
    for row in results:
        data.append({
            'codigo': row.codigo,
            'taller': row.taller,
            'provincia': row.provincia,
            'canton': row.canton,
            'codigo_canton': row.codigo_canton,
            'codigo_provincia': row.codigo_provincia
        })

    return jsonify(data), 200


@rmwa.route('/get_cliente_data_for_id', methods=['GET'])
@jwt_required()
def get_cliente_data_for_id():
    # Obtener parámetros de la query string
    cod_cliente = request.args.get('cod_cliente', None)
    enterprise = request.args.get('enterprise', None)

    # Validar si ambos parámetros fueron proporcionados
    if not cod_cliente or not enterprise:
        return jsonify({"error": "Missing parameters: 'cod_cliente' and/or 'enterprise'"}), 400

    try:
        # 1) Intentar la consulta SIN guion
        cliente = (
            Cliente.query()
            .filter(
                Cliente.cod_cliente == cod_cliente,
                Cliente.empresa == enterprise
            )
            .first()
        )

        # 2) Si no encuentra resultados, intentar con guion
        if not cliente:
            cod_cliente_with_dash = add_dash_before_last_digit(cod_cliente)
            cliente = (
                Cliente.query()
                .filter(
                    Cliente.cod_cliente == cod_cliente_with_dash,
                    Cliente.empresa == enterprise
                )
                .first()
            )
            # Si sigue sin encontrar resultados, retornamos error 404
            if not cliente:
                return jsonify({"error": "Client not found"}), 404

        # Preparar la respuesta como un diccionario
        data = {
            "empresa": cliente.empresa,
            "cod_cliente": cliente.cod_cliente,
            "cod_tipo_identificacion": cliente.cod_tipo_identificacion,
            "nombre": cliente.nombre,
            "apellido1": cliente.apellido1,
            "ruc": cliente.ruc
        }

        return jsonify(data), 200

    except Exception as e:
        # Manejar cualquier error inesperado
        return jsonify({"error": str(e)}), 500
def add_dash_before_last_digit(cod_cliente: str) -> str:
    if len(cod_cliente) < 2:
        return cod_cliente
    return cod_cliente[:-1] + '-' + cod_cliente[-1]


@rmwa.route('/get_list_tipo_problema', methods=['GET'])
@jwt_required()
def get_duracion_reparacion():
    try:
        results = (
            ar_duracion_reparacion.query()
            .filter(
                ar_duracion_reparacion.tipo_duracion == 'N',
                ar_duracion_reparacion.codigo_empresa == 20
            )
            .with_entities(
                ar_duracion_reparacion.descripcion.label('tipo_problema'),
                ar_duracion_reparacion.codigo_duracion.label('codigo')
            )
            .all()
        )

        # Prepare a list of dictionaries for JSON response
        data = []
        for row in results:
            data.append({
                "tipo_problema": row.tipo_problema,
                "codigo": str(row.codigo)  # Convert NUMBER to string
            })

        return jsonify(data), 200

    except Exception as e:
        # Handle any unexpected error
        return jsonify({"error": str(e)}), 500

@rmwa.route('/save_post_case_warranty', methods=['POST'])
@jwt_required()
def warranty():
    c = None
    try:
        # 1. Parse request body
        dataCaso = json.loads(request.data)
        userShineray = request.args.get('userShineray')
        enterpriseShineray = request.args.get('enterpriseShineray')

        # 2. Validate required fields
        validacion_exitosa, mensaje_error = validar_campos(dataCaso)
        if not validacion_exitosa:
            return jsonify({"error": mensaje_error}), 400

        # 3. Convert string values to uppercase, handle exceptions
        for clave, valor in dataCaso.items():
            try:
                dataCaso[clave] = str(valor).upper()
            except AttributeError:
                print(f"Warning: The key '{clave}' has a value that cannot be converted to uppercase.")

        # 4. Set additional fields
        set_non_variable_data(dataCaso, userShineray, enterpriseShineray)

        # -----------------------------------------
        # Open the DB connection once
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        # -----------------------------------------

        # 5. Get info from 'taller'
        taller_ok, taller_response = get_taller_info(dataCaso, c)
        if not taller_ok:
            # If fail, raise an exception so we can rollback
            raise RuntimeError(taller_response.json['error'])

        # 6. Get motor info
        motor_ok, motor_response = get_motor_info(dataCaso)
        if not motor_ok:
            # If fail, raise an exception so we can rollback
            raise RuntimeError(motor_response.json['error'])

        # 7. Insert into ST_CASOS_POSTVENTA + generate 'cod_comprobante'
        data_st_casos_post_venta = dataCaso.copy()
        # Remove 'PROBLEMAS' from the copy so it won't be in the insert
        data_st_casos_post_venta.pop("PROBLEMAS", None)
        generate_comprobante_code(data_st_casos_post_venta, dataCaso, c)

        # 8. Save problem types in ST_CASOS_TIPO_PROBLEMA
        save_cod_tipo_problema(dataCaso, c)

        # If everything worked, commit the transaction
        c.commit()

        return jsonify({"casoData": dataCaso}), 200

    except Exception as e:
        # Roll back if ANY step fails
        if c:
            c.rollback()
        print(f"Error in warranty process: {e}")
        return jsonify({'Error en el registro del caso': str(e)}), 500

    finally:
        if c:
            c.close()
def validar_campos(data):
    """
    Checks for the presence of required fields in 'data'.
    Returns (False, <error_message>) if missing. Otherwise, (True, None).
    """
    campos_necesarios = [
        "NOMBRE_CASO",
        "DESCRIPCION",
        "NOMBRE_CLIENTE",
        "COD_TIPO_IDENTIFICACION",
        "IDENTIFICACION_CLIENTE",
        "COD_MOTOR",
        "KILOMETRAJE",
        "CODIGO_TALLER",
        "COD_TIPO_PROBLEMA"
    ]
    for campo in campos_necesarios:
        if campo not in data:
            return False, f"Falta el campo {campo} en el JSON recibido."
    return True, None
def set_non_variable_data(data, userShineray, enterpriseShineray):
    """
    Sets additional fields that are constant or derived.
    """
    data['EMPRESA'] = enterpriseShineray
    data['TIPO_COMPROBANTE'] = 'CP'

    # Convert 'FECHA' to datetime
    fecha_formateada = datetime.strptime(data['FECHA'], '%Y/%m/%d %H:%M:%S')
    data['FECHA'] = fecha_formateada

    data['CODIGO_NACION'] = 1
    data['CODIGO_RESPONSABLE'] = userShineray
    data['COD_CANAL'] = 5
    data['ADICIONADO_POR'] = userShineray

    # Convert 'FECHA_VENTA' to datetime
    fecha_venta = datetime.strptime(data['FECHA_VENTA'], '%Y/%m')
    data['FECHA_VENTA'] = fecha_venta

    data['APLICA_GARANTIA'] = 2
def generate_comprobante_code(data, dataCaso, c):
    """
    Calls the PL/SQL procedure to generate 'cod_comprobante'
    and inserts a row in ST_CASOS_POSTVENTA.
    Uses the open connection 'c' to execute statements.
    """
    cur = None
    try:
        v_cod_empresa = 20
        v_cod_tipo_comprobante = 'CP'
        v_cod_agencia = 1

        query = """
        DECLARE
          v_cod_empresa           FLOAT := :1;
          v_cod_tipo_comprobante  VARCHAR2(50) := :2;
          v_cod_agencia           FLOAT := :3;
          v_result                VARCHAR2(50);
        BEGIN
          v_result := KC_ORDEN.asigna_cod_comprobante(
                          p_cod_empresa => v_cod_empresa,
                          p_cod_tipo_comprobante => v_cod_tipo_comprobante,
                          p_cod_agencia => v_cod_agencia
          );
          :4 := v_result;
        END;
        """

        cur = c.cursor()
        result_var = cur.var(cx_Oracle.STRING)
        cur.execute(query, (v_cod_empresa, v_cod_tipo_comprobante, v_cod_agencia, result_var))
        result = result_var.getvalue()

        # Store 'cod_comprobante' in both dictionaries
        dataCaso['COD_COMPROBANTE'] = result
        data['COD_COMPROBANTE'] = result

        # Insert into ST_CASOS_POSTVENTA
        sql_insert = """
        INSERT INTO ST_CASOS_POSTVENTA (
            nombre_caso, descripcion, nombre_cliente, cod_tipo_identificacion, identificacion_cliente,
            cod_motor, kilometraje, codigo_taller, cod_tipo_problema, fecha_venta, manual_garantia,
            telefono_contacto1, telefono_contacto2, e_mail1, empresa, tipo_comprobante, fecha,
            codigo_nacion, codigo_responsable, cod_canal, adicionado_por, codigo_provincia,
            codigo_canton, cod_producto, cod_distribuidor_cli, cod_comprobante, aplica_garantia
        ) VALUES (
            :NOMBRE_CASO, :DESCRIPCION, :NOMBRE_CLIENTE, :COD_TIPO_IDENTIFICACION, :IDENTIFICACION_CLIENTE,
            :COD_MOTOR, :KILOMETRAJE, :CODIGO_TALLER, :COD_TIPO_PROBLEMA, :FECHA_VENTA, :MANUAL_GARANTIA,
            :TELEFONO_CONTACTO1, :TELEFONO_CONTACTO2, :E_MAIL, :EMPRESA, :TIPO_COMPROBANTE, :FECHA,
            :CODIGO_NACION, :CODIGO_RESPONSABLE, :COD_CANAL, :ADICIONADO_POR, :CODIGO_PROVINCIA,
            :CODIGO_CANTON, :COD_PRODUCTO, :COD_DISTRIBUIDOR_CLI, :COD_COMPROBANTE, :APLICA_GARANTIA
        )
        """
        cur.execute(sql_insert, data)

    except Exception as e:
        raise RuntimeError(f"Error in 'generate_comprobante_code': {e}") from e
    finally:
        if cur:
            cur.close()

def get_taller_info(data, c):
    """
    Retrieves COD_PROVINCIA and COD_CANTON from AR_TALLER_SERVICIO_TECNICO
    based on 'CODIGO_TALLER', using the open connection 'c'.
    """
    cur = None
    try:
        id_taller = data['CODIGO_TALLER']
        if not id_taller:
            return False, jsonify({"error": "Se requiere el campo 'CODIGO_TALLER'"}), 400

        query = """
            SELECT COD_PROVINCIA, COD_CANTON
            FROM AR_TALLER_SERVICIO_TECNICO
            WHERE CODIGO = :1
        """

        cur = c.cursor()
        cur.execute(query, (id_taller,))
        city = cur.fetchall()

        if not city:
            return False, jsonify({"error": f"No se encontró taller con código {id_taller}"}), 404

        data['CODIGO_PROVINCIA'] = city[0][0]
        data['CODIGO_CANTON'] = city[0][1]
        return True, data

    except Exception as e:
        return False, jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
def get_motor_info(data):
    try:
        num_motor = data['COD_MOTOR']
        if not num_motor:
            return False, jsonify({"error": "Se requiere el campo 'COD_MOTOR'"}), 400

        data_motor = oracle.infoMotor(num_motor)
        data['COD_PRODUCTO'] = data_motor[1]
        data['COD_DISTRIBUIDOR_CLI'] = data_motor[0]
        return True, data

    except Exception as e:
        return False, jsonify({"error": str(e)}), 500
def save_cod_tipo_problema(data, c):

    cur = None
    try:
        sql = """
        INSERT INTO ST_CASOS_TIPO_PROBLEMA
        (empresa, tipo_comprobante, cod_comprobante, codigo_duracion, adicionado_por, descripcion)
        VALUES
        (:empresa, :tipo_comprobante, :cod_comprobante, :codigo_duracion, :adicionado_por, :descripcion)
        """

        problemas_str = data.get("PROBLEMAS", "[]")
        problemas_str = problemas_str.replace("'", '"')  # Convert single quotes to double quotes
        problemas_list = json.loads(problemas_str)

        empresa = 20
        cod_comprobante = data["COD_COMPROBANTE"]
        tipo_comprobante = data["TIPO_COMPROBANTE"]
        adicionado_por = 'SHIBOT'

        cur = c.cursor()
        for problema in problemas_list:
            params_insert = {
                'empresa': empresa,
                'tipo_comprobante': tipo_comprobante,
                'cod_comprobante': cod_comprobante,
                'codigo_duracion': problema["CODIGO_TIPO_PROBLEMA"],
                'adicionado_por': adicionado_por,
                'descripcion': problema["DESCRIPCION_DEL_PROBLEMA"],
            }
            cur.execute(sql, params_insert)

    except Exception as e:
        raise RuntimeError(f"Error in 'save_cod_tipo_problema': {e}") from e
    finally:
        if cur:
            cur.close()

@rmwa.route('/get_caso_postventa', methods=['GET'])
@jwt_required()
def get_caso_postventa():
    """
    Endpoint que retorna la información de un caso postventa según
    las claves primarias empresa, tipo_comprobante y cod_comprobante.

    Query Params:
        - empresa (int)
        - tipo_comprobante (str)
        - cod_comprobante (str)
    """

    # 1. Obtener parámetros de la query string
    empresa = request.args.get('empresa')
    tipo_comprobante = request.args.get('tipo_comprobante')
    cod_comprobante = request.args.get('cod_comprobante')

    # 2. Validar si los parámetros fueron proporcionados
    if not empresa or not tipo_comprobante or not cod_comprobante:
        return jsonify({"error": "Missing parameters: 'empresa', 'tipo_comprobante', 'cod_comprobante'"}), 400

    try:
        #  Convertir empresa a numérico
        empresa_int = int(empresa)

        caso = (
            st_casos_postventa.query()
            .filter(
                st_casos_postventa.empresa == empresa_int,
                st_casos_postventa.tipo_comprobante == tipo_comprobante,
                st_casos_postventa.cod_comprobante == cod_comprobante
            )
            .first()
        )

        if not caso:
            return jsonify({"error": "Caso Postventa no encontrado"}), 404

        #  Preparar la respuesta como un diccionario
        #    (A continuación se listan todas las columnas del modelo.
        data = {
            "empresa": caso.empresa,
            "tipo_comprobante": caso.tipo_comprobante,
            "cod_comprobante": caso.cod_comprobante,
            "fecha": caso.fecha.isoformat() if caso.fecha else None,
            "nombre_caso": caso.nombre_caso,
            "descripcion": caso.descripcion,
            "codigo_nacion": caso.codigo_nacion,
            "codigo_provincia": caso.codigo_provincia,
            "codigo_canton": caso.codigo_canton,
            "nombre_cliente": caso.nombre_cliente,
            "cod_producto": caso.cod_producto,
            "cod_motor": caso.cod_motor,
            "kilometraje": float(caso.kilometraje) if caso.kilometraje else None,
            "codigo_taller": caso.codigo_taller,
            "codigo_responsable": caso.codigo_responsable,
            "cod_tipo_problema": caso.cod_tipo_problema,
            "aplica_garantia": caso.aplica_garantia,
            "adicionado_por": caso.adicionado_por,
            "fecha_adicion": caso.fecha_adicion.isoformat() if caso.fecha_adicion else None,
            "cod_distribuidor": caso.cod_distribuidor,
            "manual_garantia": caso.manual_garantia,
            "estado": caso.estado,
            "fecha_cierre": caso.fecha_cierre.isoformat() if caso.fecha_cierre else None,
            "usuario_cierra": caso.usuario_cierra,
            "observacion_final": caso.observacion_final,
            "identificacion_cliente": caso.identificacion_cliente,
            "telefono_contacto1": caso.telefono_contacto1,
            "telefono_contacto2": caso.telefono_contacto2,
            "telefono_contacto3": caso.telefono_contacto3,
            "e_mail1": caso.e_mail1,
            "e_mail2": caso.e_mail2,
            "cod_tipo_identificacion": caso.cod_tipo_identificacion,
            "cod_agente": caso.cod_agente,
            "cod_pedido": caso.cod_pedido,
            "cod_tipo_pedido": caso.cod_tipo_pedido,
            "numero_guia": caso.numero_guia,
            "cod_distribuidor_cli": caso.cod_distribuidor_cli,
            "fecha_venta": caso.fecha_venta.isoformat() if caso.fecha_venta else None,
            "es_cliente_contactado": caso.es_cliente_contactado,
            "cod_canal": caso.cod_canal,
            "referencia": caso.referencia,
            "aplica_excepcion": caso.aplica_excepcion,
            "cod_empleado": caso.cod_empleado,
            "cod_tipo_persona": caso.cod_tipo_persona
        }

        return jsonify(data), 200

    except ValueError:
        # Esto puede ocurrir si empresa no se puede convertir a int
        return jsonify({"error": "El parámetro 'empresa' debe ser un número válido"}), 400
    except Exception as e:
        # 8. Manejar cualquier otro error inesperado
        return jsonify({"error": str(e)}), 500


@rmwa.route('/get_usuarios_rol_astgar', methods=['GET'])
@jwt_required()
def get_usuarios_rol_astgar():
    """
    Endpoint que retorna la información de los usuarios asociados al rol 'ASTGAR'.

    Retorna:
        - usuario: Código de usuario.
        - nombre: Nombre del usuario.
        - apellido1: Primer apellido del usuario.
    """
    try:
        # Usamos el método de clase query() del mapeo TgRolUsuario
        resultados = (
            tg_rol_usuario.query()
            .join(Usuario, Usuario.usuario_oracle == tg_rol_usuario.usuario)
            .filter(tg_rol_usuario.cod_rol == 'ASTGAR')
            .with_entities(tg_rol_usuario.usuario, Usuario.nombre, Usuario.apellido1)
            .all()
        )

        if not resultados:
            return jsonify({"error": "No se encontraron usuarios para el rol ASTGAR"}), 404

        # Preparar la respuesta en formato JSON
        data = [
            {
                "usuario": usuario,
                "nombre": nombre,
                "apellido1": apellido1
            }
            for usuario, nombre, apellido1 in resultados
        ]

        return jsonify(data), 200

    except Exception as e:
        # Manejar cualquier error inesperado
        print(e)
        return jsonify({"error": str(e)}), 500


@rmwa.route('/assign_taller_usuario', methods=['POST'])
@jwt_required()
def assign_taller_usuario():
    """
    Endpoint to insert a new record into the AR_TALLER_SERVICIO_USUARIO table.

    Expects a JSON payload with at least:
      - empresa (int)
      - codigo_taller (str)
      - cod_rol (str)
      - usuario (str)

    Optional fields:
      - activo (int) [0 or 1, defaults to 1]
      - adicionado_por (str) [defaults to 'USER']
      - fecha_adicion (datetime) [defaults to SYSDATE]
      - modificado_por (str)
      - fecha_modificacion (datetime)

    Example JSON body:
    {
      "empresa": 20,
      "codigo_taller": "T123",
      "cod_rol": "ASTGAR",
      "usuario": "AMENDOZA",
      "activo": 1
    }
    """
    try:
        # 1) Retrieve JSON data from the request body
        data = request.get_json()

        # 2) Validate required fields
        required_fields = ["empresa", "codigo_taller", "cod_rol", "usuario"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: '{field}'"}), 400

        # 3) Create the SQLAlchemy instance
        new_record = ar_taller_servicio_usuario(
            EMPRESA=data["empresa"],
            CODIGO_TALLER=data["codigo_taller"],
            COD_ROL=data["cod_rol"],
            USUARIO=data["usuario"],
            ACTIVO=data.get("activo", 1),  # default to 1 if not provided
            ADICIONADO_POR=data.get("adicionado_por"),
            # fecha_adicion is automatically handled by the DB (SYSDATE)
            MODIFICADO_POR=data.get("modificado_por"),
            # fecha_modificacion can be manually updated here or via a trigger
        )

        # 4) Insert into the database
        db.session.add(new_record)
        db.session.commit()

        return jsonify({"message": "Record successfully inserted"}), 201

    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@rmwa.route('/update_taller_usuario', methods=['PUT'])
@jwt_required()
def update_taller_usuario():
    """
    Endpoint to update an existing record in the AR_TALLER_SERVICIO_USUARIO table.

    The record is identified via its primary key:
      - empresa, codigo_taller, cod_rol, usuario

    Optional fields to update: activo, modificado_por, etc.

    Example JSON body:
    {
      "empresa": 20,
      "codigo_taller": "T123",
      "cod_rol": "ASTGAR",
      "usuario": "AMENDOZA",
      "activo": 0,
      "modificado_por": "ASANCHEZ"
    }
    """
    try:
        data = request.get_json()

        # Validate PK
        required_fields = ["empresa", "codigo_taller", "cod_rol", "usuario"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: '{field}'"}), 400

        # Convert to int if necessary
        empresa_pk = int(data["empresa"])

        # Find the existing record
        record = (
            ar_taller_servicio_usuario.query()
            .filter(
                ar_taller_servicio_usuario.EMPRESA == empresa_pk,
                ar_taller_servicio_usuario.CODIGO_TALLER == data["codigo_taller"],
                ar_taller_servicio_usuario.COD_ROL == data["cod_rol"],
                ar_taller_servicio_usuario.USUARIO == data["usuario"]
            )
            .first()
        )

        if not record:
            return jsonify({"error": "Record not found"}), 404

        # Update optional fields
        if "activo" in data:
            record.ACTIVO = data["activo"]
        if "modificado_por" in data:
            record.MODIFICADO_POR = data["modificado_por"]
        if "fecha_modificacion" in data:
            record.FECHA_MODIFICACION = data["fecha_modificacion"]

        db.session.commit()

        return jsonify({"message": "Record successfully updated"}), 200

    except ValueError:
        return jsonify({"error": "The 'empresa' field must be a valid number"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@rmwa.route('/delete_taller_usuario', methods=['DELETE'])
@jwt_required()
def delete_taller_usuario():
    """
    Endpoint to delete a record from the AR_TALLER_SERVICIO_USUARIO table
    based on its primary key.

    Receives (via JSON body) the fields:
      - empresa (int)
      - codigo_taller (str)
      - cod_rol (str)
      - usuario (str)

    Example JSON:
    {
      "empresa": 20,
      "codigo_taller": "T123",
      "cod_rol": "ASTGAR",
      "usuario": "AMENDOZA"
    }
    """
    try:
        data = request.get_json()

        # Validate PK
        required_fields = ["empresa", "codigo_taller", "cod_rol", "usuario"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: '{field}'"}), 400

        empresa_pk = int(data["empresa"])

        # Find the record
        record = (
            ar_taller_servicio_usuario.query()
            .filter(
                ar_taller_servicio_usuario.EMPRESA == empresa_pk,
                ar_taller_servicio_usuario.CODIGO_TALLER == data["codigo_taller"],
                ar_taller_servicio_usuario.COD_ROL == data["cod_rol"],
                ar_taller_servicio_usuario.USUARIO == data["usuario"]
            )
            .first()
        )

        if not record:
            return jsonify({"error": "Record not found"}), 404

        db.session.delete(record)
        db.session.commit()

        return jsonify({"message": "Record successfully deleted"}), 200

    except ValueError:
        return jsonify({"error": "The 'empresa' field must be a valid number"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@rmwa.route('/get_taller_usuario_relations', methods=['GET'])
@jwt_required()
def get_taller_usuario_relations():
    """
    Endpoint to retrieve the relationships in AR_TALLER_SERVICIO_USUARIO.

    Optional query param:
      - empresa (int): If provided, filters by that empresa code.

    Returns a list of objects, e.g.:
    [
      {
        "empresa": 20,
        "codigo_taller": "T123",
        "cod_rol": "ASTGAR",
        "usuario": "AMENDOZA",
        "activo": 1,
        ...
      },
      ...
    ]
    """
    try:
        # Optional query param: 'empresa'
        empresa_str = request.args.get('empresa', None)

        query = ar_taller_servicio_usuario.query()

        if empresa_str is not None:
            # Convert to int and filter by empresa
            empresa_int = int(empresa_str)
            query = query.filter(ar_taller_servicio_usuario.EMPRESA == empresa_int)

        # Execute query
        results = query.all()

        # If no results, we can return an empty list
        if not results:
            return jsonify([]), 200

        # Build JSON response
        data = []
        for r in results:
            data.append({
                "empresa": r.EMPRESA,
                "codigo_taller": r.CODIGO_TALLER,
                "cod_rol": r.COD_ROL,
                "usuario": r.USUARIO,
                "activo": r.ACTIVO,
                "adicionado_por": r.ADICIONADO_POR,
                "fecha_adicion": r.FECHA_ADICION.isoformat() if r.FECHA_ADICION else None,
                "modificado_por": r.MODIFICADO_POR,
                "fecha_modificacion": r.FECHA_MODIFICACION.isoformat() if r.FECHA_MODIFICACION else None
            })

        return jsonify(data), 200

    except ValueError:
        # If 'empresa' is invalid
        return jsonify({"error": "The 'empresa' query param must be a valid integer"}), 400
    except Exception as e:
        # Catch any other errors
        return jsonify({"error": str(e)}), 500
