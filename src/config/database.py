from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import datetime
from os import getenv
import dotenv

datetime_format = '%d%m%y'

app = Flask(__name__)
# Configuración de la base de datos
db_username = getenv("USERORA")
db_password = getenv("PASSWORD")
db_host = getenv("IP")
db_port = getenv("PORT")
db_sid = getenv("SID")

db_uri = f"oracle+cx_oracle://{db_username}:{db_password}@{db_host}:{db_port}/{db_sid}?encoding=utf-8"
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DATETIME_FORMAT'] = datetime_format

db = SQLAlchemy(app)

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

Session = sessionmaker(bind=engine)
session = Session()