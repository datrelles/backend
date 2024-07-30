# coding: utf-8
from sqlalchemy import Column, DateTime, Index, VARCHAR, text, BLOB
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

Base = declarative_base(metadata = db.metadata)

class st_material_imagen(Base):
    __tablename__ = 'st_material_imagen'
    __table_args__ = (
        Index('PK_MATERIAL_IMAGEN', 'empresa', 'cod_tipo_material', 'cod_material', 'secuencia'),
        {'schema': 'stock'}
    )

    cod_tipo_material = Column(VARCHAR(3), primary_key=True, nullable=False)
    cod_material = Column(VARCHAR(14), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    secuencia = Column(NUMBER(3), primary_key=True, nullable=False)
    nombre_vista = Column(VARCHAR(100))
    imagen = Column(BLOB)
    miniatura = Column(BLOB)
    nombre_archivo = Column(VARCHAR(600))
    fecha_adicion = Column(DateTime, default=text("SYSDATE"))
    usuario = Column(VARCHAR(30), default=text("USER"))

    @classmethod
    def query(cls):
        return db.session.query(cls)

class st_despiece_d_imagen(Base):
    __tablename__ = 'st_despiece_d_imagen'
    __table_args__ = (
        Index('PK_DESPIECE_D_IMAGEN', 'cod_despiece', 'secuencia', 'empresa'),
        {'schema': 'stock'}
    )

    cod_despiece = Column(VARCHAR(20), primary_key=True, nullable=False)
    secuencia = Column(NUMBER(5, 1), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    foto = Column(BLOB)
    miniatura = Column(BLOB)
    fecha_adicion = Column(DateTime, default=text("SYSDATE"), nullable=False)
    usuario = Column(VARCHAR(30), default=text("USER"), nullable=False)

    @classmethod
    def query(cls):
        return db.session.query(cls)
