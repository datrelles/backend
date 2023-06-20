from flask import Blueprint, request, jsonify
from src.function_jwt import validate_token
from src import oracle
import json


web_services = Blueprint("web_services", __name__)


@web_services.before_request
def verify_token_middleware():
    token = request.headers['Authorization'].split(" ")[1]
    return validate_token(token,output=False)


@web_services.route("/atelier", methods=["POST"])
def atelier():

        class create_dict(dict):

            # __init__ function
            def __init__(self):
                self = dict()

                # Function to add key:value

            def add(self, key, value):
                self[key] = value

        token = request.headers['Authorization'].split(" ")[1]
        info = validate_token(token, output=True)
        user = info['username']
        password = info['password']
        array = oracle.execute_sql(
            'select ROWNUM, P.DESCRIPCION, C.DESCRIPCION,T.DESCRIPCION, T.NOMBRE_CONTACTO, T.TELEFONO1, T.TELEFONO2, T.TELEFONO3, T.DIRECCION, T.RUC,T.FECHA_ADICION, T.FECHA_MODIFICACION, T.FECHA_NACIMIENTO from AR_TALLER_SERVICIO_TECNICO T , AR_PROVINCIAS P, ar_ciudades c WHERE T.CODIGO_EMPRESA = 20  and   T.CODIGO_PROVINCIA = P.CODIGO_PROVINCIA (+) and   c.codigo_ciudad(+)    = t.codigo_ciudad and   c.codigo_provincia(+) = t.codigo_provincia',user,password)
        mydict = create_dict()
        for row in array:
            mydict.add(row[0], (
            {"PROVINCIA": row[1], "CIUDAD": row[2], "NOMBRE TALLER": row[3], "NOMBRE MECANICO": row[4],
             "NUMERO PRINCIPAL": row[5], "NUMERO ALTERNATIVO": row[6], "NUMERO CONVENCIONAL PRINCIPAL": row[7],
             "DIRECCION": row[8], "RUC": row[9], "FECHA CREACION": row[10], "FECHA MODIFICACION": row[11], "FECHA NACIMIENTO": row[12]}))
        stud_json = json.dumps(mydict, indent=2, default=str, ensure_ascii=False).encode('utf8')
        return stud_json


@web_services.route('/api-packing-list-by-code', methods = ['GET'])
def byCode():
    class create_dict(dict):

        # __init__ function
        def __init__(self):
            self = dict()

            # Function to add key:value

        def add(self, key, value):
            self[key] = value

    code = request.args.get('code')
    token = request.headers['Authorization'].split(" ")[1]
    info = validate_token(token, output=True)
    user = info['username']
    password = info['password']
    array = oracle.execute_sql(
        'select ROWNUM, P.COD_PRODUCTO, P.COD_MOTOR, P.COD_CHASIS, P.CAMVCPN, P.ANIO, P.COD_COLOR, P.CILINDRAJE, P.TONELAJE, P.OCUPANTES, P.MODELO, P.CLASE, P.SUBCLASE, P.FECHA_ADICION, P.FECHA_MODIFICACION, V.COD_LIQUIDACION, V.NOMBRE from ST_PROD_PACKING_LIST P, VT_VALORACION_SERIE V where p.empresa = 20 and p.cod_producto = v.COD_PRODUCTO(+) AND p.empresa = v.empresa(+) and p.cod_chasis = v.NUMERO_SERIE(+) and P.COD_MOTOR = '+ "'"+code+"'",user,password)
    mydict = create_dict()
    for row in array:
        mydict.add(row[0],({"CODPRODUC":row[1],"CODMOTOR":row[2],"CODCHASIS":row[3], "CPN":row[4], "YEAR":row[5],"COLOR":row[6],"CILINDRAJE":row[7],"TONELAJE":row[8], "OCUPANTES":row[9], "MODELO":row[10],"CLASE":row[11], "SUBCLASE":row[12], "FECHA CREACION":row[13], "FECHA MODIFICACION":row[14], "CODIGO LIQUIDACION":row[15], "IMPORTACION":row[16]}))
    stud_json = json.dumps(mydict, indent=2, default=str, ensure_ascii=False).encode('utf8')
    return stud_json


@web_services.route('/api-packing-list', methods = ['GET'])
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
    token = request.headers['Authorization'].split(" ")[1]
    info = validate_token(token, output=True)
    user = info['username']
    password = info['password']
    array = oracle.execute_sql(
        'select ROWNUM, P.COD_PRODUCTO, P.COD_MOTOR, P.COD_CHASIS, P.CAMVCPN, P.ANIO, P.COD_COLOR, P.CILINDRAJE, P.TONELAJE, P.OCUPANTES, P.MODELO, P.CLASE, P.SUBCLASE, P.FECHA_ADICION, P.FECHA_MODIFICACION, V.COD_LIQUIDACION, V.NOMBRE from ST_PROD_PACKING_LIST P, VT_VALORACION_SERIE V where p.empresa = 20 and p.cod_producto = v.COD_PRODUCTO(+) AND p.empresa = v.empresa(+) and   p.cod_chasis = v.NUMERO_SERIE(+) and P.anio = '+year,user,password)
    mydict = create_dict()
    for row in array:
        mydict.add(row[0],({"CODPRODUC":row[1],"CODMOTOR":row[2],"CODCHASIS":row[3], "CPN":row[4], "YEAR":row[5],"COLOR":row[6],"CILINDRAJE":row[7],"TONELAJE":row[8], "OCUPANTES":row[9], "MODELO":row[10],"CLASE":row[11], "SUBCLASE":row[12], "FECHA CREACION":row[13], "FECHA MODIFICACION":row[14], "CODIGO LIQUIDACION":row[15], "IMPORTACION":row[16]}))
    stud_json = json.dumps(mydict, indent=2, default=str, ensure_ascii=False).encode('utf8')
    return stud_json



