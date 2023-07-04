# coding: utf-8
from sqlalchemy import Column, DateTime, VARCHAR
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from config.database import db

Base = declarative_base(metadata = db.metadata)

class StTipoAforo(Base):
    __tablename__ = 'st_tipo_aforo'
    __table_args__ = {'schema': 'stock'}

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False, index=True)
    cod_aforo = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    nombre = Column(VARCHAR(50))
    valor = Column(NUMBER(3, 0, False))
    observacion = Column(VARCHAR(100))
    usuario_crea = Column(VARCHAR(20))
    fecha_crea = Column(DateTime)
    usuario_modifica = Column(VARCHAR(20))
    fecha_modifica = Column(DateTime)

    @classmethod
    def query(cls):
        return db.session.query(cls)
