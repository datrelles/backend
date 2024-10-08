# coding: utf-8
from sqlalchemy import Column, VARCHAR
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db


Base = declarative_base(metadata = db.metadata)

class StUnidadImportacion(Base):
    __tablename__ = 'st_unidad_importacion'
    __table_args__ = {'schema': 'stock'}

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_unidad = Column(VARCHAR(8), primary_key=True, nullable=False)
    nombre = Column(VARCHAR(80))

    @classmethod
    def query(cls):
        return db.session.query(cls)