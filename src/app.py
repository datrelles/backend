from flask import Flask, render_template, request, redirect, url_for, jsonify
from config import config
from src import oracle

app=Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/my-first-api', methods = ['GET'])
def hello():

    name = request.args.get('name')
    return jsonify({
        # "message": "PackingList Data",
        "Packing List data": oracle.execute_sql('select COD_PRODUCTO, COD_MOTOR, COD_CHASIS, CAMVCPN, ANIO, COD_COLOR, CILINDRAJE, TONELAJE, OCUPANTES, MODELO, CLASE, SUBCLASE, FECHA_ADICION, FECHA_MODIFICACION from ST_PROD_PACKING_LIST where rownum<1000')
        })

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        print(request.form['username'])
        print(request.form['password'])
        return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')

if __name__=='__main__':
    app.config.from_object(config['development'])
    app.run()