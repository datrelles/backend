# coding: utf-8
from sqlalchemy import Column, Index, VARCHAR
from sqlalchemy.dialects.mysql import NVARCHAR
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db
from datetime import datetime
from sqlalchemy import Sequence

Base = declarative_base(metadata = db.metadata)

class Chasis(Base):
    __tablename__ = 'st_chasis'
    __table_args__ = (
        Index('idx_chasis_codigo', 'codigo_chasis'),
        {'schema': 'stock'}
    )

    codigo_chasis = Column(
        NUMBER(14, 0),
        Sequence('seq_st_chasis', schema='stock'),
        primary_key=True)

    aros_rueda_posterior = Column(VARCHAR(50))
    neumatico_delantero = Column(VARCHAR(50))
    neumatico_trasero = Column(VARCHAR(50))
    suspension_delantera = Column(VARCHAR(50))
    suspension_trasera = Column(VARCHAR(50))
    frenos_delanteros = Column(VARCHAR(50))
    frenos_traseros = Column(VARCHAR(50))
    aros_rueda_delantera = Column(VARCHAR(50))

    usuario_crea = Column(VARCHAR(50))
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = datetime.now()
    fecha_modificacion = datetime.now()

    @classmethod
    def query(cls):
        return db.session.query(cls)

class DimensionPeso(Base):
    __tablename__ = 'st_dimensiones_peso'
    __table_args__ = {'schema': 'stock'}

    codigo_dim_peso = Column(
        NUMBER(14, 0),
        Sequence('seq_st_dimensiones_peso', schema='stock'),
        primary_key=True
    )

    altura_total = Column(NUMBER(10))
    longitud_total = Column(NUMBER(10))
    ancho_total = Column(NUMBER(10))
    peso_seco = Column(NUMBER(10))
    usuario_crea = Column(VARCHAR(50))
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = datetime.now()
    fecha_modificacion = datetime.now()

    @classmethod
    def query(cls):
        return db.session.query(cls)

class ElectronicaOtros(Base):
    __tablename__ = 'st_electronica_otros'
    __table_args__ = {'schema': 'stock'}

    codigo_electronica = Column(
        NUMBER(14, 0),
        Sequence('seq_st_electronica_otros', schema='stock'),
        primary_key=True
    )

    capacidad_combustible = Column(VARCHAR(70))
    tablero = Column(VARCHAR(70))
    luces_delanteras = Column(VARCHAR(50))
    luces_posteriores = Column(VARCHAR(50))
    garantia = Column(VARCHAR(70))
    velocidad_maxima = Column(VARCHAR(50))
    usuario_crea = Column(VARCHAR(50))
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = datetime.now()
    fecha_modificacion = datetime.now()

    @classmethod
    def query(cls):
        return db.session.query(cls)