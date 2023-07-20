# coding: utf-8
from sqlalchemy import Column, DateTime, Index, LargeBinary, VARCHAR, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

Base = declarative_base(metadata = db.metadata)

class StDespiece(Base):
    __tablename__ = 'st_despiece'
    __table_args__ = (
        Index('idx_despiece_marca', 'empresa', 'cod_marca'),
        Index('ind$_despice_padre', 'cod_despiece_padre', 'empresa'),
        {'schema': 'stock'}
    )

    cod_despiece = Column(VARCHAR(20), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    nombre_c = Column(VARCHAR(200), nullable=False)
    nombre_i = Column(VARCHAR(200), nullable=False)
    nombre_e = Column(VARCHAR(200), nullable=False)
    nivel = Column(NUMBER(1, 0, False), nullable=False, index=True)
    cod_despiece_padre = Column(VARCHAR(20))
    cod_despice_d = Column(VARCHAR(20))
    foto = Column(LargeBinary)
    nombre_imagen = Column(VARCHAR(50), comment='UTILIZADO PARA ENTORNO WEB')
    cod_marca = Column(NUMBER(3, 0, False), comment='VIENE DE MARCA')

    @classmethod
    def query(cls):
        return db.session.query(cls)

class StDespieceD(Base):
    __tablename__ = 'st_despiece_d'
    __table_args__ = (
        Index('ind$_despiece_d_fk_desp', 'cod_despiece', 'empresa'),
        {'schema': 'stock'}
    )

    cod_despiece = Column(VARCHAR(20), primary_key=True, nullable=False)
    secuencia = Column(NUMBER(5, 1, True), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    partno = Column(VARCHAR(100))
    nombre_c = Column(VARCHAR(200))
    nombre_i = Column(VARCHAR(200))
    nombre_e = Column(VARCHAR(200))
    cantidad = Column(NUMBER(9, 2, True))
    remark = Column(VARCHAR(20))
    precio_ref = Column(NUMBER(14, 2, True))
    coordenadas = Column(VARCHAR(20))
    es_web = Column(NUMBER(1, 0, False), nullable=False, server_default=text("1 "))

    @classmethod
    def query(cls):
        return db.session.query(cls)