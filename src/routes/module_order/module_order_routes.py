from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.routes.module_order.db_connection import get_oracle_connection
import datetime

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
