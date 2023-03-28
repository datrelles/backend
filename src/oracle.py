import cx_Oracle
from os import getenv
import dotenv

dotenv.load_dotenv()


def connection(user,password):
    try:

        conexion = cx_Oracle.connect(
            user=user,
            password=password,
            dsn=cx_Oracle.makedsn(getenv("IP"), getenv("PORT"), getenv("SID"))
        )
    except Exception as err:
        print('Error en la conexion a la base de datos. Error:', err)
    else:
        print('Conectado a Oracle Database', conexion.version)
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