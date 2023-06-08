import requests
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import datetime as dt

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf.csrf import CSRFProtect
from numpy.core.defchararray import upper
from requests.auth import HTTPBasicAuth

import oracle
from routes.web_services import web_services
from routes.auth import auth
from dotenv import load_dotenv, find_dotenv
from src.models.ModelUser import ModelUser
from src.models.entities.User import User
from flask_login import LoginManager, login_user,logout_user, login_required
from os import getenv
import dotenv
from flask_cors import CORS, cross_origin

import json
import os
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, unset_jwt_cookies, jwt_required, JWTManager

###################################################
from src.config.database import db
from src.routes.routes import bp
from src.routes.routes_custom import bpcustom
import logging
from sqlalchemy import create_engine
###################################################

dotenv.load_dotenv()

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "please-remember-me"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
app.config['CORS_HEADERS'] = 'Content-Type'
scheduler = BackgroundScheduler()
###################################################
os.environ["NLS_LANG"] = ".UTF8"
app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle+cx_oracle://stock:stock@192.168.51.73:1521/mlgye01?encoding=utf-8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

app.register_blueprint(bp)
app.register_blueprint(bpcustom)

#############################################################################

jwt = JWTManager(app)
CORS(app)
app.secret_key = getenv("SECRET_KEY")
login_manager = LoginManager(app)

app.register_blueprint(auth, url_prefix="/")
app.register_blueprint(web_services, url_prefix="/api")


@app.route('/token', methods=["POST"])
@cross_origin()
def create_token():
    user = request.json.get("user", None)
    password = request.json.get("password", None)

    try:
        db = oracle.connection('stock', 'stock')
        cursor = db.cursor()
        sql = """SELECT USUARIO_ORACLE, PASSWORD, NOMBRE FROM USUARIO 
                WHERE USUARIO_ORACLE = '{}'""".format(user.upper())
        cursor.execute(sql)
        db.close
        row = cursor.fetchone()
        if row != None:
            isCorrect = User.check_password(row[1],password)
            if isCorrect:
                access_token = create_access_token(identity=user)
                return {"access_token": access_token}
            else:
                return {"msg": "Wrong password"}, 401
        else:
            return {"msg": "Wrong username"}, 401
    except Exception as ex:
        raise Exception(ex)

@app.after_request
@cross_origin()
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response

@app.route('/profile')
@jwt_required()
@cross_origin()
def my_profile():
    response_body = {
        "name": "Damian",
        "about": "Hello! I'm a full stack developer that loves python and javascript"
    }
    return response_body

@app.route('/enterprise/<id>')
@jwt_required()
@cross_origin()
def enterprise(id):
    aux = "N"
    try:
        c = oracle.connection('stock', 'stock')
        cur_01 = c.cursor()
        id = str(upper(id))
        print(id)
        sql = ('SELECT DISTINCT E.EMPRESA, E.NOMBRE FROM EMPRESA E, USUARIO_EMPRESA UE, USUARIO U '
               'WHERE E.EMPRESA = UE.EMPRESA AND UE.USERIDC = U.USERIDC '
               'AND U.USUARIO_ORACLE =  (CASE WHEN (SELECT U2.TODA_EMPRESA FROM USUARIO U2 WHERE U2.USUARIO_ORACLE = :id) = :aux THEN :id ELSE U.USUARIO_ORACLE END)')
        cursor = cur_01.execute(sql, [id, aux])
        c.close
        row_headers = [x[0] for x in cursor.description]
        array = cursor.fetchall()
        empresas = []
        for result in array:
            empresas.append(dict(zip(row_headers, result)))
        empresas_ordenadas = sorted(empresas, key=lambda k: k['NOMBRE'])
        return json.dumps(empresas_ordenadas)
    except Exception as ex:
        raise Exception(ex)
    return response_body


@app.route('/branch/<id>/<en>')
@jwt_required()
@cross_origin()
def branch(id,en):
    try:
        c = oracle.connection('stock', 'stock')
        cur_01 = c.cursor()
        id = str(upper(id))

        sql = ('SELECT DISTINCT A.COD_AGENCIA, A.NOMBRE FROM TG_AGENCIA A, TG_USUARIO_X_AGENCIA B '
               'WHERE A.EMPRESA=B.EMPRESA AND B.EMPRESA = :en '
               'AND A.COD_AGENCIA = (CASE WHEN (SELECT UE.TODA_AGENCIA FROM USUARIO_EMPRESA UE WHERE UE.EMPRESA = :en AND UE.USERIDC = :id ) = :a THEN B.COD_AGENCIA ELSE A.COD_AGENCIA END) '
               'AND B.USERIDC= (CASE WHEN (SELECT UE.TODA_AGENCIA FROM USUARIO_EMPRESA UE WHERE UE.EMPRESA = :en AND UE.USERIDC = :id ) = :a THEN :id ELSE B.USERIDC END) ')
        cursor = cur_01.execute(sql, id=id, en=en, a='N')
        c.close
        row_headers = [x[0] for x in cursor.description]
        array = cursor.fetchall()
        agencias = []
        for result in array:
            agencias.append(dict(zip(row_headers, result)))
        agencias_ordenadas = sorted(agencias, key=lambda k: k['NOMBRE'])
        return json.dumps(agencias_ordenadas)
    except Exception as ex:
        raise Exception(ex)
    return response_body


@app.route("/logout",methods=["POST"])
@cross_origin()
def logout():
    response = jsonify({"msg": "logout succesfull"})
    unset_jwt_cookies(response)
    return response


# @login_manager.user_loader
# def load_user(username):
#     return ModelUser.get_by_id(username)

# @app.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('login'))

# def status_401(error):
#     return redirect(url_for('login'))
# def status_404(error):
#     return "<h1>Página no encontrada</h1>", 404


# @app.route('/')
# def index():
#     return redirect(url_for('login'))


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         data = request.get_json()
#         usuario = data['username'].upper()
#         password = data['password']
#         print(usuario,password)
#         user = User(usuario,password)
#         logged_user=ModelUser.login(user)
#         if logged_user != None:
#             if logged_user.password:
#                 login_user(logged_user)
#                 return jsonify({'msg': 'User Logged'})                    #redirect(url_for('home'))
#             else:
#                 #flash("Invalid password...")
#                 return jsonify({'msg': 'Invalid password...'})                           #render_template('auth/login.html')
#         else:
#             #flash("User not found...")
#             return jsonify({'msg': 'User not found...'})                                                     #render_template('auth/login.html')
#     else:
#         return render_template('auth/login.html')
#

# @app.route('/home')
# @login_required
# def home():
#     return render_template('home.html')


########################################################################

@app.route("/user/<id>", methods=['GET'])
@jwt_required()
def getUser(id):
    c = oracle.connection('stock', 'stock')
    cur_01 = c.cursor()
    sql = ('SELECT * FROM usuario WHERE USUARIO_ORACLE = :id')
    cursor = cur_01.execute(sql,[id])
    c.close
    row_headers = [x[0] for x in cursor.description]
    print(row_headers)
    array = cursor.fetchall()

    usuario = []
    for result in array:
        usuario.append(dict(zip(row_headers, result)))
    return json.dumps(usuario[0])
    cur_01.execute(sql,[id])
    c.commit()
    cur_01.close()
    c.close()
    return jsonify({'msg': 'User updated'})


@app.route("/users", methods=['GET', 'POST'])
@jwt_required()
def users():
    if request.method == 'POST':
        data = request.get_json()
        usuario = data['username'].upper()
        password = data['password']
        email = data['email']
        id = usuario[0:3]
        empresa_actual = 20
        agencia_actual = 30

        c = oracle.connection('stock', 'stock')
        cur_01 = c.cursor()
        sql = (
                'insert into usuario(USERIDC,USUARIO_ORACLE, E_MAIL, PASSWORD, EMPRESA_ACTUAL, AGENCIA_ACTUAL) '
                'values(:id,:usuario,:email,:password, :empresa_actual, :agencia_actual)')

        cur_01.execute(sql, [id, usuario, email, password, empresa_actual,agencia_actual])
        c.commit()
        c.close
        return jsonify('received')
    else:
        c = oracle.connection('stock', 'stock')
        cur_01 = c.cursor()
        sql = ('select ROWNUM, USUARIO_ORACLE, APELLIDO1, APELLIDO2, NOMBRE from usuario where rownum <= 10')
        cursor = cur_01.execute(sql)
        row_headers = [x[0] for x in cursor.description]
        array = cursor.fetchall()
        c.close
        usuario = []
        for result in array:
            usuario.append(dict(zip(row_headers, result)))
        return json.dumps(usuario)

@app.route("/users/<id>", methods=['DELETE'])
@jwt_required()
def deleteUser(id):
    c = oracle.connection('stock', 'stock')
    cur_01 = c.cursor()
    sql = ('delete from usuario where USUARIO_ORACLE = :id')
    cur_01.execute(sql,[id])
    c.commit()
    cur_01.close()
    c.close()
    return jsonify({'msg': 'User deleted'})

@app.route("/users/<id>", methods=['PUT'])
@jwt_required()
def updateUser(id):
    usuario_oracle = str(upper(request.json['username']))
    email = request.json['email']
    password = request.json['password']
    print(id,usuario_oracle,email,password)
    c = oracle.connection('stock', 'stock')
    cur_01 = c.cursor()
    sql = ('UPDATE usuario SET USUARIO_ORACLE = :usuario_oracle, E_MAIL = :email, PASSWORD = :password where USUARIO_ORACLE = :id')
    cur_01.execute(sql,[usuario_oracle,email,password, id])
    c.commit()
    cur_01.close()
    c.close()
    return jsonify({'msg': 'User updated'})

##########################################################################################################################################################

def consume_api_mantenimiento_auto():
    # Make a request to the API.
    today = dt.date.today()
    yesterday = today - dt.timedelta(days=1)
    yesterday = yesterday.strftime("%Y-%m-%d")
    response = requests.get(
        "https://api.jelou.ai/v1/company/405/reports/145/rows?startAt=" + yesterday + "T00:00:01.007-05:00&endAt=" + yesterday + "T23:59:59.007-05:00&limit=500&page=1",
        auth=HTTPBasicAuth(getenv("API_USER"), getenv("API_PASS")))
    data = response.json()
    rows = data['rows']
    c = oracle.connection('stock', 'stock')
    cursor = c.cursor()

    for row in rows:
        codigo_taller = int(row["codigoTaller"])
        mantenimiento_prox = int(row["mantenimientoProx"])
        nombre_mantenimiento = row["nombreMantenimiento"]
        nombre_garantia = row["nombreGarantia"]
        nombre_taller = row.get("nombreTaller", " ")
        telefono_garantia = row.get("telefonoGarantia", None)
        chasis = row["chasis"]
        mantenimiento_actual = int(row["mantenimientoActual"])
        placa = row["placa"]
        legal_id = row["legalId"]
        created_at = row["createdAt"]
        updated_at = row["updatedAt"]
        empresa = '20'

        query = "INSERT INTO ST_WS_MANTENIMIENTOS (codigo_taller, mantenimiento_prox, nombre_mantenimiento, nombre_garantia, chasis, mantenimiento_actual, placa, legal_id, fecha_crea, fecha_mod, empresa, nombre_taller, telefono_garantia) VALUES (:codigo_taller, :mantenimiento_prox, :nombre_mantenimiento, :nombre_garantia, :chasis, :mantenimiento_actual, :placa, :legal_id, TO_DATE(:created_at, 'DD/MM/YYYY HH24:MI'), TO_DATE(:updated_at, 'DD/MM/YYYY HH24:MI'), :empresa, :nombre_taller, :telefono_garantia)"

        try:
            cursor.execute(query, {
            "codigo_taller": codigo_taller,
            "mantenimiento_prox": mantenimiento_prox,
            "nombre_mantenimiento": nombre_mantenimiento.upper(),
            "nombre_garantia": nombre_garantia.upper(),
            "chasis": chasis.upper(),
            "mantenimiento_actual": mantenimiento_actual,
            "placa": placa.upper(),
            "legal_id": legal_id.upper(),
            "created_at": created_at,
            "updated_at": updated_at,
            "empresa": empresa,
            "nombre_taller": nombre_taller.upper(),
            "telefono_garantia": telefono_garantia
        })
            c.commit()

        except c.Error as error:
            print("Error inserting row ", codigo_taller, " ", created_at, " :",error)
    c.close()
    return jsonify({'msg': 'Test'})

def consume_api_repuestos_auto():

    today = dt.date.today()
    yesterday = today - dt.timedelta(days=1)
    yesterday = yesterday.strftime("%Y-%m-%d")
    response = requests.get("https://api.jelou.ai/v1/company/405/reports/137/rows?startAt="+yesterday+"T00:00:01.007-05:00&endAt="+yesterday+"T23:59:59.007-05:00&limit=500&page=1",
                            auth=HTTPBasicAuth(getenv("API_USER"),getenv("API_PASS")))
    data = response.json()
    rows = data['rows']
    c = oracle.connection('stock', 'stock')
    cursor = c.cursor()

    for row in rows:
        user_id = int(row["userId"])
        full_name = row["fullName"]
        city = row["city"]
        phone = row["phone"]
        trademark = row.get("trademark", " ")
        model = row.get("model", None)
        color = row.get("color", None)
        detail = row.get("detail", None)
        status = row.get("status", " ")
        observation = row.get("observation", " ")
        fecha_crea = row["createdAt"]
        fecha_mod = row["updatedAt"]
        empresa = '20'

        query = "INSERT INTO ST_WS_REPUESTOS (user_id, full_name, city, phone, trademark, model, color, detail, status, observation, fecha_crea, fecha_mod, empresa ) VALUES (:user_id, :full_name, :city, :phone, :trademark, :model, :color, :detail, :status, :observation, TO_DATE(:fecha_crea, 'DD/MM/YYYY HH24:MI'), TO_DATE(:fecha_mod, 'DD/MM/YYYY HH24:MI'), :empresa)"

        try:
            cursor.execute(query, {
            "user_id": user_id,
            "full_name": full_name.upper(),
            "city": city.upper(),
            "phone": phone,
            "trademark": trademark.upper(),
            "model": model.upper(),
            "color": color.upper(),
            "detail": detail.upper(),
            "status": status.upper(),
            "observation": observation.upper(),
            "fecha_crea": fecha_crea,
            "fecha_mod": fecha_mod,
            "empresa": empresa,
        })
            c.commit()

        except c.Error as error:
            print("Error inserting row ", user_id, " ", fecha_crea, " :",error)
    c.close()
    return jsonify({'msg': 'Test'})

####################################################################################

scheduler.add_job(func=consume_api_repuestos_auto, trigger="cron", hour="16", minute="0")
scheduler.add_job(func=consume_api_mantenimiento_auto, trigger="cron", hour="16", minute="1")

scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    load_dotenv(find_dotenv())
    #csrf.init_app(app)
    # app.register_error_handler(401, status_401)
    # app.register_error_handler(404, status_404)
    app.run(host='0.0.0.0', port=5000)

