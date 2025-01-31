from flask_jwt_extended import jwt_required
from flask import Blueprint, jsonify, request
from src import oracle
from src.models.postVenta import ar_taller_servicio_tecnico, ADprovincias, ADcantones, ar_duracion_reparacion
from src.models.clientes import Cliente
from sqlalchemy import (and_)
import cx_Oracle
from os import getenv
import json
from datetime import datetime, date
#here modules

import logging

rmwa = Blueprint('routes_module_warranty', __name__)

@rmwa.route('/manual_entry_of_warranty_cases', methods=['POST'])
@jwt_required()
def manual_entry_of_warranty_cases():
    return jsonify("test" , "test")

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
    # Retrieve parameters from the query string
    cod_cliente = request.args.get('cod_cliente', None)
    enterprise = request.args.get('enterprise', None)

    # Validate if both parameters were provided
    if not cod_cliente or not enterprise:
        return jsonify({"error": "Missing parameters: 'cod_cliente' and/or 'enterprise'"}), 400

    try:
        # Insert a dash before the last digit of 'cod_cliente'
        cod_cliente_with_dash = add_dash_before_last_digit(cod_cliente)

        # Query the model using the class method 'query'
        cliente = (
            Cliente.query()
            .filter(
                Cliente.cod_cliente == cod_cliente_with_dash,
                Cliente.empresa == enterprise
            )
            .first()
        )

        # Check if a record was found
        if not cliente:
            return jsonify({"error": "Client not found"}), 404

        # Prepare the response as a dictionary
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
        # Handle any unexpected error
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
    """
    Main endpoint to handle warranty case creation, using a single DB connection/transaction.
    1. Validates incoming data.
    2. Upper-cases string values.
    3. Sets non-variable data.
    4. Gets 'taller' info.
    5. Gets motor info.
    6. Generates 'cod_comprobante' and inserts into ST_CASOS_POSTVENTA.
    7. Saves problem types in ST_CASOS_TIPO_PROBLEMA.
    If any step fails, the transaction is rolled back, and the connection is closed.
    """
    c = None
    try:
        # 1. Parse request body
        dataCaso = json.loads(request.data)

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
        set_non_variable_data(dataCaso)

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
def set_non_variable_data(data):
    """
    Sets additional fields that are constant or derived.
    """
    data['EMPRESA'] = 20
    data['TIPO_COMPROBANTE'] = 'CP'

    # Convert 'FECHA' to datetime
    fecha_formateada = datetime.strptime(data['FECHA'], '%Y/%m/%d %H:%M:%S')
    data['FECHA'] = fecha_formateada

    data['CODIGO_NACION'] = 1
    data['CODIGO_RESPONSABLE'] = 'WSSHIBOT'
    data['COD_CANAL'] = 5
    data['ADICIONADO_POR'] = 'WSSHIBOT'

    # Convert 'FECHA_VENTA' to datetime
    fecha_venta = datetime.strptime(data['FECHA_VENTA'], '%Y/%m')
    data['FECHA_VENTA'] = fecha_venta

    data['APLICA_GARANTIA'] = 2

# ------------------------ DB OPERATIONS ------------------------
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
    """
    Retrieves the product code and distributor from 'oracle.infoMotor'
    based on 'COD_MOTOR'.
    This function doesn't require the open connection, as 'oracle.infoMotor'
    presumably handles it internally or uses another mechanism.
    """
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
    """
    Inserts multiple rows into ST_CASOS_TIPO_PROBLEMA
    based on the 'PROBLEMAS' field in 'data', using the open connection 'c'.
    """
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