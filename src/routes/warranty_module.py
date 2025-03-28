from flask_jwt_extended import jwt_required
from flask import Blueprint, jsonify, request
from src import oracle
from src.models.postVenta import ar_taller_servicio_tecnico, ADprovincias, ADcantones, ar_duracion_reparacion, st_casos_postventa, ar_taller_servicio_usuario, st_casos_postventas_obs,st_casos_productos
from src.models.clientes import Cliente, st_politica_credito, persona, st_vendedor
from src.models.users import Usuario, tg_rol_usuario, tg_agencia, Orden
from src.models.productos import Producto
from src.models.despiece_repuestos import st_producto_despiece
from src.models.lote import StLote, st_inventario_lote
from sqlalchemy import and_, extract, func
from sqlalchemy.exc import SQLAlchemyError
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

        # If everything worked, commit the transactio
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
    Establece campos adicionales que son constantes o derivados,
    aplicando conversiones seguras de string a entero cuando corresponda.
    """
    data['EMPRESA'] = enterpriseShineray
    data['TIPO_COMPROBANTE'] = 'CP'

    # Convertir 'FECHA' a datetime
    data['FECHA'] = datetime.strptime(data['FECHA'], '%Y/%m/%d %H:%M:%S')

    # Establecer campos numéricos usando safe_int.
    # Se usa un valor por defecto en caso de que el dato no se encuentre o no pueda convertirse.
    data['CODIGO_NACION'] = safe_int(data.get('CODIGO_NACION', 1), 1)
    # Si userShineray representa un ID numérico, se convierte; de lo contrario se deja como está.
    data['CODIGO_RESPONSABLE'] = safe_int(userShineray, userShineray)
    data['COD_CANAL'] = safe_int(data.get('COD_CANAL', 5), 5)
    data['ADICIONADO_POR'] = safe_int(userShineray, userShineray)

    # Convertir 'FECHA_VENTA' a datetime
    data['FECHA_VENTA'] = datetime.strptime(data['FECHA_VENTA'], '%Y/%m')

    data['APLICA_GARANTIA'] = safe_int(data.get('APLICA_GARANTIA', 2), 2)
    data['KILOMETRAJE'] = safe_int(data.get('KILOMETRAJE', 0))
    data['COD_TIPO_PROBLEMA'] = safe_int(data.get('COD_TIPO_PROBLEMA', 0))
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
def safe_int(value, default=0):
    """
    Intenta convertir value a entero. Si falla, retorna el valor por defecto.
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

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
        print(e)
        return jsonify({"error": str(e)}), 500

@rmwa.route('/get_incidences_by_motor_year', methods=['GET'])
@jwt_required()
def get_incidences_by_motor_year():
    """
    Endpoint that groups by year the number of incidences (cases),
    filtering by 'empresa' (company) and 'cod_motor_' (motor code)
    in the ST_CASOS_POSTVENTA table.
    """
    try:
        empresa_str = request.args.get('empresa', None)
        cod_motor_str = request.args.get('cod_motor_', None)

        if not empresa_str or not cod_motor_str:
            return jsonify({"error": "Missing required parameters (empresa, cod_motor_)."}), 400

        try:
            empresa_int = int(empresa_str)
        except ValueError:
            return jsonify({"error": "Parameter 'empresa' must be a valid integer."}), 400

        # Base query construction
        query = st_casos_postventa.query()

        # Filter by 'empresa'
        query = query.filter(st_casos_postventa.empresa == empresa_int)

        # Filter by 'cod_motor'
        query = query.filter(st_casos_postventa.cod_motor == cod_motor_str)

        # Group by year and count the number of cases
        # Using extract('YEAR', st_casos_postventa.fecha)
        # If you are using Oracle without extract('YEAR'), you can do:
        #    func.to_char(st_casos_postventa.fecha, 'YYYY').label("year")
        results = (
            query.with_entities(
                extract('YEAR', st_casos_postventa.fecha).label("year"),
                func.count('*').label("incidences")
            )
            .group_by(extract('YEAR', st_casos_postventa.fecha))
            .order_by(extract('YEAR', st_casos_postventa.fecha))
            .all()
        )

        # Build the response
        data = []
        for row in results:
            # row.year might be a float (e.g., 2022.0) depending on the DB/ORM
            year_value = int(row.year) if row.year is not None else None
            data.append({
                "year": year_value,
                "incidences": row.incidences
            })

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rmwa.route('/postventas_obs', methods=['POST'])
@jwt_required()
def create_postventas_obs():
    try:
        data = request.get_json()
        required_fields = ["empresa", "tipo_comprobante", "cod_comprobante", "usuario", "observacion", "tipo"]

        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: '{field}'"}), 400

        # Busca la secuencia máxima y calcula la siguiente
        last_record = (
            st_casos_postventas_obs.query()
            .filter(
                st_casos_postventas_obs.empresa == data["empresa"],
                st_casos_postventas_obs.tipo_comprobante == data["tipo_comprobante"],
                st_casos_postventas_obs.cod_comprobante == data["cod_comprobante"]
            )
            .order_by(st_casos_postventas_obs.secuencia.desc())
            .first()
        )

        next_secuencia = 1 if last_record is None else last_record.secuencia + 1

        # Ignora la fecha que viene del front y usa la del servidor
        new_record = st_casos_postventas_obs(
            empresa=data["empresa"],
            tipo_comprobante=data["tipo_comprobante"],
            cod_comprobante=data["cod_comprobante"],
            secuencia=next_secuencia,
            fecha=datetime.now(),  # Aquí se fuerza la fecha/hora del backend
            usuario=data["usuario"],
            observacion=data["observacion"],
            tipo=data["tipo"]
        )
        db.session.add(new_record)
        db.session.commit()

        return jsonify({"message": "Record successfully inserted", "secuencia": next_secuencia}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        print(str(e))
        return jsonify({"error": str(e)}), 500

@rmwa.route('/postventas_obs/<string:cod_comprobante>', methods=['GET'])
@jwt_required()
def get_postventas_obs_by_cod(cod_comprobante):
    try:
        records = (
            st_casos_postventas_obs.query()
            .filter(st_casos_postventas_obs.cod_comprobante == cod_comprobante)
            .all()
        )
        data_list = []
        for r in records:
            data_list.append({
                "empresa": r.empresa,
                "tipo_comprobante": r.tipo_comprobante,
                "cod_comprobante": r.cod_comprobante,
                "secuencia": r.secuencia,
                "fecha": r.fecha.isoformat() if r.fecha else None,
                "usuario": r.usuario,
                "observacion": r.observacion,
                "tipo": r.tipo
            })
        return jsonify(data_list), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500


@rmwa.route('/postventas_obs/<string:cod_comprobante>/<int:secuencia>', methods=['PUT'])
@jwt_required()
def update_postventas_obs(cod_comprobante, secuencia):
    try:
        data = request.get_json()

        # Locate record using filters
        record = (
            st_casos_postventas_obs.query()
            .filter(
                st_casos_postventas_obs.cod_comprobante == cod_comprobante,
                st_casos_postventas_obs.secuencia == secuencia
            )
            .first()
        )
        if not record:
            return jsonify({"error": "Record not found"}), 404

        if "fecha" in data:
            record.fecha = data["fecha"]
        if "usuario" in data:
            record.usuario = data["usuario"]
        if "observacion" in data:
            record.observacion = data["observacion"]
        if "tipo" in data:
            record.tipo = data["tipo"]

        db.session.commit()
        return jsonify({"message": "Record successfully updated"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@rmwa.route('/postventas_obs/<string:cod_comprobante>/<int:secuencia>', methods=['DELETE'])
@jwt_required()
def delete_postventas_obs(cod_comprobante, secuencia):
    try:
        record = (
            st_casos_postventas_obs.query()
            .filter(
                st_casos_postventas_obs.cod_comprobante == cod_comprobante,
                st_casos_postventas_obs.secuencia == secuencia
            )
            .first()
        )
        if not record:
            return jsonify({"error": "Record not found"}), 404

        db.session.delete(record)
        db.session.commit()
        return jsonify({"message": "Record successfully deleted"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@rmwa.route('/agencia/active', methods=['GET'])
@jwt_required()
def get_active_agencies():
    try:
        # Parse 'empresa' from query parameters
        empresa_param = request.args.get('empresa', type=int)
        if not empresa_param:
            return jsonify({"error": "Missing or invalid 'empresa' query parameter"}), 400

        # Build the subquery using 'exists'
        subquery = (
            db.session.query(Orden)
            .filter(
                Orden.tipo_comprobante == 'A0',
                Orden.empresa == tg_agencia.empresa,
                Orden.bodega == tg_agencia.cod_agencia
            )
            .exists()
        )

        # Filter 'tg_agencia' by 'empresa', 'activo', and the EXISTS condition
        agencies = (
            tg_agencia.query()
            .filter(
                tg_agencia.empresa == empresa_param,
                tg_agencia.activo == 'S',
                subquery  # EXISTS(...)
            )
            .all()
        )

        # Build the response mimicking "AGENCIA" and "COD_AGENCIA"
        data_list = []
        for agency in agencies:
            data_list.append({
                "AGENCIA": agency.nombre,
                "COD_AGENCIA": str(agency.cod_agencia)  # Emulating TO_CHAR
            })

        return jsonify(data_list), 200

    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500


@rmwa.route('/politica_credito', methods=['GET'])
@jwt_required()
def get_politica_credito():

    try:
        # Extract query parameters
        empresa_param = request.args.get('empresa', type=int)
        cod_politica_param = request.args.get('codPolitica', type=int)

        # Check for missing or invalid parameters
        if not empresa_param or not cod_politica_param:
            return jsonify({"error": "Missing or invalid query parameters (empresa, codPolitica)"}), 400

        # Query the table
        politicas = (
            st_politica_credito.query()
            .filter(
                st_politica_credito.empresa == empresa_param,
                st_politica_credito.cod_politica == cod_politica_param
            )
            .all()
        )

        # Build the response (mimicking NOMBRE and TO_CHAR(COD_POLITICA))
        result = []
        for p in politicas:
            result.append({
                "NOMBRE": p.nombre,
                "COD_POLITICA": str(p.cod_politica)  # Emulating TO_CHAR
            })

        return jsonify(result), 200

    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500


@rmwa.route('/persona/vendors', methods=['GET'])
@jwt_required()
def get_vendors_by_empresa_and_activo():
    """
    Emulates:
    SELECT a.cod_persona, a.nombre, a.cod_tipo_persona
      FROM persona a
           JOIN st_vendedor b
             ON a.empresa = b.empresa
            AND a.cod_tipo_persona = b.cod_tipo_persona
            AND a.cod_persona = b.cod_vendedor
     WHERE a.empresa = :empresa
       AND a.cod_tipo_persona = 'VEN'
       AND b.activo = :activo;

    Takes 'empresa' and 'activo' from query params, e.g.:
        GET /persona/vendors?empresa=20&activo=S
    """
    try:
        empresa_param = request.args.get('empresa', type=int)
        activo_param = request.args.get('activo', type=str)  # 'S' or 'N'

        if not empresa_param or not activo_param:
            return jsonify({"error": "Missing or invalid query parameters: (empresa, activo)"}), 400

        # Perform the join between persona (a) and st_vendedor (b)
        results = (
            db.session.query(
                persona.cod_persona,
                persona.nombre,
                persona.cod_tipo_persona
            )
            .join(
                st_vendedor,
                and_(
                    persona.empresa == st_vendedor.empresa,
                    persona.cod_tipo_persona == st_vendedor.cod_tipo_persona,
                    persona.cod_persona == st_vendedor.cod_vendedor
                )
            )
            .filter(
                persona.empresa == empresa_param,
                persona.cod_tipo_persona == 'VEN',
                st_vendedor.activo == activo_param
            )
            .all()
        )

        # Build response
        data_list = []
        for row in results:
            data_list.append({
                "COD_PERSONA": row[0],
                "NOMBRE": row[1],
                "COD_TIPO_PERSONA": row[2]
            })

        return jsonify(data_list), 200

    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500

@rmwa.route('/producto/despiece', methods=['GET'])
@jwt_required()
def get_productos_with_despiece():
    """
    Emulates:
    SELECT A.COD_PRODUCTO, A.NOMBRE
      FROM producto A
     WHERE A.EMPRESA = :empresa
       AND A.ACTIVO = :activo
       AND EXISTS (
           SELECT 1
             FROM st_producto_despiece X
            WHERE A.EMPRESA = X.EMPRESA
              AND A.COD_PRODUCTO = X.COD_PRODUCTO
       );

    Takes 'empresa' and 'activo' from query params, for example:
        GET /producto/despiece?empresa=20&activo=S
    """
    try:
        # Extract query parameters
        empresa_param = request.args.get('empresa', type=int)
        activo_param = request.args.get('activo', type=str)

        # Basic validation of parameters
        if empresa_param is None or not activo_param:
            return jsonify({"error": "Missing or invalid 'empresa' or 'activo' query parameters"}), 400

        # Build the subquery using exists(...)
        subquery = (
            db.session.query(st_producto_despiece)
            .filter(
                st_producto_despiece.empresa == Producto.empresa,
                st_producto_despiece.cod_producto == Producto.cod_producto
            )
            .exists()
        )

        # Main query
        productos = (
            Producto.query()
            .filter(
                Producto.empresa == empresa_param,
                Producto.activo == activo_param,
                subquery  # This adds the EXISTS condition
            )
            .all()
        )

        # Build the response with COD_PRODUCTO and NOMBRE
        data_list = []
        for prod in productos:
            data_list.append({
                "COD_PRODUCTO": prod.cod_producto,
                "NOMBRE": prod.nombre,
                "modelo": prod.cod_modelo
            })

        return jsonify(data_list), 200

    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500

@rmwa.route('/lotes/inventory', methods=['GET'])
@jwt_required()
def get_lotes_with_inventory():
    """
    Receives query parameters:
      - empresa (int)
      - bodega (int)
      - producto (str)
    Example request:
      GET /lotes/inventory?empresa=20&bodega=6&producto=R150-FR0545
    """
    try:
        # Read query parameters
        empresa_param = request.args.get('empresa', type=int)
        bodega_param = request.args.get('bodega', type=int)
        producto_param = request.args.get('producto', type=str)

        # Basic validation
        if empresa_param is None or bodega_param is None or not producto_param:
            return jsonify({"error": "Missing or invalid query parameters (empresa, bodega, producto)"}), 400

        # Build the subquery using EXISTS
        subquery = (
            db.session.query(st_inventario_lote)
            .filter(
                st_inventario_lote.empresa == empresa_param,
                st_inventario_lote.tipo_comprobante_lote == StLote.tipo_comprobante,
                st_inventario_lote.cod_comprobante_lote == StLote.cod_comprobante,
                st_inventario_lote.cod_bodega == bodega_param,
                st_inventario_lote.cod_producto == producto_param,
                st_inventario_lote.cod_aamm == 0,       # Hardcoded as per your example
                st_inventario_lote.cantidad > 0         # Hardcoded condition
            )
            .exists()
        )

        # Main query on st_lote, filtering by empresa and the EXISTS subquery
        lotes = (
            StLote.query()
            .filter(
                StLote.empresa == empresa_param,
                subquery
            )
            .order_by(StLote.fecha)
            .all()
        )

        # Build the response
        data_list = []
        for lote in lotes:
            data_list.append({
                "cod_comprobante_lote": lote.cod_comprobante,
                "descripcion": lote.descripcion,
                "tipo": lote.tipo_comprobante
            })

        return jsonify(data_list), 200

    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500

@rmwa.route('/existence_by_agency', methods=['GET'])
@jwt_required()
def consulta_existencia():
    """
    Endpoint to query product existence from KS_INVENTARIO.consulta_existencia.
    Example call:
      GET /consulta_existencia?empresa=20&cod_agencia=6&cod_producto=R150-FR0545
    """
    c = None
    try:
        # 1. Retrieve required query parameters
        empresa_str = request.args.get('empresa')
        cod_agencia_str = request.args.get('cod_agencia')
        cod_producto = request.args.get('cod_producto')

        # 2. Validate parameters
        if not empresa_str or not cod_agencia_str or not cod_producto:
            return jsonify({"error": "Parameters 'empresa', 'cod_agencia', and 'cod_producto' are required"}), 400

        # 3. Convert 'empresa' and 'cod_agencia' to numeric types
        try:
            empresa = float(empresa_str)
            cod_agencia = float(cod_agencia_str)
        except ValueError:
            return jsonify({"error": "'empresa' and 'cod_agencia' must be numeric"}), 400

        # 4. Open database connection
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))

        # 5. Prepare the PL/SQL block to call the package
        #    and store the result in an output variable.
        plsql_block = """
        DECLARE
          v_existencia_lote NUMBER(14,2);
        BEGIN
          v_existencia_lote := KS_INVENTARIO.consulta_existencia(
                                  :1,   -- empresa
                                  :2,   -- cod_agencia
                                  :3,   -- cod_producto
                                  'U',  -- fixed
                                  SYSDATE,
                                  1,    -- fixed
                                  'Z',  -- fixed
                                  1     -- fixed
                               );
          :4 := v_existencia_lote;
        END;
        """

        # 6. Execute PL/SQL block with bind variables
        cur = c.cursor()
        out_var = cur.var(cx_Oracle.NUMBER)
        cur.execute(plsql_block, (empresa, cod_agencia, cod_producto, out_var))
        existencia_lote = out_var.getvalue()

        # 7. Close cursor, return JSON response
        cur.close()
        return jsonify({"existencia_lote": float(existencia_lote)}), 200

    except Exception as e:
        # Roll back and return error if something fails
        if c:
            c.rollback()
        print(f"Error calling KS_INVENTARIO.consulta_existencia: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        # Close connection
        if c:
            c.close()

@rmwa.route('/existencia_lote_by_agency_cod_producto', methods=['GET'])
@jwt_required()
def existencia_lote():
    """
    GET /existencia_lote?empresa=20&cod_agencia=6&cod_producto=R150-FR0545&tipo_comprobante_lote=LT&cod_comprobante_lote=F1B241126

    Calls ks_inventario_lote.consulta_existencia with the parameters from the query string.
    """
    c = None
    try:
        # 1. Read required query parameters
        empresa_str = request.args.get('empresa')  # e.g. 20
        cod_agencia_str = request.args.get('cod_agencia')  # e.g. 6
        cod_producto = request.args.get('cod_producto')  # e.g. R150-FR0545
        tipo_comprobante_lote = request.args.get('tipo_comprobante_lote')  # e.g. LT
        cod_comprobante_lote = request.args.get('cod_comprobante_lote')  # e.g. F1B241126


        if not all([empresa_str, cod_agencia_str, cod_producto, tipo_comprobante_lote, cod_comprobante_lote]):
            return jsonify({"error": "Missing one or more required query parameters"}), 400

        # 3. Convert empresa and cod_agencia to numeric (if appropriate)
        try:
            empresa = float(empresa_str)
            cod_agencia = float(cod_agencia_str)
        except ValueError:
            return jsonify({"error": "'empresa' and 'cod_agencia' must be numeric"}), 400

        # 4. Open a database connection
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur = c.cursor()

        # 5. Prepare PL/SQL block
        #    The 3rd and 8th parameters are NULL, and the 7th param is 'U', 9th is 1
        plsql_block = """
        DECLARE
            v_existencia_lote NUMBER(14,2);
        BEGIN
            v_existencia_lote := ks_inventario_lote.consulta_existencia(
                :1,   -- empresa
                :2,   -- cod_agencia
                NULL, -- 3rd parameter, remains NULL
                :3,   -- cod_producto
                :4,   -- tipo_comprobante_lote
                :5,   -- cod_comprobante_lote
                'U',  -- 7th parameter
                NULL, -- 8th parameter
                1     -- 9th parameter
            );
            :6 := v_existencia_lote;
        END;
        """

        # 6. Execute the PL/SQL block with bind variables
        out_var = cur.var(cx_Oracle.NUMBER)  # output variable
        cur.execute(plsql_block, (
            empresa,  # :1
            cod_agencia,  # :2
            cod_producto,  # :3
            tipo_comprobante_lote,  # :4
            cod_comprobante_lote,  # :5
            out_var  # :6 (output)
        ))

        # 7. Retrieve the result and close cursor
        existencia_lote = out_var.getvalue()
        cur.close()

        # 8. Return JSON response
        return jsonify({"existencia_lote": float(existencia_lote)}), 200

    except Exception as e:
        # In case of any error, rollback if the connection is open
        if c:
            c.rollback()
        print(f"Error in existencia_lote endpoint: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        # Always close the connection if it was opened
        if c:
            c.close()


@rmwa.route('/obt_precio_actual', methods=['GET'])
@jwt_required()
def get_costo():
    """
    Minimal endpoint to retrieve cost directly from ks_producto_lote.obt_costo_lote
    without using ROWTYPE objects.
    Example query:
      GET /get_costo?empresa=20&cod_producto=R150-FR0545&cod_comprobante_lote=F1B241126&tipo_comprobante_lote=LT
    """
    c = None
    try:
        # 1) Retrieve query parameters
        empresa_str = request.args.get('empresa')
        cod_producto = request.args.get('cod_producto')
        cod_comprobante_lote = request.args.get('cod_comprobante_lote')
        tipo_comprobante_lote = request.args.get('tipo_comprobante_lote')

        # Validate we have the necessary params
        if not all([empresa_str, cod_producto, cod_comprobante_lote, tipo_comprobante_lote]):
            return jsonify({"error": "Missing one or more required query parameters"}), 400

        # Convert 'empresa' to numeric if applicable
        try:
            empresa = float(empresa_str)
        except ValueError:
            return jsonify({"error": "'empresa' must be numeric"}), 400

        # 2) Open the database connection
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur = c.cursor()

        # 3) Minimal PL/SQL block calling ks_producto_lote.obt_costo_lote
        #    and returning the result in an output variable (out_cost).
        plsql_block = """
        DECLARE
            v_costo NUMBER(14,2);
        BEGIN
            v_costo := ks_producto_lote.obt_costo_lote(
                          :p_empresa,
                          :p_cod_producto,
                          :p_cod_comprobante_lote,
                          :p_tipo_comprobante_lote,
                          SYSDATE
                       );
            :p_out_cost := v_costo;
        END;
        """

        # 4) Bind variable for the output (cost)
        out_cost_var = cur.var(cx_Oracle.NUMBER)

        # 5) Execute the PL/SQL block
        cur.execute(plsql_block, {
            "p_empresa": empresa,
            "p_cod_producto": cod_producto,
            "p_cod_comprobante_lote": cod_comprobante_lote,
            "p_tipo_comprobante_lote": tipo_comprobante_lote,
            "p_out_cost": out_cost_var
        })

        # 6) Retrieve cost from output variable
        cost_value = out_cost_var.getvalue()

        # Close the cursor
        cur.close()

        # 7) Return the cost in JSON
        return jsonify({"costo": float(cost_value)}), 200

    except Exception as e:
        # Roll back if there's any exception
        if c:
            c.rollback()
        print(f"Error in get_costo endpoint: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        # Ensure the connection is closed
        if c:
            c.close()

@rmwa.route('/generate_order_warranty', methods=['GET'])
@jwt_required()
def genera_pedido():
    """
    Invokes ks_casos_postventas.p_genera_pedido, returning p_cod_pedido and p_tipo_pedido in JSON.
    Also updates st_casos_productos and st_casos_postventa with those values for
    (empresa, tipo_comprobante, cod_comprobante).
    """
    c = None
    try:
        # 1. Read query parameters (IN / IN OUT)
        p_empresa_str          = request.args.get('empresa')
        p_tipo_comprobante     = request.args.get('tipo_comprobante')
        p_cod_comprobante      = request.args.get('cod_comprobante')
        p_cod_agencia_str      = request.args.get('cod_agencia')
        p_cod_politica_str     = request.args.get('cod_politica')
        p_todos_str            = request.args.get('todos')  # Optional
        p_cod_pedido_in        = request.args.get('cod_pedido')     # IN OUT
        p_tipo_pedido_in       = request.args.get('tipo_pedido')    # IN OUT

        # 2. Validate mandatory parameters
        if not all([
            p_empresa_str, p_tipo_comprobante, p_cod_comprobante,
            p_cod_agencia_str, p_cod_politica_str
        ]):
            return jsonify({"error": "Missing one or more required query parameters"}), 400

        # 3. Convert numeric params
        try:
            p_empresa = int(p_empresa_str)
            p_cod_agencia = int(p_cod_agencia_str)
            p_cod_politica = int(p_cod_politica_str)
        except ValueError:
            return jsonify({"error": "Some numeric parameters cannot be converted"}), 400

        # 4. p_todos: default to 1 if not provided
        if p_todos_str is None or p_todos_str.strip() == "":
            p_todos = 1
        else:
            try:
                p_todos = int(p_todos_str)
            except ValueError:
                return jsonify({"error": "'p_todos' must be numeric"}), 400

        # 5. Open DB connection (cx_Oracle) to call the stored procedure
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur = c.cursor()

        # 6. Define PL/SQL block
        plsql_block = """
        BEGIN
            ks_casos_postventas.p_genera_pedido(
                p_empresa          => :p_empresa,
                p_tipo_comprobante => :p_tipo_comprobante,
                p_cod_comprobante  => :p_cod_comprobante,
                p_cod_agencia      => :p_cod_agencia,
                p_cod_politica     => :p_cod_politica,
                p_todos            => :p_todos,
                p_cod_pedido       => :p_cod_pedido,
                p_tipo_pedido      => :p_tipo_pedido
            );
        END;
        """

        # 7. Prepare bind variables (IN OUT)
        b_cod_pedido = cur.var(cx_Oracle.STRING)
        b_cod_pedido.setvalue(0, p_cod_pedido_in if p_cod_pedido_in else "")
        b_tipo_pedido = cur.var(cx_Oracle.STRING)
        b_tipo_pedido.setvalue(0, p_tipo_pedido_in if p_tipo_pedido_in else "")

        # 8. Execute PL/SQL block
        cur.execute(plsql_block, {
            "p_empresa": p_empresa,
            "p_tipo_comprobante": p_tipo_comprobante,
            "p_cod_comprobante": p_cod_comprobante,
            "p_cod_agencia": p_cod_agencia,
            "p_cod_politica": p_cod_politica,
            "p_todos": p_todos,
            "p_cod_pedido": b_cod_pedido,
            "p_tipo_pedido": b_tipo_pedido
        })

        # Commit changes made by the procedure (if any)
        c.commit()

        # 9. Retrieve OUT parameters
        out_cod_pedido = b_cod_pedido.getvalue()
        out_tipo_pedido = b_tipo_pedido.getvalue()

        # 10. Update st_casos_productos
        #     matching the same (empresa, tipo_comprobante, cod_comprobante).
        matching_products = (
            st_casos_productos.query()
            .filter(
                st_casos_productos.empresa == p_empresa,
                st_casos_productos.tipo_comprobante == p_tipo_comprobante,
                st_casos_productos.cod_comprobante == p_cod_comprobante
            )
            .all()
        )

        for rec in matching_products:
            rec.cod_pedido = out_cod_pedido
            rec.cod_tipo_pedido = out_tipo_pedido

        # 11. Update st_casos_postventa (a single record)
        matching_postventa = (
            st_casos_postventa.query()
            .filter(
                st_casos_postventa.empresa == p_empresa,
                st_casos_postventa.cod_comprobante == p_cod_comprobante
            )
            .first()
        )

        if matching_postventa:
            matching_postventa.cod_pedido = out_cod_pedido
            matching_postventa.cod_tipo_pedido = out_tipo_pedido

        # Commit all changes in SQLAlchemy
        db.session.commit()

        # 12. Return the final values
        return jsonify({
            "p_cod_pedido": out_cod_pedido,
            "p_tipo_pedido": out_tipo_pedido,
            "updated_products": len(matching_products),
            "updated_postventa": 1 if matching_postventa else 0
        }), 200

    except Exception as e:
        # Rollback both cx_Oracle and SQLAlchemy sessions if any error
        if c:
            c.rollback()
        db.session.rollback()
        print(f"Error in genera_pedido: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if c:
            c.close()


#REST API ST_CASOS_PRODUCTOS
@rmwa.route('/casos_productos', methods=['POST'])
@jwt_required()
def create_casos_productos():
    """
    Creates a new record in ST_CASOS_PRODUCTOS.
    - Data comes from JSON body.
    - Automatically determines the next 'secuencia' if none exists
      for (empresa, tipo_comprobante, cod_comprobante).
    """
    try:
        data = request.get_json()
        required_fields = [
            "empresa",
            "tipo_comprobante",
            "cod_comprobante",
            "cod_producto",
            "cantidad",
            "precio",
            "adicionado_por",
            "tipo_comprobante_lote",
            "cod_comprobante_lote"

        ]

        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: '{field}'"}), 400

        # Get the last record for this (empresa, tipo_comprobante, cod_comprobante)
        last_record = (
            st_casos_productos.query()
            .filter(
                st_casos_productos.empresa == data["empresa"],
                st_casos_productos.tipo_comprobante == data["tipo_comprobante"],
                st_casos_productos.cod_comprobante == data["cod_comprobante"]
            )
            .order_by(st_casos_productos.secuencia.desc())
            .first()
        )
        next_secuencia = 1 if last_record is None else last_record.secuencia + 1

        new_record = st_casos_productos(
            empresa=data["empresa"],
            tipo_comprobante=data["tipo_comprobante"],
            cod_comprobante=data["cod_comprobante"],
            secuencia=next_secuencia,
            cod_producto=data["cod_producto"],
            cantidad=data["cantidad"],
            precio=data["precio"],
            # Set default or from JSON
            adicionado_por=data.get("adicionado_por"),
            fecha_adicion=datetime.now(),  # Force server-side timestamp
            cod_pedido=data.get("cod_pedido",""),
            cod_tipo_pedido=data.get("cod_tipo_pedido",""),
            tipo_comprobante_lote=data.get("tipo_comprobante_lote"),
            cod_comprobante_lote=data.get("cod_comprobante_lote")
        )

        db.session.add(new_record)
        db.session.commit()

        return jsonify({
            "message": "Record successfully inserted",
            "secuencia": next_secuencia
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@rmwa.route('/casos_productos', methods=['GET'])
@jwt_required()
def get_casos_productos_by_args():
    """
    Retrieves records from ST_CASOS_PRODUCTOS based on query parameters.
    Example:
      GET /casos_productos?cod_comprobante=ABC123
    Optionally, accept args for empresa, tipo_comprobante, etc.
    """
    try:
        cod_comprobante = request.args.get('cod_comprobante', type=str)
        if not cod_comprobante:
            return jsonify({"error": "Missing or invalid 'cod_comprobante' query parameter"}), 400

        records = (
            st_casos_productos.query()
            .filter(st_casos_productos.cod_comprobante == cod_comprobante)
            .all()
        )

        data_list = []
        for r in records:
            data_list.append({
                "empresa": r.empresa,
                "tipo_comprobante": r.tipo_comprobante,
                "cod_comprobante": r.cod_comprobante,
                "secuencia": r.secuencia,
                "cod_producto": r.cod_producto,
                "cantidad": float(r.cantidad),
                "precio": float(r.precio),
                "adicionado_por": r.adicionado_por,
                "fecha_adicion": (r.fecha_adicion.isoformat() if r.fecha_adicion else None),
                "cod_pedido": r.cod_pedido,
                "cod_tipo_pedido": r.cod_tipo_pedido,
                "tipo_comprobante_lote": r.tipo_comprobante_lote,
                "cod_comprobante_lote": r.cod_comprobante_lote
            })

        return jsonify(data_list), 200

    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500

@rmwa.route('/casos_productos', methods=['DELETE'])
@jwt_required()
def delete_casos_productos():
    """
    Deletes a record from ST_CASOS_PRODUCTOS by
    cod_comprobante (from args) + secuencia (from route).
    Example:
      DELETE /casos_productos/1?cod_comprobante=ABC123
    """
    try:
        secuencia = request.args.get('secuencia')
        cod_comprobante = request.args.get('cod_comprobante', type=str)
        if not cod_comprobante:
            return jsonify({"error": "Missing or invalid 'cod_comprobante' query parameter"}), 400

        record = (
            st_casos_productos.query()
            .filter(
                st_casos_productos.cod_comprobante == cod_comprobante,
                st_casos_productos.secuencia == secuencia
            )
            .first()
        )
        if not record:
            return jsonify({"error": "Record not found"}), 404

        db.session.delete(record)
        db.session.commit()
        return jsonify({"message": "Record successfully deleted"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@rmwa.route('/casos_postventa/cerrar', methods=['POST'])
@jwt_required()
def cerrar_caso():

    try:
        data = request.get_json()
        required_fields = ["empresa", "cod_comprobante", "aplica_garantia", "observacion_final", "usuario_cierra"]

        # Validar campos obligatorios
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Falta el campo obligatorio '{field}'"}), 400

        # Asegurar que aplica_garantia sea 0 o 1
        aplica_garantia_val = int(data["aplica_garantia"])
        if aplica_garantia_val not in (0, 1):
            return jsonify({"error": "aplica_garantia debe ser 0 o 1"}), 400

        # Buscar el caso
        caso = (
            st_casos_postventa.query()
            .filter(
                st_casos_postventa.empresa == data["empresa"],
                st_casos_postventa.cod_comprobante == data["cod_comprobante"]
            )
            .first()
        )

        if not caso:
            return jsonify({"error": "No se encontró el caso"}), 404

        # Actualizar la información
        caso.aplica_garantia = aplica_garantia_val
        caso.estado = 'C'
        caso.fecha_cierre = datetime.now()  # Se registra la fecha de cierre en el servidor

        # Si se incluye una observación final u otros campos
        if "observacion_final" in data:
            caso.observacion_final = data["observacion_final"]

        if "usuario_cierra" in data:
            caso.usuario_cierra = data["usuario_cierra"]

        # Si hay más campos que quieras actualizar, agrégalos aquí según sea necesario

        # Guardar los cambios en la base de datos
        db.session.commit()

        # Respuesta con datos básicos
        return jsonify({
            "message": (
                "Caso cerrado con garantía" if aplica_garantia_val == 1
                else "Caso cerrado sin garantía"
            ),
            "empresa": caso.empresa,
            "cod_comprobante": caso.cod_comprobante,
            "estado": caso.estado,
            "aplica_garantia": caso.aplica_garantia,
            "fecha_cierre": caso.fecha_cierre.isoformat() if caso.fecha_cierre else None
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@rmwa.route('/close_preliminary', methods=['POST'])
@jwt_required()
def cierre_previo():
    c = None
    try:
        # 1. Leer parámetros
        p_empresa_str      = request.args.get('empresa', type=int)
        p_tipo_comprobante = request.args.get('tipo_comprobante')
        p_cod_comprobante  = request.args.get('cod_comprobante')
        p_observacion      = request.args.get('observacion', default="", type=str)
        p_usuario_cierra   = request.args.get('usuario_cierra', default="", type=str)

        # Validar que no falte alguno de los parámetros obligatorios
        if not all([p_empresa_str, p_tipo_comprobante, p_cod_comprobante, p_usuario_cierra]):
            return jsonify({"error": "Falta uno o más parámetros requeridos (empresa, tipo_comprobante, cod_comprobante, usuario_cierra, observacion)"}), 400

        # Validar longitud de la observación
        if len(p_observacion.strip()) < 1:
            return jsonify({"error": "La observación debe tener al menos 10 caracteres"}), 400

        # 2. Convertir empresa a entero
        try:
            p_empresa = int(p_empresa_str)
        except ValueError:
            return jsonify({"error": "'empresa' debe ser un número entero"}), 400

        # 3. Conexión con cx_Oracle para invocar ps_verifica_cierre
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur = c.cursor()

        # 4. Actualizar st_casos_postventa.estado = 'R' y usuario_cierra
        caso = (
            st_casos_postventa.query()
            .filter(
                st_casos_postventa.empresa == p_empresa,
                st_casos_postventa.tipo_comprobante == p_tipo_comprobante,
                st_casos_postventa.cod_comprobante == p_cod_comprobante
            )
            .first()
        )

        if not caso:
            return jsonify({"error": "No se encontró el caso indicado"}), 404

        # Cambiar estado a 'R' (cierre previo) y registrar quién lo cierra
        caso.estado = 'R'
        caso.usuario_cierra = p_usuario_cierra

        # 5. Insertar la observación en st_casos_postventas_obs (similar a 'INGRESAR_OBSERVACION')
        last_record = (
            st_casos_postventas_obs.query()
            .filter(
                st_casos_postventas_obs.empresa == p_empresa,
                st_casos_postventas_obs.tipo_comprobante == p_tipo_comprobante,
                st_casos_postventas_obs.cod_comprobante == p_cod_comprobante
            )
            .order_by(st_casos_postventas_obs.secuencia.desc())
            .first()
        )
        next_seq = 1 if last_record is None else last_record.secuencia + 1

        new_obs = st_casos_postventas_obs(
            empresa=p_empresa,
            tipo_comprobante=p_tipo_comprobante,
            cod_comprobante=p_cod_comprobante,
            secuencia=next_seq,
            fecha=datetime.now(),
            usuario=p_usuario_cierra,      # se registra quién está cerrando
            observacion=p_observacion,
            tipo="PRE"                   # para distinguir que es cierre previo
        )
        db.session.add(new_obs)

        # Guardar cambios en SQLAlchemy
        db.session.commit()

        # 6. Retornar JSON
        return jsonify({
            "message": "Cierre previo realizado con éxito",
            "empresa": p_empresa,
            "tipo_comprobante": p_tipo_comprobante,
            "cod_comprobante": p_cod_comprobante,
            "estado": caso.estado,
            "usuario_cierra": caso.usuario_cierra
        }), 200

    except Exception as e:
        # Rollback en cx_Oracle y SQLAlchemy si ocurre un error
        if c:
            c.rollback()
        db.session.rollback()
        print(f"Error in cierre_previo: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if c:
            c.close()
