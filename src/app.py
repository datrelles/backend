from flask import Flask, render_template, request, redirect, url_for, jsonify
from src.routes.web_services import web_services
from src.routes.auth import auth
from dotenv import load_dotenv


app = Flask(__name__)
app.register_blueprint(auth, url_prefix="/")
app.register_blueprint(web_services, url_prefix="/api")


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print(request.form['username'])
        print(request.form['password'])
        return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')


if __name__ == '__main__':
    # app.config.from_object(config['development'])
    load_dotenv()
    app.run(host='0.0.0.0', port=5000)

