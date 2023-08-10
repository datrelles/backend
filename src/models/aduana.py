# coding: utf-8
from sqlalchemy import Column, DateTime, VARCHAR, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

Base = declarative_base(metadata = db.metadata)

class StAduRegimen(Base):
    __tablename__ = 'st_adu_regimen'
    __table_args__ = {'schema': 'stock'}

    cod_regimen = Column(NUMBER(3, 0, False), primary_key=True)
    descripcion = Column(VARCHAR(100), nullable=False)
    es_activo = Column(NUMBER(1, 0, False), nullable=False, server_default=text("1 "))
    adicionado_por = Column(VARCHAR(30), server_default=text("USER"))
    fecha_adicion = Column(DateTime, server_default=text("SYSDATE"))
    modificado_por = Column(VARCHAR(30))
    fecha_modificacion = Column(DateTime)
    documentos_max = Column(NUMBER(4, 0, False), nullable=False, server_default=text("1 "))
