from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify
from numpy.core.defchararray import upper
from flask_mail import Mail, Message

import oracle
from routes.web_services import web_services
from routes.auth import auth
from dotenv import load_dotenv, find_dotenv
from src.models.entities.User import User
from flask_login import LoginManager
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
from src.routes.routes_auth import au
from src.routes.routes_custom import bpcustom
from src.routes.routes_fin import bpfin
from src.routes.routes_logis import bplog
from src.routes.routes_com import bpcom
from src.routes.module_contabilidad import rmc
from src.routes.warranty_module import rmwa
from src.routes.email_alert import aem, execute_send_alert_emails, execute_send_alert_emails_for_role

###################################################

dotenv.load_dotenv()

app = Flask(__name__)

#####################mail################################

app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'facturacion@massline.com.ec'
app.config['MAIL_PASSWORD'] = 'lpnkxmlgmdsshlmz'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = 'facturacion@massline.com.ec'
mail = Mail(app)
###################################################

app.config["JWT_SECRET_KEY"] = "please-remember-me"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['CORS_HEADERS'] = 'Content-Type'
scheduler = BackgroundScheduler()

os.environ["NLS_LANG"] = ".UTF8"

# Configuración de la base de datos
db_username = getenv("USERORA")
db_password = getenv("PASSWORD")
db_host = getenv("IP")
db_port = getenv("PORT")
db_sid = getenv("SID")
db_uri = f"oracle+cx_oracle://{db_username}:{db_password}@{db_host}:{db_port}/{db_sid}?encoding=utf-8"
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

app.register_blueprint(bp)
app.register_blueprint(bpcustom)
app.register_blueprint(au, url_prefix="/auth")
app.register_blueprint(bpfin, url_prefix="/fin")
app.register_blueprint(bplog, url_prefix="/log")
app.register_blueprint(bpcom, url_prefix="/com")
app.register_blueprint(aem, url_prefix="/alert_email")
app.register_blueprint(rmc, url_prefix="/cont")
app.register_blueprint(rmwa, url_prefix="/warranty")

#############################################################################

jwt = JWTManager(app)
CORS(app, resources={
    r"/*": {
        "origins": "*",  # Allows all origins
        "allow_headers": ["Content-Type", "Authorization"],  # Specify allowed headers
        "supports_credentials": True  # Optional, for cookies and authorization headers
    }
})
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
        db = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
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

@app.route('/enterprise/<id>')
@jwt_required()
@cross_origin()
def enterprise(id):
    aux = "N"
    try:
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
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
        return jsonify(empresas_ordenadas)
    except Exception as ex:
        raise Exception(ex)
    return jsonify(response_body)


@app.route('/enterprise_default/<id>')
@jwt_required()
@cross_origin()
def enterprise_default(id):
    try:
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur_01 = c.cursor()
        id = str(upper(id))
        sql = ('select u.empresa_actual, u.agencia_actual from usuario u where u.usuario_oracle = :id')
        cursor = cur_01.execute(sql, [id])
        c.close
        row_headers = [x[0] for x in cursor.description]
        array = cursor.fetchall()
        empresas = []
        for result in array:
            empresas.append(dict(zip(row_headers, result)))
        return jsonify(empresas)
    except Exception as ex:
        raise Exception(ex)
    return jsonify(response_body)


@app.route('/branch/<id>/<en>')
@jwt_required()
@cross_origin()
def branch(id,en):
    try:
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
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
        return jsonify(agencias_ordenadas)
    except Exception as ex:
        raise Exception(ex)
    return jsonify(response_body)
@app.route('/modules/<user>/<enterprise>')
@jwt_required()
@cross_origin()
def module(user,enterprise):
    try:
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur_01 = c.cursor()
        user = str(upper(user))
        sql = ('SELECT DISTINCT F.COD_SISTEMA, F.SISTEMA, F.PATH_IMAGEN, F.RUTA '
                'FROM computo.usuario  a, computo.TG_ROL_USUARIO B, computo.TG_ROL C, computo.TG_MENU_SISTEMA_ROL D, computo.TG_MENU_SISTEMA E, computo.TG_SISTEMA F '
                'WHERE a.usuario_oracle        =         :id '
                'AND   A.EMPRESA_ACTUAL        =         :en '
                'AND   B.EMPRESA               =         A.EMPRESA_ACTUAL '
                'AND   B.USUARIO               =         A.USUARIO_ORACLE '
                'AND   B.ACTIVO                =         1 '
                'AND   C.EMPRESA               =         B.EMPRESA '
                'AND   C.COD_ROL               =         B.COD_ROL '
                'AND   C.ACTIVO                =         1 '
                'AND   D.COD_ROL               =         B.COD_ROL '
                'AND   D.COD_SISTEMA           =         E.COD_SISTEMA '
                'AND   D.COD_MENU              =         E.COD_MENU_PADRE '
                'AND   D.EMPRESA               =         B.EMPRESA '
                'AND   D.EMPRESA               =         E.EMPRESA '
                'AND   D.ACTIVO                =         1 '
                'AND   F.COD_SISTEMA           =         E.COD_SISTEMA')
        cursor = cur_01.execute(sql, id=user, en=enterprise)
        c.close
        row_headers = [x[0] for x in cursor.description]
        array = cursor.fetchall()
        modulos = []
        for result in array:
            modulos.append(dict(zip(row_headers, result)))
        modulos = sorted(modulos, key=lambda k: k['SISTEMA'])
        return jsonify(modulos)
    except Exception as ex:
        raise Exception(ex)
    return jsonify(response_body)

@app.route('/menus/<user>/<enterprise>/<system>')
@jwt_required()
@cross_origin()
def menu(user,enterprise, system):
    try:
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur_01 = c.cursor()
        user = str(upper(user))
        sql = ('SELECT E.COD_MENU, E.COD_MENU_PADRE, E.NOMBRE, E.RUTA '
                    'FROM computo.usuario  a, computo.TG_ROL_USUARIO B,  computo.TG_ROL C, ' 
                    'computo.TG_MENU_SISTEMA_ROL D, computo.TG_MENU_SISTEMA E, computo.TG_SISTEMA F '
                    'WHERE a.usuario_oracle        =         :id '
                    'AND   A.EMPRESA_ACTUAL        =         :en '
                    'AND   B.EMPRESA               =         A.EMPRESA_ACTUAL '
                    'AND   B.USUARIO               =         A.USUARIO_ORACLE '
                    'AND   B.ACTIVO                =         1 '
                    'AND   C.EMPRESA               =         B.EMPRESA '
                    'AND   C.COD_ROL               =         B.COD_ROL '
                    'AND   C.ACTIVO                =         1 '
                    'AND   D.COD_ROL               =         B.COD_ROL '
                    'AND   D.COD_SISTEMA           =         E.COD_SISTEMA '
                    'AND   D.EMPRESA               =         B.EMPRESA '
                    'AND   D.EMPRESA               =         E.EMPRESA '
                    'AND   D.COD_MENU              =         E.COD_MENU '
                    'AND   D.ACTIVO                =         1 '
                    'AND   F.COD_SISTEMA           =         E.COD_SISTEMA '
                    'AND   F.COD_SISTEMA           =         :sys')
        cursor = cur_01.execute(sql, id=user, en=enterprise, sys=system)
        c.close
        row_headers = [x[0] for x in cursor.description]
        array = cursor.fetchall()
        menus = []
        for result in array:
            menus.append(dict(zip(row_headers, result)))
        result = {}
        for item in menus:
            if item["COD_MENU_PADRE"] is None:
                result[item["COD_MENU"]] = {
                    "title": item["NOMBRE"],
                    "items": []
                }
        for item in menus:
            if item["COD_MENU_PADRE"] is not None:
                result[item["COD_MENU_PADRE"]]["items"].append({
                    "COD_MENU": item["COD_MENU"],
                    "NOMBRE": item["NOMBRE"],
                    "RUTA": item["RUTA"]
                })

        return jsonify(list(result.values()))

    except Exception as ex:
        raise Exception(ex)
    return jsonify(response_body)

@app.route("/logout",methods=["POST"])
@cross_origin()
def logout():
    response = jsonify({"msg": "logout succesfull"})
    unset_jwt_cookies(response)
    return response


def scheduled_task():
    with app.app_context():
        execute_send_alert_emails_for_role()

scheduler.add_job(scheduled_task, 'interval', minutes=30)
scheduler.start()

if __name__ == '__main__':
    load_dotenv(find_dotenv())
    app.run(host='0.0.0.0', port=5000, debug = True)