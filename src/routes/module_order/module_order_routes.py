from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.routes.module_order.db_connection import get_oracle_connection
from datetime import datetime
import uuid
rmor = Blueprint('routes_module_order', __name__)

@rmor.route('/credit_policies', methods=['GET'])
@jwt_required()
def get_credit_policies():
    """
    GET /credit_policies

    Returns a list of active credit policies for a given company and agency.
    """
    c = None
    try:
        enterprise = request.args.get('empresa')
        cod_agencia = request.args.get('cod_agencia')

        if not all([enterprise, cod_agencia]):
            return jsonify({"error": "Missing required parameters (empresa, cod_agencia)"}), 400

        try:
            empresa = int(enterprise)
        except ValueError:
            return jsonify({"error": "'empresa' must be integer"}), 400

        c = get_oracle_connection()
        cur = c.cursor()

        sql = """
        SELECT a.nombre,
               TO_CHAR(a.cod_politica) AS cod_politica
        FROM st_politica_credito a,
             st_politica_credito_d b
        WHERE b.empresa = a.empresa
          AND b.cod_politica = a.cod_politica
          AND a.empresa = :empresa
          AND b.es_activo = 1
          AND EXISTS (
                SELECT 'x'
                  FROM stock.tg_agencia age
                 WHERE age.empresa = a.empresa
                   AND age.cod_agencia = :cod_agencia
                   AND (
                        (age.tipo_relacion_polcre = 'I'
                         AND EXISTS (
                            SELECT 'x'
                              FROM stock.st_agencia_polcre c
                             WHERE c.empresa = age.empresa
                               AND c.cod_agencia = age.cod_agencia
                               AND c.cod_politica = a.cod_politica
                         ))
                        OR
                        (age.tipo_relacion_polcre = 'E'
                         AND NOT EXISTS (
                            SELECT 'x'
                              FROM stock.st_agencia_polcre c
                             WHERE c.empresa = age.empresa
                               AND c.cod_agencia = age.cod_agencia
                               AND c.cod_politica = a.cod_politica
                         ))
                        OR
                        (age.tipo_relacion_polcre = 'T')
                    )
             )
        GROUP BY a.cod_politica, a.nombre
        ORDER BY a.cod_politica
        """

        cur.execute(sql, empresa=empresa, cod_agencia=cod_agencia)
        rows = cur.fetchall()

        # The columns are: nombre, cod_politica
        result = [{"cod_politica": row[1], "nombre": row[0]} for row in rows]
        cur.close()
        return jsonify(result), 200

    except Exception as ex:
        if c:
            c.rollback()
        return jsonify({"error": str(ex)}), 500
    finally:
        if c:
            c.close()
    """
    GET /get_credit_policy_description

    Retrieves the description of a credit policy based on company, agency, and policy code.
    """
    c = None
    try:
        enterprise = request.args.get('empresa')
        cod_agencia = request.args.get('cod_agencia')
        cod_politica = request.args.get('cod_politica')

        if not all([enterprise, cod_agencia, cod_politica]):
            return jsonify({"error": "Missing one or more required query parameters (empresa, cod_agencia, cod_politica)"}), 400

        try:
            empresa = int(enterprise)
        except (ValueError, TypeError):
            return jsonify({"error": "'empresa' must be a valid integer"}), 400

        # Usa el helper para obtener la conexión
        c = get_oracle_connection()
        cur = c.cursor()

        plsql = """
        DECLARE
            v_desc VARCHAR2(255);
            v_err  VARCHAR2(255);
        BEGIN
            PK_V6_OBTENER_ST_POL_CRE.P_SACA_DESCRIPCION_ST_POL_CRE(
                :empresa,
                :cod_agencia,
                :cod_politica,
                :desc,
                :err
            );
        END;
        """

        desc_var = cur.var(str)
        err_var  = cur.var(str)

        cur.execute(plsql, {
            "empresa": empresa,
            "cod_agencia": cod_agencia,
            "cod_politica": cod_politica,
            "desc": desc_var,
            "err": err_var
        })

        error_msg = err_var.getvalue()
        policy_desc = desc_var.getvalue()

        if error_msg:
            return jsonify({"error": error_msg}), 400

        if not policy_desc:
            return jsonify({"error": "Policy description not found"}), 404

        return jsonify({"description": policy_desc}), 200

    except Exception as ex:
        if c:
            c.rollback()
        return jsonify({"error": f"Internal server error: {str(ex)}"}), 500

    finally:
        if c:
            c.close()


@rmor.route('/clientes_mayoreo', methods=['GET'])
@jwt_required()
def get_clientes_politica():
    """
    GET /clientes_politica

    Retrieves a list of clients filtered by credit policy, company, agency, order type, and optionally client code.

    Query Parameters:
        empresa (int): Company code (required)
        cod_agencia (str): Agency code (required)
        cod_politica (str): Policy code (required)
        pl_lv_cod_tipo_pedido (str): Order type code (required) IN this case "PE"
        cod_persona_cli (str): Client/person code (optional)

    """
    c = None
    try:
        # --- Get and validate parameters ---
        empresa_str = request.args.get('empresa')
        cod_agencia = request.args.get('cod_agencia')
        cod_politica = request.args.get('cod_politica')
        pl_lv_cod_tipo_pedido = request.args.get('pl_lv_cod_tipo_pedido')
        cod_persona_cli = request.args.get('cod_persona_cli', None)

        if not all([empresa_str, cod_agencia, cod_politica, pl_lv_cod_tipo_pedido]):
            return jsonify({"error": "Missing one or more required query parameters (empresa, cod_agencia, cod_politica, pl_lv_cod_tipo_pedido)"}), 400
        try:
            empresa = int(empresa_str)
        except ValueError:
            return jsonify({"error": "'empresa' must be integer"}), 400

        c = get_oracle_connection()
        cur = c.cursor()

        # --- Main SQL (unions) ---
        sql = """
        SELECT b.cod_persona cod_persona,
               (A.apellido1||' '||RTRIM(A.nombre)) nombre,
               b.cod_tipo_persona cod_tipo_persona,
               b.empresa empresa
        FROM   cliente A, PERSONA B, cliente_hor C, ST_POL_CRE_TIPO_CLIENTE D
        WHERE  A.cod_cliente      = NVL(:cod_persona_cli, COD_PERSONA)
        AND    A.COD_CLIENTE      = B.COD_PERSONA
        AND    A.COD_CLIENTE      = C.COD_CLIENTEH
        AND    A.empresa          = :empresa
        AND    A.EMPRESA          = B.EMPRESA
        AND    A.EMPRESA          = C.empresah
        AND    B.COD_TIPO_PERSONA = 'CLI'
        AND    D.COD_POLITICA     = :cod_politica
        AND    D.EMPRESA          = A.EMPRESA
        AND    D.COD_TIPO_CLIENTEH = C.COD_TIPO_CLIENTEH
        AND    :pl_lv_cod_tipo_pedido != 'PC'
        AND EXISTS
          (SELECT 1
             FROM TG_AGENCIA AA,
                  EMPRESA BB
            WHERE AA.EMPRESA = BB.EMPRESA
              AND AA.RUC = BB.RUC
              AND AA.EMPRESA = :empresa
              AND AA.COD_AGENCIA = :cod_agencia
          )
        UNION
        SELECT b.cod_persona cod_persona,
               (A.apellido1||' '||RTRIM(A.nombre)) nombre,
               b.cod_tipo_persona cod_tipo_persona,
               b.empresa empresa
        FROM   cliente A, PERSONA B, cliente_hor C, ST_POL_CRE_TIPO_CLIENTE D, ST_CLIENTE_CONSIGNACION E
        WHERE  A.cod_cliente      = NVL(:cod_persona_cli, COD_PERSONA)
        AND    A.COD_CLIENTE      = B.COD_PERSONA
        AND    A.COD_CLIENTE      = C.COD_CLIENTEH
        AND    A.empresa          = :empresa
        AND    A.EMPRESA          = B.EMPRESA
        AND    A.EMPRESA          = C.empresah
        AND    B.COD_TIPO_PERSONA = 'CLI'
        AND    D.COD_POLITICA     = :cod_politica
        AND    D.EMPRESA          = A.EMPRESA
        AND    D.COD_TIPO_CLIENTEH = C.COD_TIPO_CLIENTEH
        AND    C.EMPRESAH          = E.EMPRESA
        AND    C.COD_CLIENTEH      = E.COD_CLIENTE
        AND    E.ES_ACTIVO=1
        AND    :pl_lv_cod_tipo_pedido='PC'
        AND EXISTS
          (SELECT 1
             FROM TG_AGENCIA AA,
                  EMPRESA BB
            WHERE AA.EMPRESA = BB.EMPRESA
              AND AA.RUC = BB.RUC
              AND AA.EMPRESA = :empresa
              AND AA.COD_AGENCIA = :cod_agencia
          )
        UNION
        SELECT b.cod_persona cod_persona,
               (A.apellido1||' '||RTRIM(A.nombre)) nombre,
               b.cod_tipo_persona cod_tipo_persona,
               b.empresa empresa
        FROM   cliente A, PERSONA B, cliente_hor C, ST_POL_CRE_TIPO_CLIENTE D, ST_CLIENTE_CONSIGNACION E,
               TG_AGENCIA G
        WHERE  A.cod_cliente      = NVL(:cod_persona_cli, COD_PERSONA)
        AND    A.COD_CLIENTE      = B.COD_PERSONA
        AND    A.COD_CLIENTE      = C.COD_CLIENTEH
        AND    A.empresa          = :empresa
        AND    A.EMPRESA          = B.EMPRESA
        AND    A.EMPRESA          = C.empresah
        AND    B.COD_TIPO_PERSONA = 'CLI'
        AND    D.COD_POLITICA     = :cod_politica
        AND    D.EMPRESA          = A.EMPRESA
        AND    D.COD_TIPO_CLIENTEH = C.COD_TIPO_CLIENTEH
        AND    C.EMPRESAH          = E.EMPRESA
        AND    C.COD_CLIENTEH      = E.COD_CLIENTE
        AND    E.ES_ACTIVO=1
        AND    :pl_lv_cod_tipo_pedido='PC'
        AND    G.COD_AGENCIA = :cod_agencia
        AND    G.EMPRESA = A.EMPRESA
        AND    G.RUC = A.COD_CLIENTE
        AND NOT EXISTS
          (SELECT 1
             FROM TG_AGENCIA AA,
                  EMPRESA BB
            WHERE AA.EMPRESA = BB.EMPRESA
              AND AA.RUC = BB.RUC
              AND AA.EMPRESA = :empresa
              AND AA.COD_AGENCIA = :cod_agencia
          )
        """

        cur.execute(sql, {
            "empresa": empresa,
            "cod_agencia": cod_agencia,
            "cod_politica": cod_politica,
            "pl_lv_cod_tipo_pedido": pl_lv_cod_tipo_pedido,
            "cod_persona_cli": cod_persona_cli
        })

        rows = cur.fetchall()
        columns = [col[0].lower() for col in cur.description]
        result = [dict(zip(columns, row)) for row in rows]

        cur.close()
        return jsonify(result), 200

    except Exception as ex:
        if c:
            c.rollback()
        return jsonify({"error": str(ex)}), 500

    finally:
        if c:
            c.close()


@rmor.route('/cliente_info', methods=['GET'])
@jwt_required()
def get_cliente_info():
    """
    GET /cliente_info

    Loads ALL client info for order header (names, credit, consignation, category, address, phone, city, cups, balances, etc.)

    Query Parameters:
        empresa (int): Company code (required)
        cod_persona_cli (str): Client/person code (required)
        cod_politica (str): Credit policy code (required)
        cod_tipo_pedido (str): Order type code (required, e.g. 'PC')
        cod_pedido (str): Order code (optional, for consignation)
        cod_agencia (str): Agency code (optional, for category)
        cod_tipo_persona_cli (str): Client type code (optional, for cartera vencida)

    Returns:
        200: JSON with all client/policy/order info (flat dictionary)
        400: If parameters are missing or invalid
        404: If client not found or not valid for policy
        500: Internal or database error
    """
    c = None
    try:
        # --- 1. Obtener y validar parámetros ---
        empresa_str = request.args.get('empresa')
        cod_persona_cli = request.args.get('cod_persona_cli')
        cod_politica = request.args.get('cod_politica')
        cod_tipo_pedido = request.args.get('cod_tipo_pedido')
        cod_pedido = request.args.get('cod_pedido', None)
        cod_agencia = request.args.get('cod_agencia', None)
        cod_tipo_persona_cli = request.args.get('cod_tipo_persona_cli', None)

        if not all([empresa_str, cod_persona_cli, cod_politica, cod_tipo_pedido]):
            return jsonify({"error": "Missing required parameters (empresa, cod_persona_cli, cod_politica, cod_tipo_pedido)"}), 400

        try:
            empresa = int(empresa_str)
        except ValueError:
            return jsonify({"error": "'empresa' must be integer"}), 400

        c = get_oracle_connection()
        cur = c.cursor()
        result = {}

        # --- 2. Datos básicos de cliente ---
        sql_basic = """
            SELECT
                cli.cod_cliente,
                cli.apellido1 || ' ' || rtrim(cli.nombre) AS nombre,
                cli.direccion AS direccion_envio,
                cli.telefono
            FROM cliente cli
            WHERE cli.cod_cliente = :cod_persona_cli
              AND cli.empresa = :empresa
        """
        cur.execute(sql_basic, cod_persona_cli=cod_persona_cli, empresa=empresa)
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Client not found."}), 404
        result.update({
            "cod_persona_cli": row[0],
            "nombre_cliente": row[1],
            "direccion_envio": row[2],
            "telefono": row[3]
        })

        # --- 3. Dirección, teléfono, zona y ciudad (procedimientos PL/SQL) ---
        out_direccion = cur.var(str)
        out_telefono = cur.var(str)
        out_zona = cur.var(str)
        out_error = cur.var(str)
        cur.callproc("PK_V6_CLIENTE_OBTENER.P_DIR_TEL_CLIENTE", [
            empresa, cod_persona_cli, out_direccion, out_telefono, out_zona, out_error
        ])
        if out_error.getvalue():
            return jsonify({"error": out_error.getvalue()}), 400

        out_ciudad = cur.var(str)
        out_error2 = cur.var(str)
        cur.callproc("PK_V6_OBT_TG_CLASIFICACIONES.P_SACA_NOMBRE_CIUDAD", [
            empresa, out_zona.getvalue(), out_ciudad, out_error2
        ])
        if out_error2.getvalue():
            return jsonify({"error": out_error2.getvalue()}), 400

        result["direccion_envio"] = out_direccion.getvalue()
        result["telefono"] = out_telefono.getvalue()
        result["zona_geografica"] = out_zona.getvalue()
        result["ciudad"] = out_ciudad.getvalue()

        # --- 4. Tipo y modelo cliente ---
        sql_tipo = """
            SELECT ch.cod_tipo_clienteh, d.cod_modelo, d.cod_tipo_clienteh
            FROM cliente_hor ch
            JOIN ST_POL_CRE_TIPO_CLIENTE d ON d.empresa = ch.empresah AND d.cod_tipo_clienteh = ch.cod_tipo_clienteh
            WHERE ch.cod_clienteh = :cod_persona_cli
              AND ch.empresah = :empresa
              AND d.cod_politica = :cod_politica
        """
        cur.execute(sql_tipo, cod_persona_cli=cod_persona_cli, empresa=empresa, cod_politica=cod_politica)
        tipo_row = cur.fetchone()
        if tipo_row:
            result.update({
                "cod_tipo_clienteh": tipo_row[0],
                "cod_modelo": tipo_row[1],
                "tipo_clienteh": tipo_row[2]
            })
        else:
            result.update({
                "cod_tipo_clienteh": None,
                "cod_modelo": None,
                "tipo_clienteh": None
            })

        # --- 5. Cupos de consignación si corresponde ---
        if cod_tipo_pedido.upper() == "PC":
            sql_consigna = """
                SELECT cu.cupo_valor, cu.cupo_unidades, cu.observacion, cu.es_activo, cu.dias_gracia_cartera
                FROM ST_CLIENTE_CONSIGNACION cu
                WHERE cu.empresa = :empresa AND cu.cod_cliente = :cod_persona_cli AND cu.es_activo = 1
            """
            cur.execute(sql_consigna, empresa=empresa, cod_persona_cli=cod_persona_cli)
            cons_row = cur.fetchone()
            if cons_row:
                result.update({
                    "cupo_consignacion": cons_row[0],
                    "unidades_consignacion": cons_row[1],
                    "observacion_consignacion": cons_row[2],
                    "consignacion_activa": cons_row[3],
                    "dias_gracia_consignacion": cons_row[4]
                })
            else:
                result.update({
                    "cupo_consignacion": None,
                    "unidades_consignacion": None,
                    "observacion_consignacion": None,
                    "consignacion_activa": 0,
                    "dias_gracia_consignacion": None
                })

        # --- 6. Consultar cupo crédito, saldo actual y disponible ---
        out_cod_cat_cliente = cur.var(str)
        out_cli_aprobado_cupo = cur.var(float)
        cur.callproc("KS_CLIENTE_CUPO.P_CONSULTA_DATOS", [
            empresa, cod_persona_cli, 1, out_cod_cat_cliente, out_cli_aprobado_cupo
        ])
        result["cod_cat_cliente"] = out_cod_cat_cliente.getvalue()
        result["cupo_credito"] = out_cli_aprobado_cupo.getvalue() if out_cli_aprobado_cupo.getvalue() is not None else 0

        # Saldo actual capital
        saldo_actual = 0
        try:
            sql_saldo = "SELECT ks_cliente.saldo_actual_capital(:empresa, :cod_persona_cli) FROM dual"
            cur.execute(sql_saldo, empresa=empresa, cod_persona_cli=cod_persona_cli)
            saldo_row = cur.fetchone()
            saldo_actual = saldo_row[0] if saldo_row and saldo_row[0] is not None else 0
        except Exception:
            saldo_actual = 0

        result["saldo_actual"] = saldo_actual
        cupo_credito = result.get("cupo_credito") or 0
        result["cupo_disponible"] = float(cupo_credito) - float(saldo_actual)

        # Cartera vencida
        try:
            cartera_vencida = cur.callfunc(
                "ks_cliente.saldo_actual_corte",
                float,
                [empresa, cod_tipo_persona_cli , cod_persona_cli, datetime.date.today()]
            )
        except Exception:
            cartera_vencida = 0

        result["cartera_vencida"] = cartera_vencida

        # --- 7. Cuotas si tipo cliente es 'D' y no hay num_cuotas ---
        if result.get("cod_tipo_clienteh") == 'D' and not request.args.get('num_cuotas'):
            sql_cuotas = """
                SELECT x.num_cuotas, x.forma_pago_precio
                FROM St_Cliente_Polcre_d x
                WHERE x.empresa = :empresa
                  AND x.es_activo = 1
                  AND x.cod_politica = :cod_politica
                  AND x.cod_cliente = :cod_persona_cli
                ORDER BY x.num_cuotas DESC
            """
            cur.execute(sql_cuotas, empresa=empresa, cod_politica=cod_politica, cod_persona_cli=cod_persona_cli)
            cuo_row = cur.fetchone()
            if cuo_row:
                result["num_cuotas"] = cuo_row[0]
                result["cod_forma_pago"] = cuo_row[1]
            else:
                result["num_cuotas"] = None
                result["cod_forma_pago"] = None

        cur.close()
        return jsonify(result), 200

    except Exception as ex:
        if c:
            c.rollback()
            print(ex)
        return jsonify({"error": str(ex)}), 500
    finally:
        if c:
            c.close()

    """
    GET /cliente_info

    Loads ALL client info for order header (names, credit, consignation, category, address, phone, city, cups, balances, etc.)

    Query Parameters:
        empresa (int): Company code (required)
        cod_persona_cli (str): Client/person code (required)
        cod_politica (str): Credit policy code (required)
        cod_tipo_pedido (str): Order type code (required, e.g. 'PC')
        cod_pedido (str): Order code (optional, for consignation)
        cod_agencia (str): Agency code (optional, for category)
        cod_tipo_persona_cli (str): Client type code (optional, for cartera vencida)

    Returns:
        200: JSON with all client/policy/order info (flat dictionary)
        400: If parameters are missing or invalid
        404: If client not found or not valid for policy
        500: Internal or database error
    """
    c = None
    try:
        # --- Get and validate params ---
        empresa_str = request.args.get('empresa')
        cod_persona_cli = request.args.get('cod_persona_cli')
        cod_politica = request.args.get('cod_politica')
        cod_tipo_pedido = request.args.get('cod_tipo_pedido')
        cod_pedido = request.args.get('cod_pedido', None)
        cod_agencia = request.args.get('cod_agencia', None)
        cod_tipo_persona_cli = request.args.get('cod_tipo_persona_cli', None)

        if not all([empresa_str, cod_persona_cli, cod_politica, cod_tipo_pedido]):
            return jsonify({"error": "Missing required parameters (empresa, cod_persona_cli, cod_politica, cod_tipo_pedido)"}), 400

        try:
            empresa = int(empresa_str)
        except ValueError:
            return jsonify({"error": "'empresa' must be integer"}), 400

        c = get_oracle_connection()
        cur = c.cursor()

        result = {}

        # 1. --- Nombres, dirección, teléfono, ciudad ---
        sql_basic = """
        SELECT
            cli.cod_cliente,
            cli.apellido1 || ' ' || rtrim(cli.nombre) AS nombre,
            cli.direccion AS direccion_envio,
            cli.telefono
            
        FROM cliente cli
        WHERE cli.cod_cliente = :cod_persona_cli
          AND cli.empresa = :empresa
        """
        cur.execute(sql_basic, cod_persona_cli=cod_persona_cli, empresa=empresa)
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Client not found."}), 404
        result.update({
            "cod_persona_cli": row[0],
            "nombre_cliente": row[1],
            "direccion_envio": row[2],
            "telefono": row[3]
        })

        out_direccion = cur.var(str)
        out_telefono = cur.var(str)
        out_zona = cur.var(str)
        out_error = cur.var(str)

        cur.callproc("PK_V6_CLIENTE_OBTENER.P_DIR_TEL_CLIENTE", [
            empresa,
            cod_persona_cli,
            out_direccion,
            out_telefono,
            out_zona,
            out_error
        ])

        # Verifica error en la llamada
        if out_error.getvalue():
            # Si hay error, responde 400 o lo que prefieras
            return jsonify({"error": out_error.getvalue()}), 400

        # 2. Llama a PK_V6_OBT_TG_CLASIFICACIONES.P_SACA_NOMBRE_CIUDAD para el nombre de la ciudad

        out_ciudad = cur.var(str)
        out_error2 = cur.var(str)
        cur.callproc("PK_V6_OBT_TG_CLASIFICACIONES.P_SACA_NOMBRE_CIUDAD", [
            empresa,
            out_zona.getvalue(),
            out_ciudad,
            out_error2
        ])

        if out_error2.getvalue():
            # Si hay error, responde 400 o lo que prefieras
            return jsonify({"error": out_error2.getvalue()}), 400

        # 3. Actualiza el result dict

        result["direccion_envio"] = out_direccion.getvalue()
        result["telefono"] = out_telefono.getvalue()
        result["zona_geografica"] = out_zona.getvalue()
        result["ciudad"] = out_ciudad.getvalue()

        # 2. --- Tipo y modelo cliente ---
        sql_tipo = """
        SELECT ch.cod_tipo_clienteh, d.cod_modelo, d.cod_tipo_clienteh
        FROM cliente_hor ch
        JOIN ST_POL_CRE_TIPO_CLIENTE d ON d.empresa = ch.empresah AND d.cod_tipo_clienteh = ch.cod_tipo_clienteh
        WHERE ch.cod_clienteh = :cod_persona_cli
          AND ch.empresah = :empresa
          AND d.cod_politica = :cod_politica
        """
        cur.execute(sql_tipo, cod_persona_cli=cod_persona_cli, empresa=empresa, cod_politica=cod_politica)
        tipo_row = cur.fetchone()
        if tipo_row:
            result.update({
                "cod_tipo_clienteh": tipo_row[0],
                "cod_modelo": tipo_row[1],
                "tipo_clienteh": tipo_row[2]
            })
        else:
            result.update({
                "cod_tipo_clienteh": None,
                "cod_modelo": None,
                "tipo_clienteh": None
            })

        # 3. --- Cupos de consignación si corresponde ---
        if cod_tipo_pedido.upper() == "PC":
            # Chequeo si cliente tiene consignación activa
            sql_consigna = """
            SELECT cu.cupo_valor, cu.cupo_unidades, cu.observacion, cu.es_activo, cu.dias_gracia_cartera
            FROM ST_CLIENTE_CONSIGNACION cu
            WHERE cu.empresa = :empresa AND cu.cod_cliente = :cod_persona_cli AND cu.es_activo = 1
            """
            cur.execute(sql_consigna, empresa=empresa, cod_persona_cli=cod_persona_cli)
            cons_row = cur.fetchone()
            if cons_row:
                result.update({
                    "cupo_consignacion": cons_row[0],
                    "unidades_consignacion": cons_row[1],
                    "observacion_consignacion": cons_row[2],
                    "consignacion_activa": cons_row[3],
                    "dias_gracia_consignacion": cons_row[4]
                })
            else:
                result.update({
                    "cupo_consignacion": None,
                    "unidades_consignacion": None,
                    "observacion_consignacion": None,
                    "consignacion_activa": 0,
                    "dias_gracia_consignacion": None
                })

        # 4. --- Nombres de cliente por procedimiento PL/SQL (simulado como select) ---
        # (En la práctica: usar callproc o PL/SQL block si lo necesitas)
        # result["lv_nombre_cliente"] = result.get("nombre_cliente")

        # 5. --- Consultar cupo crédito, saldo actual y disponible usando procedimientos/funciones PL/SQL ---

        # --- Llama al procedimiento KS_CLIENTE_CUPO.P_CONSULTA_DATOS ---
        out_cod_cat_cliente = cur.var(str)
        out_cli_aprobado_cupo = cur.var(float)

        cur.callproc("KS_CLIENTE_CUPO.P_CONSULTA_DATOS", [
            empresa,
            cod_persona_cli,
            1,  # Opción 1: consulta
            out_cod_cat_cliente,
            out_cli_aprobado_cupo
        ])

        result["cod_cat_cliente"] = out_cod_cat_cliente.getvalue()
        result["cupo_credito"] = out_cli_aprobado_cupo.getvalue() if out_cli_aprobado_cupo.getvalue() is not None else 0

        # --- Llama la función para saldo_actual_capital (debe existir como FUNCTION que retorna un número) ---
        saldo_actual = 0
        try:
            # Si tu función es ks_cliente.saldo_actual_capital(empresa, cod_persona_cli)
            sql_saldo = "SELECT ks_cliente.saldo_actual_capital(:empresa, :cod_persona_cli) FROM dual"
            cur.execute(sql_saldo, empresa=empresa, cod_persona_cli=cod_persona_cli)
            saldo_row = cur.fetchone()
            saldo_actual = saldo_row[0] if saldo_row and saldo_row[0] is not None else 0
        except Exception as e:
            saldo_actual = 0  # Si hay error, lo dejas en cero o manejas el error

        result["saldo_actual"] = saldo_actual

        # --- Calcula cupo disponible ---
        cupo_credito = result.get("cupo_credito") or 0
        result["cupo_disponible"] = float(cupo_credito) - float(saldo_actual)

        # --- Cartera vencida (llama la función si existe) ---
        cartera_vencida = 0
        try:
            # Si tienes la función ks_cliente.saldo_actual_corte(empresa, cod_tipo_persona_cli, cod_persona_cli, sysdate)
            # cod_tipo_persona_cli puede venir de los parámetros, si no, pásalo como None o ajusta según lógica.
            sql_vencida = """
                          SELECT ks_cliente.saldo_actual_corte(:empresa, :cod_tipo_persona_cli, :cod_persona_cli, \
                                                               SYSDATE) \
                          FROM dual \
                          """
            cur.execute(sql_vencida, empresa=empresa, cod_tipo_persona_cli=cod_tipo_persona_cli,
                        cod_persona_cli=cod_persona_cli)
            vencida_row = cur.fetchone()
            cartera_vencida = vencida_row[0] if vencida_row and vencida_row[0] is not None else 0
        except Exception as e:
            cartera_vencida = 0  # Si falla, lo dejas en cero o logueas el error

        result["cartera_vencida"] = cartera_vencida

        # 6. --- Cuotas si tipo cliente es 'D' y no hay num_cuotas ---
        if result.get("cod_tipo_clienteh") == 'D' and not request.args.get('num_cuotas'):
            sql_cuotas = """
            SELECT x.num_cuotas, x.forma_pago_precio
            FROM St_Cliente_Polcre_d x
            WHERE x.empresa = :empresa
              AND x.es_activo = 1
              AND x.cod_politica = :cod_politica
              AND x.cod_cliente = :cod_persona_cli
            ORDER BY x.num_cuotas DESC
            """
            cur.execute(sql_cuotas, empresa=empresa, cod_politica=cod_politica, cod_persona_cli=cod_persona_cli)
            cuo_row = cur.fetchone()
            if cuo_row:
                result["num_cuotas"] = cuo_row[0]
                result["cod_forma_pago"] = cuo_row[1]
            else:
                result["num_cuotas"] = None
                result["cod_forma_pago"] = None

        cur.close()
        return jsonify(result), 200

    except Exception as ex:
        if c:
            c.rollback()
            print(ex)
        return jsonify({"error": str(ex)}), 500
    finally:
        if c:
            c.close()

@rmor.route('/vendedores_agencia', methods=['GET'])
@jwt_required()
def get_vendedores_agencia():
    """
    GET /vendedores_agencia

    Returns all salespersons (VEN) for a given company and agency.

    Query Parameters:
        empresa (int): Company code (required)
        cod_agencia (str): Agency code (required)

    Returns:
        200: JSON list of salespersons [{"nombre": ..., "cod_persona": ...}, ...]
        400: If parameters are missing or invalid
        500: On internal/database error
    """
    c = None
    try:
        empresa_str = request.args.get('empresa')
        cod_agencia = request.args.get('cod_agencia')

        if not all([empresa_str, cod_agencia]):
            return jsonify({"error": "Missing required parameters (empresa, cod_agencia)"}), 400

        try:
            empresa = int(empresa_str)
        except ValueError:
            return jsonify({"error": "'empresa' must be integer"}), 400

        c = get_oracle_connection()
        cur = c.cursor()

        sql = """
        SELECT a.nombre, a.cod_persona
        FROM persona a,
             tg_agencia_persona b
        WHERE a.empresa = :empresa
          AND a.cod_tipo_persona = 'VEN'
          AND b.empresa = a.empresa
          AND b.cod_tipo_persona = a.cod_tipo_persona
          AND b.cod_persona = a.cod_persona
          AND b.cod_agencia = :cod_agencia
        ORDER BY a.nombre
        """

        cur.execute(sql, empresa=empresa, cod_agencia=cod_agencia)
        rows = cur.fetchall()
        result = [{"nombre": r[0], "cod_persona_vendor": r[1]} for r in rows]

        cur.close()
        return jsonify(result), 200

    except Exception as ex:
        if c:
            c.rollback()
        return jsonify({"error": str(ex)}), 500
    finally:
        if c:
            c.close()


@rmor.route('/politica_credito_detalle', methods=['GET'])
@jwt_required()
def get_politica_credito_detalle():
    """
    GET /politica_credito_detalle

    Consulta y retorna el detalle de la política de crédito por número de cuotas para un cliente.
    Parámetros (query):
      - empresa (int): Código de empresa (requerido)
      - cod_politica (str): Código de política de crédito (requerido)
      - num_cuotas (int): Número de cuotas (requerido)
      - cod_persona_cli (str): Código de cliente (requerido)
      - cod_tipo_clienteh (str): Código tipo cliente horizontal (requerido para consulta modelo item)
    """
    c = None
    try:
        # --- Obtener y validar params ---
        empresa_str = request.args.get('empresa')
        cod_politica = request.args.get('cod_politica')
        num_cuotas_str = request.args.get('num_cuotas')
        cod_persona_cli = request.args.get('cod_persona_cli')
        cod_tipo_clienteh = request.args.get('cod_tipo_clienteh')

        if not all([empresa_str, cod_politica, num_cuotas_str, cod_persona_cli, cod_tipo_clienteh]):
            return jsonify({"error": "Missing required parameters (empresa, cod_politica, num_cuotas, cod_persona_cli, cod_tipo_clienteh)"}), 400

        try:
            empresa = int(empresa_str)
            num_cuotas = int(num_cuotas_str)
        except ValueError:
            return jsonify({"error": "'empresa' and 'num_cuotas' must be integer"}), 400

        c = get_oracle_connection()
        cur = c.cursor()
        result = {}

        # 1. Obtener lv_cod_TIPO_CLIENTE (REG_MODELO_ITEM.TIPO) con consulta a TG_MODELO_ITEM
        sql_tipo = """
            SELECT TIPO
            FROM TG_MODELO_ITEM
            WHERE EMPRESA = :empresa
              AND COD_MODELO = 'CLI1'
              AND COD_ITEM = :cod_tipo_clienteh
        """
        cur.execute(sql_tipo, empresa=empresa, cod_tipo_clienteh=cod_tipo_clienteh)
        row_tipo = cur.fetchone()
        lv_cod_TIPO_CLIENTE = row_tipo[0] if row_tipo else None
        result['lv_cod_TIPO_CLIENTE'] = lv_cod_TIPO_CLIENTE

        # 2. Consulta la política de crédito general
        out_es_activo = cur.var(int)
        out_por_interes = cur.var(float)
        out_factor_credito = cur.var(float)
        out_dias_vencimiento1_max = cur.var(int)
        out_dias_vencimiento1_min = cur.var(int)
        out_cod_forma_pago = cur.var(str)

        cur.callproc("stock.ks_politica_credito_d.consulta_datos", [
            empresa,
            cod_politica,
            num_cuotas,
            0,  # ¿Siempre 0 según el procedimiento?
            out_es_activo,
            out_por_interes,
            out_factor_credito,
            out_dias_vencimiento1_max,
            out_dias_vencimiento1_min,
            out_cod_forma_pago
        ])

        result.update({
            "es_activo": out_es_activo.getvalue(),
            "por_interes": out_por_interes.getvalue(),
            "factor_credito": out_factor_credito.getvalue(),
            "dias_vencimiento1_max": out_dias_vencimiento1_max.getvalue(),
            "dias_vencimiento1_min": out_dias_vencimiento1_min.getvalue(),
            "cod_forma_pago": out_cod_forma_pago.getvalue()
        })

        # 3. Si es distribuidor, consulta específica para el cliente
        reg_cliente = {
            "es_activo": None,
            "por_interes": None,
            "dias_vencimiento1_max": None,
            "dias_vencimiento1_min": None
        }
        if lv_cod_TIPO_CLIENTE == 'D':
            out_cliente_es_activo = cur.var(int)
            out_cliente_por_interes = cur.var(float)
            out_cliente_dias_vencimiento1_max = cur.var(int)
            out_cliente_dias_vencimiento1_min = cur.var(int)

            cur.callproc("stock.ks_politica_credito_d.consulta_cliente_datos", [
                empresa,
                cod_politica,
                num_cuotas,
                cod_persona_cli,
                1,
                out_cliente_es_activo,
                out_cliente_por_interes,
                out_cliente_dias_vencimiento1_max,
                out_cliente_dias_vencimiento1_min
            ])

            reg_cliente["es_activo"] = out_cliente_es_activo.getvalue()
            reg_cliente["por_interes"] = out_cliente_por_interes.getvalue()
            reg_cliente["dias_vencimiento1_max"] = out_cliente_dias_vencimiento1_max.getvalue()
            reg_cliente["dias_vencimiento1_min"] = out_cliente_dias_vencimiento1_min.getvalue()
            result["cliente_politica"] = reg_cliente

            # Si la política está inactiva para este cliente y es_pendiente = 'S', error
            if (reg_cliente["es_activo"] is None or reg_cliente["es_activo"] == 0):
                return jsonify({"error": f"Política de crédito para {num_cuotas} cuotas está desactivada para este cliente"}), 400
        else:
            # Si la política general está inactiva y es_pendiente = 'S', error
            if result["es_activo"] == 0:
                return jsonify({"error": f"Política de crédito para {num_cuotas} cuotas está desactivada"}), 400

        # 4. Combinar resultados finales según prioridad cliente/política general
        # (Así como en tu PL/SQL)
        result["factor_credito_final"] = result.get("factor_credito")
        result["por_interes_final"] = reg_cliente["por_interes"] if reg_cliente["por_interes"] else result.get("por_interes")
        result["dias_vencimiento1_max_final"] = reg_cliente["dias_vencimiento1_max"] if reg_cliente["dias_vencimiento1_max"] else result.get("dias_vencimiento1_max")
        result["dias_vencimiento1_min_final"] = reg_cliente["dias_vencimiento1_min"] if reg_cliente["dias_vencimiento1_min"] else result.get("dias_vencimiento1_min")

        # El campo de forma de pago solo si no estás en modo QUERY (en API siempre lo asignas)
        result["cod_forma_pago_final"] = result.get("cod_forma_pago")  # O de reg_cliente si tu lógica lo requiere

        cur.close()
        return jsonify(result), 200

    except Exception as ex:
        if c:
            c.rollback()
        return jsonify({"error": f"Error consultando política de crédito: {str(ex)}"}), 500
    finally:
        if c:
            c.close()


@rmor.route('/productos_disponibles', methods=['GET'])
@jwt_required()
def get_productos_disponibles():
    """
    GET /productos_disponibles

    Retorna productos activos filtrando por modelo, modelo_cat, item_cat (lista), empresa.

    Query Params:
      - empresa (int): Código de empresa (requerido)
      - cod_modelo_cat (str): Código de modelo categoría (requerido)
      - cod_item_cat (str): Lista de códigos de ítem cat, separados por coma, ejemplo: 'Y,E,T,L' (requerido)
      - cod_modelo (str): Código de modelo (requerido)
    """
    c = None
    try:
        empresa_str = request.args.get('empresa')
        cod_modelo_cat = request.args.get('cod_modelo_cat')
        cod_item_cat = request.args.get('cod_item_cat')
        cod_modelo = request.args.get('cod_modelo')

        # Validar requeridos
        if not all([empresa_str, cod_modelo_cat, cod_item_cat, cod_modelo]):
            return jsonify({"error": "Faltan parámetros requeridos (empresa, cod_modelo_cat, cod_item_cat, cod_modelo)"}), 400

        try:
            empresa = int(empresa_str)
        except ValueError:
            return jsonify({"error": "'empresa' debe ser un número entero"}), 400

        # Lista de items: 'Y,E,T,L' => ['Y', 'E', ...]
        cod_item_cat_list = [x.strip() for x in cod_item_cat.split(',') if x.strip()]

        c = get_oracle_connection()
        cur = c.cursor()

        sql = f"""
        SELECT 
            p.cod_producto,
            REPLACE(REPLACE(REPLACE(REPLACE(p.nombre, 'AÑO ', ''), ')', ''), '(', ''), 'XX ', '') AS nombre,
            p.precio,
            p.cod_marca,
            p.cod_modelo,
            p.cod_modelo,
            p.cod_item_cat
        FROM producto p
        WHERE p.activo = 'S'
          AND p.empresa = :empresa
          AND p.cod_modelo_cat = :cod_modelo_cat
          AND p.cod_modelo = :cod_modelo
          AND p.cod_item_cat IN ({','.join([':' + f'item{i}' for i in range(len(cod_item_cat_list))])})
        """

        # Construye los bindings
        params = {
            'empresa': empresa,
            'cod_modelo_cat': cod_modelo_cat,
            'cod_modelo': cod_modelo
        }
        for i, val in enumerate(cod_item_cat_list):
            params[f'item{i}'] = val

        cur.execute(sql, params)
        rows = cur.fetchall()
        cols = [desc[0].lower() for desc in cur.description]
        result = [dict(zip(cols, row)) for row in rows]

        cur.close()
        return jsonify(result), 200

    except Exception as ex:
        if c:
            c.rollback()
        return jsonify({"error": f"Error consultando productos: {str(ex)}"}), 500
    finally:
        if c:
            c.close()


@rmor.route('/procesar_detalle_producto', methods=['GET'])
@jwt_required()
def procesar_detalle_producto():
    """
    GET /procesar_detalle_producto

    Procesa el detalle de un producto en pedido, extrae lote, valida línea permitida en política,
    calcula descuentos y precios.

    Query Parameters:
        cod_producto (str): Código de producto (puede venir con '*' para lote) (requerido)
        empresa (int): Código de empresa (requerido)
        cod_politica (str): Código de política de crédito (requerido)
        num_cuotas (int): Número de cuotas (requerido)
        lv_cod_modelo_cat (str): Código de modelo de categoría (requerido)
        lv_cod_item_cat (str): Código de item de categoría (requerido)
        cod_promocion (str): Código de promoción (opcional)
    Returns:
        200: JSON con todos los datos procesados para el detalle de pedido
        400: Si faltan parámetros o validación
        500: Si ocurre error de BD
    """
    c = None
    try:
        # --- Obtener y validar params ---
        cod_producto = request.args.get('cod_producto')
        empresa = request.args.get('empresa')
        cod_politica = request.args.get('cod_politica')
        num_cuotas = request.args.get('num_cuotas')
        lv_cod_modelo_cat = request.args.get('lv_cod_modelo_cat')
        lv_cod_item_cat = request.args.get('lv_cod_item_cat')
        cod_promocion = request.args.get('cod_promocion', None)

        # Validaciones básicas
        if not all([cod_producto, empresa, cod_politica, num_cuotas, lv_cod_modelo_cat, lv_cod_item_cat]):
            return jsonify({"error": "Missing one or more required parameters (cod_producto, empresa, cod_politica, num_cuotas, lv_cod_modelo_cat, lv_cod_item_cat)"}), 400

        try:
            empresa = int(empresa)
            num_cuotas = int(num_cuotas)
        except Exception:
            return jsonify({"error": "'empresa' and 'num_cuotas' must be integers"}), 400

        # --- Procesa el producto/lote ---
        detalle = {
            "cod_producto": cod_producto,
            "cod_comprobante_lote": None,
            "tipo_comprobante_lote": None
        }
        # 1. Extraer lote si existe
        if "*" in cod_producto:
            posicion_pipe = cod_producto.find("*")
            detalle["cod_comprobante_lote"] = cod_producto[posicion_pipe+1:]
            if len(detalle["cod_comprobante_lote"]) == 6:
                detalle["cod_comprobante_lote"] = "A1-" + detalle["cod_comprobante_lote"]
            detalle["tipo_comprobante_lote"] = "LT"
            cod_producto_real = cod_producto[:posicion_pipe]
            detalle["cod_producto"] = cod_producto_real
        else:
            cod_producto_real = cod_producto

        # --- Lógica de producto (puedes ampliar) ---
        # Por ahora solo agrego el cod_producto procesado

        # --- Conexión Oracle ---
        c = get_oracle_connection()
        cur = c.cursor()

        # 2. Valida línea permitida para política
        # 2. Valida línea permitida para política usando bloque PL/SQL
        out_valida = cur.var(int)
        try:
            plsql = """
            DECLARE
                res BOOLEAN;
                res_num NUMBER;
            BEGIN
                res := KS_POLITICA_CREDITO_LINEA.EXISTE(
                    :empresa, :cod_politica, :num_cuotas, :cod_modelo, :cod_item
                );
                IF res THEN
                    res_num := 1;
                ELSE
                    res_num := 0;
                END IF;
                :out_valida := res_num;
            END;
            """
            cur.execute(
                plsql,
                {
                    "empresa": empresa,
                    "cod_politica": cod_politica,
                    "num_cuotas": num_cuotas,
                    "cod_modelo": lv_cod_modelo_cat,
                    "cod_item": lv_cod_item_cat,
                    "out_valida": out_valida
                }
            )
        except Exception as e:
            return jsonify({"error": f"Error llamando a KS_POLITICA_CREDITO_LINEA.EXISTE: {str(e)}"}), 500

        if out_valida.getvalue() == 0:
            return jsonify({
                "error": f"Línea de producto {lv_cod_item_cat} no permitida para esta política/cuotas.",
                "cod_politica": cod_politica,
                "num_cuotas": num_cuotas
            }), 400

        # 3. Lógica de descuento: Solo si no hay promoción
        descuento_producto = None
        if not cod_promocion:
            # Puedes reemplazar por llamada a tu proc o lógica PL/SQL real
            try:
                # Ejemplo con un paquete, personaliza el nombre real:
                out_descuento = cur.var(float)
                out_error = cur.var(str)
                cur.callproc(
                    "PK_OBTENER_ST_POLCRE_D_PRODUCT.P_SACA_POR_DESCUENTO",
                    [
                        cod_producto_real,
                        num_cuotas,
                        cod_politica,
                        empresa,
                        out_descuento,
                        None,   # fecha, por defecto SYSDATE
                        out_error
                    ]
                )
                if out_error.getvalue():
                    return jsonify({"error": out_error.getvalue()}), 400
                descuento_producto = out_descuento.getvalue()
                detalle["descuento_producto"] = descuento_producto
                detalle["descuento"] = descuento_producto if descuento_producto is not None else 0
            except Exception:
                detalle["descuento_producto"] = None
                detalle["descuento"] = 0
        else:
            detalle["descuento_producto"] = None
            detalle["descuento"] = 0

        # 4. Calcula precios (simulación, reemplaza por llamada real si aplica)
        try:
            # Ejemplo: podrías llamar a p_calcula_precios_v2 si es necesario
            # cur.callproc("P_CALCULA_PRECIOS_V2", [...])
            detalle["precios_actualizados"] = True  # Placeholder
        except Exception:
            detalle["precios_actualizados"] = False

        cur.close()
        return jsonify(detalle), 200

    except Exception as ex:
        if c:
            c.rollback()
        return jsonify({"error": str(ex)}), 500
    finally:
        if c:
            c.close()


@rmor.route('/obtener_descuento', methods=['GET'])
@jwt_required()
def obtener_descuento():
    """
    Calcula el porcentaje de descuento aplicando toda la lógica de F_OBTENER_DESCUENTO.
    Query Params:
        empresa: int
        cod_politica: int
        num_cuotas: int
        cod_producto: str
        lv_cod_modelo_cat: str
        lv_cod_item_cat: str
        cod_persona_cli: str
        cod_pedido: str
        cod_tipo_pedido: str
        secuencia: int
    Returns:
        200: JSON {"descuento": ...}
        400: Si faltan parámetros o hay error de lógica
        500: Si hay error de BD
    """
    c = None
    try:
        # Obtener y validar parámetros
        params = {}
        campos = ["empresa", "cod_politica", "num_cuotas", "cod_producto", "lv_cod_modelo_cat",
                  "lv_cod_item_cat", "cod_persona_cli", "cod_pedido", "cod_tipo_pedido", "secuencia"]
        for campo in campos:
            valor = request.args.get(campo)
            if not valor:
                return jsonify({"error": f"Missing parameter: {campo}"}), 400
            params[campo] = valor

        # Convertir a los tipos correctos
        params["empresa"] = int(params["empresa"])
        params["cod_politica"] = int(params["cod_politica"])
        params["num_cuotas"] = int(params["num_cuotas"])
        params["secuencia"] = int(params["secuencia"])

        c = get_oracle_connection()
        cur = c.cursor()
        descuento = 0

        # 1. P_SACA_POR_DESCUENTO_PRECIO (por persona)
        v_por_descuento = cur.var(float)
        v_codigo_error = cur.var(str)
        cur.callproc("PK_V6_OBTENER_ST_POL_CRE_PER.P_SACA_POR_DESCUENTO_PRECIO", [
            params["empresa"],
            params["cod_politica"],
            params["num_cuotas"],
            params["lv_cod_modelo_cat"],
            params["lv_cod_item_cat"],
            'CLI',
            params["cod_persona_cli"],
            v_por_descuento,
            v_codigo_error
        ])

        descuento = v_por_descuento.getvalue() or 0

        # 2. Si sigue en 0, P_SACA_POR_DESCUENTO_CLI
        if not descuento:
            v_por_descuento2 = cur.var(float)
            v_codigo_error2 = cur.var(str)
            cur.callproc("PK_OBTENER_ST_POLCRE_D_PRODUCT.P_SACA_POR_DESCUENTO_CLI", [
                params["cod_producto"],
                params["num_cuotas"],
                params["cod_politica"],
                params["empresa"],
                params["cod_persona_cli"],
                v_por_descuento2,
                None,  # fecha (SYSDATE en Oracle)
                v_codigo_error2
            ])
            descuento = v_por_descuento2.getvalue() or 0

        # 3. Si sigue en 0, P_SACA_POR_DESCUENTO
        if not descuento:
            v_por_descuento3 = cur.var(float)
            v_codigo_error3 = cur.var(str)
            cur.callproc("PK_OBTENER_ST_POLCRE_D_PRODUCT.P_SACA_POR_DESCUENTO", [
                params["cod_producto"],
                params["num_cuotas"],
                params["cod_politica"],
                params["empresa"],
                v_por_descuento3,
                None,  # fecha (SYSDATE)
                v_codigo_error3
            ])
            descuento = v_por_descuento3.getvalue() or 0

        # 4. Si sigue en 0, P_SACA_POR_DESCUENTO_PRECIO (por línea)
        if not descuento:
            v_por_descuento4 = cur.var(float)
            v_codigo_error4 = cur.var(str)
            cur.callproc("PK_V6_OBTENER_ST_POL_CRE_LIN.P_SACA_POR_DESCUENTO_PRECIO", [
                params["empresa"],
                params["cod_politica"],
                params["num_cuotas"],
                params["lv_cod_modelo_cat"],
                params["lv_cod_item_cat"],
                v_por_descuento4,
                v_codigo_error4
            ])
            descuento = v_por_descuento4.getvalue() or 0

        # 5. Si sigue en 0, consulta marca y KS_POLCRE_LINEA_MARCA.consulta_descuento
        if not descuento:
            cur.execute(
                "SELECT cod_marca FROM producto WHERE empresa=:empresa AND cod_producto=:cod_producto",
                empresa=params["empresa"],
                cod_producto=params["cod_producto"]
            )
            row = cur.fetchone()
            if row and row[0]:
                cod_marca = row[0]
                # Llamar a la función con SELECT FROM dual
                sql_func = """
                           SELECT KS_POLCRE_LINEA_MARCA.consulta_descuento(
                                          :empresa,
                                          :cod_politica,
                                          :num_cuotas,
                                          :lv_cod_modelo_cat,
                                          :lv_cod_item_cat,
                                          :cod_marca
                                  ) \
                           FROM dual \
                           """
                cur.execute(sql_func, {
                    "empresa": params["empresa"],
                    "cod_politica": params["cod_politica"],
                    "num_cuotas": params["num_cuotas"],
                    "lv_cod_modelo_cat": params["lv_cod_modelo_cat"],
                    "lv_cod_item_cat": params["lv_cod_item_cat"],
                    "cod_marca": cod_marca
                })
                func_row = cur.fetchone()
                descuento = func_row[0] if func_row and func_row[0] is not None else 0

        # Capar a 100 máximo
        if descuento > 100:
            descuento = 100

        # 6. Revisa si hay serie específica asociada
        v_numero_serie = None
        try:
            cur.execute("""
                SELECT numero_serie 
                FROM st_pedidos_detalles_s 
                WHERE cod_pedido=:cod_pedido AND cod_tipo_pedido=:cod_tipo_pedido
                AND empresa=:empresa AND secuencia=:secuencia
            """, cod_pedido=params["cod_pedido"], cod_tipo_pedido=params["cod_tipo_pedido"],
                 empresa=params["empresa"], secuencia=params["secuencia"])
            row = cur.fetchone()
            if row:
                v_numero_serie = row[0]
        except Exception:
            v_numero_serie = None

        # Si hay serie, buscar el descuento específico por serie
        if v_numero_serie:
            v_desc_serie = cur.var(float)
            # Devuelve un registro, pero solo usamos el campo descuento
            cur.callproc("ks_polcre_producto_serie.consulta", [
                params["empresa"],
                params["cod_politica"],
                params["cod_producto"],
                v_numero_serie,
                params["num_cuotas"],
                0  # Asumido (ver tu lógica)
            ])
            # El valor que retorna la función es un RECORD, aquí hay que adaptar según cómo se obtenga el valor en Python cx_Oracle (revisa la docu de tu ORM/driver)
            # Para ahora, lo dejamos como None, deberás completar aquí si tu driver permite obtener fields de records devueltos por procedimientos
            # descuento = ... # Extrae descuento del record
            # Por defecto:
            # descuento = v_desc_serie.getvalue() or descuento

        cur.close()
        return jsonify({"descuento": descuento}), 200

    except Exception as ex:
        if c:
            c.rollback()
        return jsonify({"error": str(ex)}), 500
    finally:
        if c:
            c.close()


@rmor.route('/calcula_precios', methods=['GET'])
@jwt_required()
def calcula_precios():
    """
    Endpoint para cálculo de precios usando tabla temporal y wrapper PL/SQL.
    """
    c = None
    try:
        # 1. Obtener y validar parámetros
        campos = [
            "empresa", "cod_agencia", "cod_producto", "cod_unidad", "cod_persona_cli",
            "cod_forma_pago", "cod_divisa", "fecha", "cod_forma_pago2",
            "cod_comprobante_lote", "tipo_comprobante_lote", "descuento",
            "num_cuotas", "pc_factor_credito", "cantidad_calculo",
            "lv_tiene_iva", "lv_tiene_ice", "anio_modelo"
        ]
        params = {}
        for campo in campos:
            valor = request.args.get(campo)
            if valor is None:
                return jsonify({"error": f"Missing parameter: {campo}"}), 400
            params[campo] = valor

        params["empresa"] = int(params["empresa"])
        params["cod_agencia"] = int(params["cod_agencia"])
        params["descuento"] = float(params["descuento"])
        params["num_cuotas"] = int(params["num_cuotas"])
        params["pc_factor_credito"] = float(params["pc_factor_credito"])
        params["cantidad_calculo"] = float(params["cantidad_calculo"])
        params["anio_modelo"] = int(params["anio_modelo"])
        # Formateo de fecha
        try:
            params["fecha"] = datetime.strptime(params["fecha"], "%Y-%m-%d")
        except Exception:
            try:
                params["fecha"] = datetime.strptime(params["fecha"], "%Y/%m/%d")
            except Exception:
                return jsonify({"error": "Formato de fecha inválido, usa YYYY-MM-DD o YYYY/MM/DD"}), 400

        # 2. Conexión a Oracle
        c = get_oracle_connection()
        cur = c.cursor()

        # 3. Consulta interes_mora, descuento, divisa
        lv_interes_mora = cur.var(float)
        lv_descuento = cur.var(float)
        lv_divisa = cur.var(str)
        lv_codigoerror = cur.var(str)
        cur.callproc("pk_v6_empresa_obtener.p_interes_mora_descuento", [
            params["empresa"],
            lv_interes_mora,
            lv_descuento,
            lv_divisa,
            lv_codigoerror
        ])
        if lv_codigoerror.getvalue():
            return jsonify({"error": lv_codigoerror.getvalue()}), 400

        # 4. Wrapper para consulta de lista de precios y tabla temporal
        session_id = str(uuid.uuid4())
        # El wrapper debe llenar la tabla TMP_LISTA_PRECIO con el resultado
        cur.callproc("WRAP_CON_REG_PRECIO_ACTUAL", [
            params["empresa"],              # p_cod_empresa
            params["cod_agencia"],          # p_cod_agencia
            params["cod_producto"],         # p_cod_producto
            params["cod_unidad"],           # p_cod_unidad
            params["cod_persona_cli"],      # p_cod_cliente
            params["cod_forma_pago"],       # p_cod_forma_pago
            params["cod_divisa"],           # p_cod_divisa
            params["fecha"],                # p_fecha (datetime)
            params["cod_forma_pago2"],      # p_cod_forma_pago2
            params["cod_comprobante_lote"], # p_lote_serie
            params["tipo_comprobante_lote"],# p_tipo_lote
            session_id                      # p_session_id
        ])
        # Recupera registro de la tabla temporal usando session_id
        cur.execute("SELECT * FROM TMP_LISTA_PRECIO WHERE SESSION_ID = :sid", sid=session_id)
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "No se pudo calcular el precio"}), 400
        columnas = [desc[0].lower() for desc in cur.description]
        reg_lista_precio = dict(zip(columnas, row))

        # 5. Traer la info de empresa para IVA
        cur.execute("SELECT * FROM EMPRESA WHERE EMPRESA=:empresa", empresa=params["empresa"])
        reg_empresa = cur.fetchone()
        if not reg_empresa:
            return jsonify({"error": "No existe la empresa"}), 400
        colnames = [desc[0].lower() for desc in cur.description]
        empresa_dict = dict(zip(colnames, reg_empresa))
        iva = empresa_dict.get("iva")
        if iva is None or iva == 0:
            return jsonify({"error": "Error NO TIENE DEFINIDO IVA EN LA TABLA EMPRESA"}), 400

        # 6. ICE
        ln_ice = 0
        if params["lv_tiene_ice"] == "S":
            ln_ice = cur.callfunc("computo.kg_reg2_general.parametro_sistema", float, [
                params["empresa"], "VEN", "CE"
            ])

        # 7. Cálculos (igual que tu lógica anterior)
        precio_lista = reg_lista_precio.get("precio")
        if round(params["pc_factor_credito"] * params["num_cuotas"], 2) > 1:
            ln_precio_lista = precio_lista * params["pc_factor_credito"] * params["num_cuotas"]
        else:
            ln_precio_lista = precio_lista

        if params["num_cuotas"] > 0:
            ln_precio = round(
                (ln_precio_lista - ln_precio_lista * (params["descuento"] / 100)) /
                params["num_cuotas"] * params["num_cuotas"], 2)
        else:
            ln_precio = round(
                ln_precio_lista - ln_precio_lista * (params["descuento"] / 100), 2)

        ln_por_interes = 0  # O traerlo de la cabecera, depende tu flujo real
        financiamiento = 0
        porcentaje_interes = 0

        if params["num_cuotas"] > 0:
            ln_valor_cuota = round(ln_precio / params["num_cuotas"], 2)
            if ln_por_interes > 0:
                v_pago = ln_precio / params["num_cuotas"]
                ln_capital = round(
                    v_pago * ((1 - pow(1 + (ln_por_interes / 1200), params["num_cuotas"] * -1)) / (ln_por_interes / 1200)), 2)
                ln_financiamiento = ln_precio - ln_capital
            else:
                ln_financiamiento = 0
            ln_suma_financiamiento = ln_financiamiento
            if ln_suma_financiamiento < 0:
                ln_suma_financiamiento = 0
            financiamiento = round(ln_suma_financiamiento * params["cantidad_calculo"], 2)
            porcentaje_interes = ln_por_interes
        else:
            financiamiento = 0
            porcentaje_interes = 0

        # IVA
        if params["lv_tiene_iva"] == "S":
            if params["cantidad_calculo"] > 0:
                vln_precio_sin_iva = (ln_precio - (financiamiento / params["cantidad_calculo"])) / (1 + (iva / 100))
            else:
                vln_precio_sin_iva = 0
            valor_iva = round((vln_precio_sin_iva * (iva / 100)) * params["cantidad_calculo"], 2)
        else:
            vln_precio_sin_iva = ln_precio
            valor_iva = 0

        # ICE
        ice = 0
        if params["lv_tiene_ice"] == "S":
            # Si tienes lógica adicional, agrégala aquí, o usa ln_ice calculado antes
            ice = ln_ice
        else:
            ice = 0

        valor_linea = round((vln_precio_sin_iva * params["cantidad_calculo"]) - ice, 2)
        ln_total_linea = (
            (valor_linea or 0) + (valor_iva or 0) + (ice or 0) + (financiamiento or 0)
        )

        # Armar el JSON resultado
        resultado = {
            "precio_lista": precio_lista,
            "precio_descontado": ln_precio,
            "precio": round(ln_precio_lista, 2),
            "financiamiento": financiamiento,
            "porcentaje_interes": porcentaje_interes,
            "valor_iva": valor_iva,
            "ice": ice,
            "valor_linea": valor_linea,
            "ln_total_linea": ln_total_linea,
            "reg_lista_precio": reg_lista_precio
        }

        return jsonify(resultado), 200

    except Exception as ex:
        if c:
            c.rollback()
        return jsonify({"error": str(ex)}), 500
    finally:
        if c:
            c.close()

@rmor.route('/direcciones_cliente', methods=['GET'])
@jwt_required()
def direcciones_cliente():
    """
    Retorna todas las direcciones activas de un cliente.
    Query Params:
        empresa: int
        cod_persona_cli: str
    Returns:
        200: JSON listado de direcciones
        400: Si faltan parámetros
        500: Error de base de datos
    """
    c = None
    try:
        # 1. Parámetros obligatorios
        empresa = request.args.get("empresa")
        cod_persona_cli = request.args.get("cod_persona_cli")
        if not empresa or not cod_persona_cli:
            return jsonify({"error": "Faltan parámetros: empresa y cod_persona_cli"}), 400
        empresa = int(empresa)

        # 2. Conexión a la BD
        c = get_oracle_connection()
        cur = c.cursor()

        # 3. Consulta de direcciones activas
        sql = """
            SELECT 
                cod_direccion,
                cod_cliente,
                ciudad,
                direccion,
                direccion_larga,
                es_activo
            FROM ST_CLIENTE_DIRECCION_GUIAS
            WHERE empresa = :empresa
              AND cod_cliente = :cod_persona_cli
              AND es_activo = 1
        """
        cur.execute(sql, empresa=empresa, cod_persona_cli=cod_persona_cli)
        columnas = [col[0].lower() for col in cur.description]
        resultados = [
            dict(zip(columnas, row)) for row in cur.fetchall()
        ]
        cur.close()
        return jsonify(resultados), 200

    except Exception as ex:
        if c:
            c.rollback()
        return jsonify({"error": str(ex)}), 500
    finally:
        if c:
            c.close()

@rmor.route('/consulta_existencia', methods=['GET'])
@jwt_required()
def consulta_existencia():
    """
    Consulta existencias e inventario para un producto, agencia y empresa.
    Query Params:
      empresa: int
      agencia: int
      cod_producto: str
      unidad: str
    Returns:
      200: JSON con los datos de inventario
      400/500: error
    """
    c = None
    try:
        # 1. Obtener parámetros
        campos = ["empresa", "cod_agencia", "cod_producto", "cod_unidad"]
        params = {}
        for campo in campos:
            valor = request.args.get(campo)
            if valor is None:
                return jsonify({"error": f"Missing parameter: {campo}"}), 400
            params[campo] = valor
        params["empresa"] = int(params["empresa"])
        params["agencia"] = int(params["cod_agencia"])

        # 2. Conexión Oracle
        c = get_oracle_connection()
        cur = c.cursor()

        # 3. Llamar procedimiento de existencia (adaptado según tu entorno real)
        existencia = cur.callfunc(
            "KS_INVENTARIO.CONSULTA_EXISTENCIA", float, [
                params["empresa"],
                params["agencia"],
                params["cod_producto"],
                params["cod_unidad"],
                datetime.now(),
                1,      # Suplir los otros flags como en tu lógica real
                'A',
                1
            ]
        )

        # 4. Consultar inventarios adicionales
        cur.execute("""
            SELECT 
                SUM(NVL(inv_b1, 0)) AS inv_b1,
                SUM(DECODE(cod_bodega, 2, NVL(inv_mp, 0), 0)) AS inv_mp,
                SUM(DECODE(cod_bodega, 3, NVL(inv_linea, 0) - NVL(inv_calidad, 0), 0)) AS inv_lin,
                SUM(DECODE(cod_bodega, 3, NVL(inv_calidad, 0), 0)) AS inv_calidad,
                SUM(NVL(inv_dc, 0)) AS inv_dc
            FROM VT_INVENTARIO_CKD
            WHERE cod_producto = :cod_producto
              AND empresa = :empresa
              AND cod_estado_producto = 'A'
        """, cod_producto=params["cod_producto"], empresa=params["empresa"])
        inv_row = cur.fetchone()
        colnames = [desc[0].lower() for desc in cur.description]
        inventarios = dict(zip(colnames, inv_row))

        # Combina resultados
        resultado = {
            "empresa": params["empresa"],
            "agencia": params["agencia"],
            "cod_producto": params["cod_producto"],
            "unidad": params["cod_unidad"],
            "existencia": existencia
        }
        resultado.update(inventarios)

        return jsonify(resultado), 200

    except Exception as ex:
        if c:
            c.rollback()
        return jsonify({"error": str(ex)}), 500
    finally:
        if c:
            c.close()

@rmor.route('/generar__cod_pedido', methods=['GET', 'POST'])
@jwt_required()
def generar_pedido():
    """
    empresa, cod_agencia, cod_tipo_pedido, cod_pedido (puede venir vacío o None).
    Return: cod_pedido generado y cod_tipo_pedido.
    """
    c = None
    try:
        # Recibir parámetros
        campos = ['empresa', 'cod_agencia', 'cod_tipo_pedido', 'cod_pedido']
        params = {}
        data = request.get_json() if request.method == 'POST' else request.args
        for campo in campos:
            valor = data.get(campo)
            if campo in ('empresa', 'cod_agencia') and valor is not None:
                valor = int(valor)
            params[campo] = valor if valor is not None else None
            if campo in ('empresa', 'cod_agencia', 'cod_tipo_pedido') and params[campo] is None:
                return jsonify({"error": f"Falta el parámetro: {campo}"}), 400

        # Conexión
        c = get_oracle_connection()
        cur = c.cursor()

        # PREPARAR variables de error y cod_pedido (IN OUT)
        lv_codigo_error = cur.var(str)
        cod_pedido_var = cur.var(str)
        cod_pedido_inicial = params.get('cod_pedido', None)
        cod_pedido_var.setvalue(0, cod_pedido_inicial if cod_pedido_inicial else "")

        # Paso 1: obtener secuencia de pedido
        cur.callproc("PK_OBTENER_ORDEN.P_SACA_SECUENCIA_PEDIDO", [
            params['empresa'],
            params['cod_agencia'],
            params['cod_tipo_pedido'],
            cod_pedido_var,    # IN OUT: se actualizará con el nuevo código
            lv_codigo_error
        ])
        if lv_codigo_error.getvalue():
            c.rollback()
            return jsonify({"error": f"Error secuencia pedido: {lv_codigo_error.getvalue()}"}), 400

        nuevo_cod_pedido = cod_pedido_var.getvalue()

        # Paso 2: actualizar la secuencia en tabla ORDEN
        lv_codigo_error2 = cur.var(str)
        cur.callproc("PK_ACTUALIZAR_ORDEN.P_ACTUALIZA_SECUENCIA_PEDIDO", [
            params['empresa'],
            params['cod_agencia'],
            params['cod_tipo_pedido'],
            1,  # fijo según el ejemplo
            lv_codigo_error2
        ])
        if lv_codigo_error2.getvalue():
            c.rollback()
            return jsonify({"error": f"Error actualizando secuencia: {lv_codigo_error2.getvalue()}"}), 400

        c.commit()
        return jsonify({
            "success": True,
            "cod_pedido": nuevo_cod_pedido,
            "cod_tipo_pedido": params['cod_tipo_pedido']
        }), 200

    except Exception as ex:
        if c:
            c.rollback()
        return jsonify({"error": str(ex)}), 500
    finally:
        if c:
            c.close()


##HELPERS DEUDA TECNICA CREAR UN HELPER.PY

def parse_fecha(valor):
    if not valor:
        return None
    if isinstance(valor, datetime):
        return valor
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(valor[:19], fmt)
        except Exception:
            continue
    raise ValueError(f"Formato de fecha inválido: {valor}")

@rmor.route('/guardar_pedido', methods=['POST'])
@jwt_required()
def guardar_pedido():
    """
    Guarda la cabecera y los detalles de un pedido.
    - Recibe JSON:
      {
        "cabecera": {...},
        "detalles": [{...}, {...}, ...]
      }
    - Convierte todas las claves a mayúsculas antes de procesar.
    - Valida obligatorios, hace rollback si hay error.
    """
    c = None
    try:
        data = request.get_json()
        if not data or "cabecera" not in data or "detalles" not in data:
            return jsonify({"error": "Se requiere 'cabecera' y 'detalles' en el JSON"}), 400

        # Convertir todas las claves a mayúsculas
        def keys_to_upper(d):
            return {k.upper(): v for k, v in d.items()}

        cab = keys_to_upper(data["cabecera"])
        detalles = [keys_to_upper(det) for det in data["detalles"]]
        if not isinstance(detalles, list) or len(detalles) == 0:
            return jsonify({"error": "La lista 'detalles' no puede estar vacía"}), 400

        # Conexión y cursor
        c = get_oracle_connection()
        cur = c.cursor()

        # -------- INSERTAR CABECERA ---------
        campos_cab = [
            'COD_TIPO_PERSONA_VEN',
            'TIENE_ICE',
            'ES_PENDIENTE',
            'OBSERVACIONES',
            'COD_TIPO_PEDIDO',
            'COD_LIQUIDACION',
            'CIUDAD',
            'COD_PEDIDO',
            'ES_APROBADO_VEN',
            'ES_BLOQUEADO',
            'ES_APROBADO_CAR',
            'REVISADO',
            'ES_FACTURADO',
            'ES_ANULADO',
            'ES_PEDIDO_REPUESTOS',
            'ADICIONADO_POR',
            'MODIFICADO_POR',
            'COD_PERSONA_VEN',
            'COD_FORMA_PAGO',
            'COD_TIPO_PERSONA_CLI',
            'COD_PERSONA_CLI',
            'COD_TIPO_PERSONA_GAR',
            'DIRECCION_ENVIO',
            'TIPO_PEDIDO',
            'COD_POLITICA',
            'ICE',
            'TELEFONO',
            'DIAS_VALIDEZ',
            'COD_BODEGA_DESPACHO',
            'COD_AGENCIA',
            'EMPRESA',
            'NUM_CUOTAS',
            'VALOR_PEDIDO',
            'FECHA_MODIFICACION',
            'FECHA_ADICION',
            'FECHA_PEDIDO',
            'FINANCIAMIENTO',
            'COMPROBANTE_MANUAL',
            'ES_FACTURA_CONSIGNACION'
        ]

        valores_cab = []
        for campo in campos_cab:
            if campo not in cab:
                c.rollback()
                return jsonify({"error": f"Falta el campo obligatorio en cabecera: {campo}"}), 400
            valores_cab.append(cab[campo])

        # Conversión de fechas si son string
        for campo_fecha in ["FECHA_PEDIDO", "FECHA_ADICION", "FECHA_MODIFICACION"]:
            if campo_fecha in campos_cab:
                idx = campos_cab.index(campo_fecha)
                valores_cab[idx] = parse_fecha(valores_cab[idx])

        # Insertar cabecera
        sql_cab = f"""
            INSERT INTO JAHER.ST_PEDIDOS_CABECERAS ({', '.join(campos_cab)})
            VALUES ({', '.join([':' + str(i + 1) for i in range(len(campos_cab))])})
        """
        cur.execute(sql_cab, valores_cab)

        # -------- INSERTAR DETALLES ---------
        campos_det = [
            'ES_PENDIENTE',
            'COD_TIPO_PEDIDO',
            'TIPO_CANTIDAD',
            'COD_PEDIDO',
            'ES_ANULADO',
            'COD_PRODUCTO',
            'COD_TIPO_PRODUCTO',
            'VALOR_LINEA',
            'PLAZO',
            'ICE',
            'COD_AGENCIA',
            'EMPRESA',
            'NUM_CUOTAS',
            'VALOR_IVA',
            'COD_CLIENTE',
            'PRECIO_LISTA',
            'PRECIO_DESCONTADO',
            'PRECIO',
            'CANTIDAD_PEDIDA',
            'SECUENCIA',
            'COD_DIRECCION',
            'DESCUENTO',
            'CANTIDAD_DESPACHADA',
            'FINANCIAMIENTO',
            'PORCENTAJE_INTERES',
            'CANTIDAD_PRODUCIDA',
            'ES_CONFIRMADO_BOD',
            'CANTIDAD_A_ENVIAR'
        ]

        sql_det = f"""
            INSERT INTO JAHER.ST_PEDIDOS_DETALLES ({', '.join(campos_det)})
            VALUES ({', '.join([':' + str(i + 1) for i in range(len(campos_det))])})
        """

        for det in detalles:
            valores_det = []
            for campo in campos_det:
                if campo not in det:
                    c.rollback()
                    return jsonify({"error": f"Falta el campo obligatorio en detalle: {campo}"}), 400
                valores_det.append(det[campo])
            cur.execute(sql_det, valores_det)

        c.commit()
        return jsonify({"msg": "Pedido guardado exitosamente", "cod_pedido": cab["COD_PEDIDO"]}), 200

    except Exception as ex:
        if c:
            c.rollback()
        return jsonify({"error": str(ex)}), 500
    finally:
        if c:
            c.close()


@rmor.route('/obtener_cod_liquidacion', methods=['GET'])
@jwt_required()
def obtener_cod_liquidacion():
    """
    Devuelve el código de liquidación usando el procedimiento PL/SQL.
    Params: empresa, cod_agencia (la fecha de pedido es el día actual, tomada del backend)
    """
    c = None
    try:
        empresa = request.args.get('empresa')
        cod_agencia = request.args.get('cod_agencia')
        if not empresa or not cod_agencia:
            return jsonify({"error": "Faltan parámetros: empresa, cod_agencia"}), 400

        empresa = int(empresa)
        cod_agencia = int(cod_agencia)
        fecha_pedido = datetime.now()  # <-- Aquí se toma la fecha actual del sistema

        c = get_oracle_connection()
        cur = c.cursor()

        cod_liquidacion = cur.var(str)
        lv_codigoerror = cur.var(str)

        cur.callproc('PK_V6_OBTENER_LIQUIDACION.P_SACA_COD_LIQUIDACION', [
            empresa,
            cod_agencia,
            fecha_pedido,
            cod_liquidacion,
            lv_codigoerror
        ])

        if lv_codigoerror.getvalue():
            return jsonify({"error": lv_codigoerror.getvalue()}), 400

        return jsonify({
            "cod_liquidacion": cod_liquidacion.getvalue(),
            "fecha_pedido_usada": fecha_pedido.strftime("%Y-%m-%d %H:%M:%S")
        }), 200

    except Exception as ex:
        if c:
            c.rollback()
        return jsonify({"error": str(ex)}), 500
    finally:
        if c:
            c.close()


@rmor.route('/pedidos_list', methods=['GET'])
@jwt_required()
def listar_pedidos_por_fecha():
    """
    Lista las cabeceras de pedidos entre dos fechas de pedido, y filtra por cod_agencia si se provee.
    """
    c = None
    try:
        fecha_ini = request.args.get('fecha_ini')
        fecha_fin = request.args.get('fecha_fin')
        cod_agencia = request.args.get('cod_agencia')  # puede ser None

        if not fecha_ini or not fecha_fin:
            return jsonify({"error": "Debe indicar fecha_ini y fecha_fin en el formato YYYY-MM-DD"}), 400

        # Validar y convertir fechas
        try:
            fecha_ini_dt = datetime.strptime(fecha_ini, "%Y-%m-%d")
            fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")
        except Exception:
            return jsonify({"error": "Formato de fecha inválido, debe ser YYYY-MM-DD"}), 400

        c = get_oracle_connection()
        cur = c.cursor()

        sql = """
            SELECT *
            FROM JAHER.ST_PEDIDOS_CABECERAS
            WHERE FECHA_PEDIDO BETWEEN :ini AND :fin
        """
        params = {"ini": fecha_ini_dt, "fin": fecha_fin_dt}

        # Si cod_agencia viene como parámetro, agrega el filtro
        if cod_agencia:
            sql += " AND COD_AGENCIA = :cod_agencia"
            params["cod_agencia"] = cod_agencia

        sql += " ORDER BY FECHA_PEDIDO DESC"

        cur.execute(sql, params)
        rows = cur.fetchall()
        columnas = [col[0] for col in cur.description]
        pedidos = [dict(zip(columnas, row)) for row in rows]
        return jsonify(pedidos), 200

    except Exception as ex:
        if c:
            c.rollback()
        return jsonify({"error": str(ex)}), 500
    finally:
        if c:
            c.close()

@rmor.route('/pedido_detalle', methods=['GET'])
@jwt_required()
def obtener_pedido_con_detalles():
    """
    Devuelve la cabecera y detalles de un pedido filtrando por cod_pedido, empresa, cod_tipo_pedido.
    """
    c = None
    try:
        cod_pedido = request.args.get('cod_pedido')
        empresa = request.args.get('empresa')
        cod_tipo_pedido = request.args.get('cod_tipo_pedido')

        if not cod_pedido:
            return jsonify({"error": "Debe indicar cod_pedido en los parámetros"}), 400

        c = get_oracle_connection()
        cur = c.cursor()

        # Buscar cabecera
        sql_cab = "SELECT * FROM JAHER.ST_PEDIDOS_CABECERAS WHERE COD_PEDIDO = :cod_pedido"
        params = {'cod_pedido': cod_pedido}
        if empresa:
            sql_cab += " AND EMPRESA = :empresa"
            params['empresa'] = empresa
        if cod_tipo_pedido:
            sql_cab += " AND COD_TIPO_PEDIDO = :cod_tipo_pedido"
            params['cod_tipo_pedido'] = cod_tipo_pedido

        cur.execute(sql_cab, params)
        cab_row = cur.fetchone()
        if not cab_row:
            return jsonify({"error": "No existe pedido"}), 404

        columnas_cab = [col[0] for col in cur.description]
        cabecera = dict(zip(columnas_cab, cab_row))

        # Buscar detalles
        sql_det = """
            SELECT * FROM JAHER.ST_PEDIDOS_DETALLES
            WHERE COD_PEDIDO = :cod_pedido
        """
        params_det = {'cod_pedido': cod_pedido}
        if empresa:
            sql_det += " AND EMPRESA = :empresa"
            params_det['empresa'] = empresa
        if cod_tipo_pedido:
            sql_det += " AND COD_TIPO_PEDIDO = :cod_tipo_pedido"
            params_det['cod_tipo_pedido'] = cod_tipo_pedido

        cur.execute(sql_det, params_det)
        rows_det = cur.fetchall()
        columnas_det = [col[0] for col in cur.description]
        detalles = [dict(zip(columnas_det, row)) for row in rows_det]

        return jsonify({"cabecera": cabecera, "detalles": detalles}), 200

    except Exception as ex:
        if c:
            c.rollback()
        return jsonify({"error": str(ex)}), 500
    finally:
        if c:
            c.close()