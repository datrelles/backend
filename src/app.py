import json

from flask import Flask, render_template, request, redirect, url_for, jsonify
from config import config
from src import oracle
import numpy

app=Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/api-packing-list', methods = ['GET'])
def byYear():
    class create_dict(dict):

        # __init__ function
        def __init__(self):
            self = dict()

            # Function to add key:value

        def add(self, key, value):
            self[key] = value

    year = request.args.get('year')

    if year == None:
        year = 'P.ANIO'

    array = oracle.execute_sql(
        'select ROWNUM, P.COD_PRODUCTO, P.COD_MOTOR, P.COD_CHASIS, P.CAMVCPN, P.ANIO, P.COD_COLOR, P.CILINDRAJE, P.TONELAJE, P.OCUPANTES, P.MODELO, P.CLASE, P.SUBCLASE, P.FECHA_ADICION, P.FECHA_MODIFICACION, V.COD_LIQUIDACION, V.NOMBRE '
        'from ST_PROD_PACKING_LIST P, VT_VALORACION_SERIE V where P.COD_MOTOR = V.NUMERO_SERIE AND P.ANIO = '+year)
    mydict = create_dict()
    for row in array:
        mydict.add(row[0],({"CODPRODUC":row[1],"CODMOTOR":row[2],"CODCHASIS":row[3], "CPN":row[4], "YEAR":row[5],"COLOR":row[6],"CILINDRAJE":row[7],"TONELAJE":row[8], "OCUPANTES":row[9], "MODELO":row[10],"CLASE":row[11], "SUBCLASE":row[12], "FECHA CREACION":row[13], "FECHA MODIFICACION":row[14], "CODIGO LIQUIDACION":row[15], "IMPORTACION":row[16]}))
    stud_json = json.dumps(mydict, indent=2, default=str)
    return stud_json

@app.route('/api-packing-list-by-code', methods = ['GET'])
def byCode():
    class create_dict(dict):

        # __init__ function
        def __init__(self):
            self = dict()

            # Function to add key:value

        def add(self, key, value):
            self[key] = value

    code = request.args.get('code')

    array = oracle.execute_sql(
        'select ROWNUM, P.COD_PRODUCTO, P.COD_MOTOR, P.COD_CHASIS, P.CAMVCPN, P.ANIO, P.COD_COLOR, P.CILINDRAJE, P.TONELAJE, P.OCUPANTES, P.MODELO, P.CLASE, P.SUBCLASE, P.FECHA_ADICION, P.FECHA_MODIFICACION, V.COD_LIQUIDACION, V.NOMBRE '
        'from ST_PROD_PACKING_LIST P, VT_VALORACION_SERIE V where P.COD_MOTOR = V.NUMERO_SERIE AND P.COD_MOTOR = '+ "'"+code+"'")
    mydict = create_dict()
    for row in array:
        mydict.add(row[0],({"CODPRODUC":row[1],"CODMOTOR":row[2],"CODCHASIS":row[3], "CPN":row[4], "YEAR":row[5],"COLOR":row[6],"CILINDRAJE":row[7],"TONELAJE":row[8], "OCUPANTES":row[9], "MODELO":row[10],"CLASE":row[11], "SUBCLASE":row[12], "FECHA CREACION":row[13], "FECHA MODIFICACION":row[14], "CODIGO LIQUIDACION":row[15], "IMPORTACION":row[16]}))
    stud_json = json.dumps(mydict, indent=2, default=str)
    return stud_json

@app.route('/atelier', methods = ['GET'])
def atelier():
    class create_dict(dict):

        # __init__ function
        def __init__(self):
            self = dict()

            # Function to add key:value

        def add(self, key, value):
            self[key] = value

    code = request.args.get('code')

    array = oracle.execute_sql('select ROWNUM, P.DESCRIPCION, C.DESCRIPCION,T.DESCRIPCION, T.NOMBRE_CONTACTO, T.TELEFONO1, T.TELEFONO2, T.TELEFONO3, T.DIRECCION,T.FECHA_ADICION, T.FECHA_MODIFICACION from AR_TALLER_SERVICIO_TECNICO T , AR_PROVINCIAS P, ar_ciudades c WHERE T.CODIGO_EMPRESA = 20  and   T.CODIGO_PROVINCIA = P.CODIGO_PROVINCIA (+) and   c.codigo_ciudad(+)    = t.codigo_ciudad and   c.codigo_provincia(+) = t.codigo_provincia')
    mydict = create_dict()
    for row in array:
        mydict.add(row[0],({"PROVINCIA":row[1],"CIUDAD":row[2],"NOMBRE TALLER":row[3], "NOMBRE MECANICO":row[4], "NUMERO PRINCIPAL":row[5],"NUMERO ALTERNATIVO":row[6],"NUMERO CONVENCIONAL PRINCIPAL":row[7],"DIRECCION":row[8], "FECHA CREACION":row[9], "FECHA MODIFICACION":row[10]}))
    stud_json = json.dumps(mydict, indent=2, default=str)
    return stud_json


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        print(request.form['username'])
        print(request.form['password'])
        return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')

if __name__=='__main__':
    # app.config.from_object(config['development'])
    app.run(host='0.0.0.0',port=5000)

