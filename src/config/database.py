from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import datetime

datetime_format = '%d%m%y'

app = Flask(__name__)
os.environ["NLS_LANG"] = ".UTF8"
app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle+cx_oracle://stock:stock@192.168.51.73:1521/mlgye01?encoding=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DATETIME_FORMAT'] = datetime_format

db = SQLAlchemy(app)