from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import datetime

datetime_format = '%d%m%y'

app = Flask(__name__)
os.environ["NLS_LANG"] = ".UTF8"
app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle+cx_oracle://stock:stock@192.168.51.73:1521/mlgye01?encoding=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DATETIME_FORMAT'] = datetime_format

db = SQLAlchemy(app)

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

Session = sessionmaker(bind=engine)
session = Session()