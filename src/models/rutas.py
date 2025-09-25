# coding: utf-8
from sqlalchemy import Column, DateTime, Index, VARCHAR, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy import Sequence
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db
from marshmallow import Schema, fields, validate, EXCLUDE, ValidationError


Base = declarative_base(metadata = db.metadata)

class STRuta(db.Model):
    __tablename__ = "ST_RUTAS"

    cod_ruta = db.Column(
        "COD_RUTA",
        db.Integer,
        Sequence("SEQ_ST_RUTAS"),
        primary_key=True,
        autoincrement=True
    )
    empresa = db.Column("EMPRESA", db.Integer, primary_key=True)

    id = db.Column("ID", db.String(20))
    nombre = db.Column("NOMBRE", db.String(200))
    @staticmethod
    def identity_key(cod_ruta: int, empresa: int):
        return (cod_ruta, empresa)

class RutaOutSchema(Schema):
    cod_ruta = fields.Integer()
    empresa = fields.Integer()
    id = fields.String(allow_none=True)
    nombre = fields.String(allow_none=True)

class RutaCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    empresa = fields.Integer(required=True)
    nombre = fields.String(required=False, allow_none=True, validate=validate.Length(max=200))

class RutaUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    empresa = fields.Integer()
    cod_ruta = fields.Integer()

    nombre = fields.String(required=False, allow_none=True, validate=validate.Length(max=200))

class STDireccionRuta(db.Model):
    __tablename__ = "ST_DIRECCION_RUTAS"
    empresa = db.Column("EMPRESA", db.Integer, primary_key=True)
    cod_cliente = db.Column("COD_CLIENTE", db.String(14), primary_key=True)
    cod_direccion = db.Column("COD_DIRECCION", db.Integer, primary_key=True)
    cod_ruta = db.Column("COD_RUTA", db.Integer, primary_key=True)

class DirRutaOutSchema(Schema):
    empresa = fields.Integer()
    cod_cliente = fields.String()
    cod_direccion = fields.Integer()
    cod_ruta = fields.Integer()

class DirRutaCreateSchema(Schema):
    class Meta: unknown = EXCLUDE
    empresa = fields.Integer(required=True)
    cod_cliente = fields.String(required=True, validate=validate.Length(max=14))
    cod_direccion = fields.Integer(required=True)
    cod_ruta = fields.Integer(required=True)

class DirRutaDetailSchema(Schema):
    class Meta: unknown = EXCLUDE
    empresa = fields.Integer(required=True)
    cod_cliente = fields.String(required=True, validate=validate.Length(max=14))
    cod_direccion = fields.Integer(required=True)
    cod_ruta = fields.Integer(required=True)

class DirRutaSearchSchema(Schema):
    class Meta: unknown = EXCLUDE
    empresa = fields.Integer()
    cod_cliente = fields.String(validate=validate.Length(max=14))
    cod_ruta = fields.Integer()
    page = fields.Integer(load_default=1)
    page_size = fields.Integer(load_default=20)

class DirRutaDeleteSchema(DirRutaDetailSchema):
    pass

class STTransportistaRuta(db.Model):
    __tablename__ = "ST_TRANSPORTISTA_RUTA"

    codigo = db.Column(
        "CODIGO",
        db.Integer,
        Sequence("SEQ_ST_TRANSPORTISTA_RUTA"),
        primary_key=True,
        autoincrement=True
    )
    empresa = db.Column("EMPRESA", db.Integer, primary_key=True)
    cod_transportista = db.Column("COD_TRANSPORTISTA", db.String(14))
    cod_ruta = db.Column("COD_RUTA", db.Integer)

class TRutaOutSchema(Schema):
    codigo = fields.Integer()
    empresa = fields.Integer()
    cod_transportista = fields.String(allow_none=True)
    cod_ruta = fields.Integer(allow_none=True)

class TRutaCreateSchema(Schema):
    class Meta: unknown = EXCLUDE
    empresa = fields.Integer(required=True)
    cod_transportista = fields.String(required=True, validate=validate.Length(max=14))
    cod_ruta = fields.Integer(required=True)

class TRutaDetailSchema(Schema):
    class Meta: unknown = EXCLUDE
    empresa = fields.Integer(required=True)
    codigo = fields.Integer(required=True)

class TRutaUpdateSchema(Schema):
    class Meta: unknown = EXCLUDE
    empresa = fields.Integer(required=True)
    codigo = fields.Integer(required=True)
    cod_transportista = fields.String(validate=validate.Length(max=14))
    cod_ruta = fields.Integer()

class TRutaSearchSchema(Schema):
    class Meta: unknown = EXCLUDE
    empresa = fields.Integer()
    cod_transportista = fields.String(validate=validate.Length(max=14))
    cod_ruta = fields.Integer()
    page = fields.Integer(load_default=1)
    page_size = fields.Integer(load_default=20)

class TRutaDeleteSchema(TRutaDetailSchema):
    pass