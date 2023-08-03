# coding: utf-8
from sqlalchemy import Column, DateTime, VARCHAR, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

Base = declarative_base(metadata = db.metadata)

class StNaviera(Base):
    __tablename__ = 'st_naviera'
    __table_args__ = {'schema': 'stock'}

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False, index=True)
    codigo = Column(VARCHAR(9), primary_key=True, nullable=False)
    nombre = Column(VARCHAR(100))
    estado = Column(NUMBER(1, 0, False), server_default=text("1"), comment='0 = INACTIVO; 1= ACTIVO')
    usuario_crea = Column(VARCHAR(20))
    fecha_crea = Column(DateTime)
    usuario_modifica = Column(VARCHAR(20))
    fecha_modifica = Column(DateTime)

    @classmethod
    def query(cls):
        return db.session.query(cls)