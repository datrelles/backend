# coding: utf-8
from sqlalchemy import Column, DateTime, Index, VARCHAR, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

Base = declarative_base(metadata = db.metadata)

class StFormula(Base):
    __tablename__ = 'st_formula'
    __table_args__ = (
        Index('PKFORMULA', 'empresa', 'cod_formula'),
        {'schema': 'stock'}
    )

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_formula = Column(VARCHAR(9), primary_key=True, nullable=False)
    nombre = Column(VARCHAR(50))
    cod_producto = Column(VARCHAR(14))
    cod_unidad = Column(VARCHAR(8))
    cantidad_produccion = Column(NUMBER(14,4))
    activa = Column(VARCHAR(1))
    mano_obra = Column(NUMBER(14,2))
    costo_standard = Column(NUMBER(14, 3))
    debito_credito = Column(NUMBER(1))
    @classmethod
    def query(cls):
        return db.session.query(cls)

class StFormulaD(Base):
    __tablename__ = 'st_formula_d'
    __table_args__ = (
        Index('PKFORMULA_D', 'empresa', 'cod_formula', 'secuencia'),
        {'schema': 'stock'}
    )

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_formula = Column(VARCHAR(9), primary_key=True, nullable=False)
    secuencia = Column(NUMBER(4),primary_key=True, nullable=False)
    cod_producto_f = Column(VARCHAR(14))
    cod_unidad_f = Column(VARCHAR(8))
    cantidad_f = Column(NUMBER(14, 2))
    debito_credito = Column(NUMBER(1))
    costo_standard = Column(NUMBER(14, 3))
    @classmethod
    def query(cls):
        return db.session.query(cls)