import cx_Oracle
from os import getenv
import dotenv

dotenv.load_dotenv()


def connection(user, password):
    conexion = None
    try:
        ip = getenv("IP")
        port = getenv("PORT")
        sid = getenv("SID")

        # Validaciones
        if not ip:
            raise ValueError("La variable de entorno 'IP' no está definida.")
        if not port:
            raise ValueError("La variable de entorno 'PORT' no está definida.")
        if not sid:
            raise ValueError("La variable de entorno 'SID' no está definida.")

        dsn = cx_Oracle.makedsn(ip, port, sid)

        conexion = cx_Oracle.connect(
            user=user,
            password=password,
            dsn=dsn
        )
        print('Conectado a Oracle Database', conexion.version)

    except Exception as err:
        print('Error en la conexión a la base de datos:', err)

    return conexion
def connection_test(user,password):
    try:

        conexion = cx_Oracle.connect(
            user=user,
            password=password,
            dsn=cx_Oracle.makedsn(getenv("IP"), getenv("PORT"), getenv("SID"))
        )
    except Exception as err:
        return False
    else:
        return True


def call_func(SQL, out_type, parameters):
    try:
        conexion = connection()
        cur_01 = conexion.cursor()
        correct = cur_01.callfunc(SQL, out_type, parameters)
    except Exception as err:
        print('Error', err)
    else:
        print('Funcion ejecutada corectamente!')
    conexion.close()
    return correct


def execute_sql(SQL,user,password):
    try:
        conexion = connection(user,password)
        cur_01 = conexion.cursor()
        cur_01.execute(SQL)
        correct = cur_01.fetchall()
    except Exception as err:
        print('Error', err)
    else:
        print('Sentencia SQL ejecutada correctamente!')
    conexion.close()
    return correct

def infoMotor(motor):
    # Configura conexion
    c = connection(getenv("USERORA"), getenv("PASSWORD"))
    # Crea un cursor
    cursor = c.cursor()
    # Define el bloque PL/SQL
    plsql_block = """
        DECLARE
            v_empresa       NUMBER := 20; -- Reemplaza con el valor adecuado
            v_numero_motor  ST_PROD_PACKING_LIST.COD_MOTOR%TYPE := :1; -- Reemplaza con el valor adecuado
            v_distribuidor  VARCHAR2(100); -- Variable de salida
            v_cod_producto  VARCHAR2(100); -- Variable de salida
            v_numero_chasis VARCHAR2(100); -- Variable de salida
            v_importacion VARCHAR2(100); -- Variable de salida
            v_nombreDistribuidor VARCHAR2(100);--Variable de salida
            REG_CLIENTE CLIENTE%ROWTYPE;
	        REG_VALORACION TC_VALORACION%ROWTYPE;
        BEGIN
            ks_casos_postventas.ps_obt_datos_moto_CLI(v_empresa, v_numero_motor, v_distribuidor, v_cod_producto, v_numero_chasis);
            IF v_distribuidor IS NOT NULL  THEN                            
            REG_CLIENTE := KS_CLIENTE.CONSULTA(v_empresa, v_distribuidor, 0);
            v_nombreDistribuidor:= REG_CLIENTE.APELLIDO1||' '||REG_CLIENTE.NOMBRE;

        END IF;

            REG_VALORACION:=KC_VALORACION.CONSULTA_X_SERIE(v_empresa, v_numero_motor,0);
            v_importacion:=REG_VALORACION.FECHA||' - '  ||REG_VALORACION.NOMBRE  ;

            :2 := v_distribuidor;
            :3 := v_cod_producto;
            :4 := v_numero_chasis;
            :5 := v_importacion;
            :6 := v_nombreDistribuidor;

            END;
        """
    # Define variables para almacenar los resultados
    distribuidor = cursor.var(cx_Oracle.STRING)
    cod_producto = cursor.var(cx_Oracle.STRING)
    numero_chasis = cursor.var(cx_Oracle.STRING)
    importacion = cursor.var(cx_Oracle.STRING)
    nombre_distribuidor = cursor.var(cx_Oracle.STRING)

    # Ejecuta el bloque PL/SQL con parámetros OUT
    cursor.execute(plsql_block, [motor, distribuidor, cod_producto, numero_chasis, importacion, nombre_distribuidor])

    # cursor.execute(plsql_block, ('163FMLKA033221', distribuidor, cod_producto, numero_chasis, importacion, nombre_distribuidor))

    # print("Distribuidor:", distribuidor.getvalue())
    # print("Código de Producto:", cod_producto.getvalue())
    # print("Número de Chasis:", numero_chasis.getvalue())
    # print("Importación:", importacion.getvalue())
    # print("Nombre del Distribuidor:", nombre_distribuidor.getvalue())
    cursor.close()
    c.close()
    return [distribuidor.getvalue(), cod_producto.getvalue(), numero_chasis.getvalue(), importacion.getvalue(),
            nombre_distribuidor.getvalue()]