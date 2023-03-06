import cx_Oracle

def connection():
    try:
        conexion = cx_Oracle.connect(
            user='stock',
            password='stock',
            dsn=cx_Oracle.makedsn('192.168.51.73', 1521, 'mlgye01')
        )
    except Exception as err:
        print('Error en la conexion a la base de datos. Error:', err)
    else:
        print('Conectado a Oracle Database', conexion.version)
    return conexion

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
    return  correct

def execute_sql(SQL):
    try:
        conexion = connection()
        cur_01 = conexion.cursor()
        cur_01.execute(SQL)
        correct = cur_01.fetchall()
    except Exception as err:
        print('Error', err)
    else:
        print('Sentencia SQL ejecutada correctamente!')
    conexion.close()
    return correct