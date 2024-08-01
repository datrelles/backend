# coding: utf-8
from sqlalchemy import Column, DateTime, Index, VARCHAR, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

Base = declarative_base(metadata = db.metadata)

class StAsignacionCupo(Base):
    __tablename__ = 'st_asignacion_cupo'
    __table_args__ = (
        Index('PK_ASIGNACION_CUPO', 'empresa', 'ruc_cliente', 'cod_producto'),
        Index('UDX_ASIGNA_CUPO_CLIENTE', 'empresa', 'ruc_cliente'),
        Index('UDX_ASIGNA_CUPO_PRODUCTO', 'empresa', 'cod_producto'),
        {'schema': 'stock'}
    )

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    ruc_cliente = Column(VARCHAR(13), primary_key=True, nullable=False)
    cod_producto = Column(VARCHAR(20), primary_key=True, nullable=False)
    porcentaje_maximo = Column(NUMBER(14,2))
    cantidad_minima = Column(NUMBER(10))
    @classmethod
    def query(cls):
        return db.session.query(cls)