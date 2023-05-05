# coding: utf-8
from sqlalchemy import Column, DateTime, Index, VARCHAR, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship,deferred
from src.config.database import db

Base = declarative_base(metadata = db.metadata)

class TgModelo(Base):
    __tablename__ = 'tg_modelo'
    __table_args__ = (
        Index('modelo$att_din', 'empresa', 'cod_usuario_valores', 'cod_tabla_valores', 'valor_columna'),
        {'schema': 'computo'}
    )

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_modelo = Column(VARCHAR(8), primary_key=True, nullable=False)
    nombre = Column(VARCHAR(30), nullable=False)
    tabla_fuente = Column(VARCHAR(30))
    tabla_relacion = Column(VARCHAR(30))
    observaciones = Column(VARCHAR(2000))
    tipo = Column(VARCHAR(1))
    cod_usuario_enlace = Column(VARCHAR(30))
    cod_tabla_enlace = Column(VARCHAR(30))
    cod_columna_codigo = Column(VARCHAR(255))
    cod_columna_nombre = Column(VARCHAR(255))
    condiciones = Column(VARCHAR(2000))
    cod_usuario_valores = Column(VARCHAR(30))
    cod_tabla_valores = Column(VARCHAR(30))
    cod_columna_valores = Column(VARCHAR(255))
    basado_tabla = Column(VARCHAR(1))
    valor_columna = Column(VARCHAR(30))

    @classmethod
    def query(cls):
        return db.session.query(cls)


class TgModeloItem(Base):
    __tablename__ = 'tg_modelo_item'
    __table_args__ = {'schema': 'computo'}

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_modelo = Column(VARCHAR(8), primary_key=True, nullable=False)
    cod_item = Column(VARCHAR(3), primary_key=True, nullable=False)
    nombre = Column(VARCHAR(50), nullable=False)
    observaciones = Column(VARCHAR(2000))
    tipo = Column(VARCHAR(1))
    orden = Column(NUMBER(2, 0, False))
    
    @classmethod
    def query(cls):
        return db.session.query(cls)


class Proveedor(Base):
    __tablename__ = 'proveedor'

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_proveedor = Column(VARCHAR(14), primary_key=True, nullable=False)
    nombre = Column(VARCHAR(100), nullable=False)
    direccion = Column(VARCHAR(200))
    pais_telefono = Column(VARCHAR(3))
    telefono = Column(VARCHAR(10))
    telefono1 = Column(VARCHAR(10))
    fax = Column(VARCHAR(10))
    e_mail = Column(VARCHAR(50))
    casilla = Column(VARCHAR(10))
    ruc = Column(VARCHAR(13))
    useridc = Column(VARCHAR(3), nullable=False)
    contacto = Column(VARCHAR(50))
    cargo = Column(VARCHAR(30))
    activo = Column(VARCHAR(1))
    direccion_numero = Column(VARCHAR(10))
    interseccion = Column(VARCHAR(50))
    autorizacion_imprenta = Column(VARCHAR(10))
    cod_modelo = Column(VARCHAR(8))
    cod_item = Column(VARCHAR(3))
    tipo_bodega = Column(NUMBER(1, 0, False), nullable=False, server_default=text("3 "))

    #empresa = deferred(relationship(Empresa, backref = 'Proveedor'))
    #tg_modelo_item = deferred(relationship(TgModeloItem, backref = 'TgModeloItem')) 

    @classmethod
    def query(cls):
        return db.session.query(cls)
