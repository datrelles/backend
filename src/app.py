from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from src.routes.web_services import web_services
from src.routes.auth import auth
from dotenv import load_dotenv, find_dotenv
from models.ModelUser import ModelUser
from models.entities.User import User
from flask_login import LoginManager, login_user,logout_user, login_required
from os import getenv
import dotenv

dotenv.load_dotenv()

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
login_manager = LoginManager(app)
csrf = CSRFProtect()

app.register_blueprint(auth, url_prefix="/")
app.register_blueprint(web_services, url_prefix="/api")

@login_manager.user_loader
def load_user(username):
    return ModelUser.get_by_id(username)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

def status_401(error):
    return redirect(url_for('login'))
def status_404(error):
    return "<h1>Página no encontrada</h1>", 404


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User(request.form['username'],request.form['password'])
        logged_user=ModelUser.login(user)
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('home'))
            else:
                flash("Invalid password...")
                return render_template('auth/login.html')
        else:
            flash("User not found...")
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')
@app.route('/home')
@login_required
def home():
    return render_template('home.html')

if __name__ == '__main__':
    load_dotenv(find_dotenv())
    csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(host='0.0.0.0', port=5000)

