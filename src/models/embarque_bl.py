# coding: utf-8
from sqlalchemy import Column, DateTime, Index, VARCHAR, text, CHAR
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from config.database import db

Base = declarative_base(metadata = db.metadata)

class StPuertosEmbarque(Base):
    __tablename__ = 'st_puertos_embarque'
    __table_args__ = {'schema': 'stock'}

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_puerto = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    descripcion = Column(VARCHAR(100))

class StEmbarquesBl(Base):
    __tablename__ = 'st_embarques_bl'
    __table_args__ = (
        Index('ind_embaques_tg_modelo_item', 'cod_item', 'cod_modelo', 'empresa'),
        Index('ind_embarques_tipo_aforo', 'empresa', 'cod_aforo'),
        Index('ind_embarques_bl02', 'cod_puerto_desembarque', 'empresa'),
        Index('ind_embarques_bl03', 'cod_puerto_embarque', 'empresa'),
        {'schema': 'stock'}
    )

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    codigo_bl_master = Column(VARCHAR(30), nullable=False)
    codigo_bl_house = Column(VARCHAR(30), primary_key=True, nullable=False)
    cod_proveedor = Column(VARCHAR(14), index=True)
    fecha_embarque = Column(DateTime)
    fecha_llegada = Column(DateTime)
    fecha_bodega = Column(DateTime)
    numero_tracking = Column(VARCHAR(30))
    naviera = Column(VARCHAR(100))
    estado = Column(VARCHAR(1))
    agente = Column(VARCHAR(100))
    buque = Column(VARCHAR(100))
    cod_puerto_embarque = Column(NUMBER(2, 0, False))
    cod_puerto_desembarque = Column(NUMBER(2, 0, False))
    costo_contenedor = Column(NUMBER(14, 2, True))
    descripcion = Column(VARCHAR(2000))
    tipo_flete = Column(VARCHAR(1))
    adicionado_por = Column(VARCHAR(30), nullable=False, server_default=text("USER "))
    fecha_adicion = Column(DateTime, nullable=False, server_default=text("SYSDATE "))
    modificado_por = Column(VARCHAR(30))
    fecha_modificacion = Column(DateTime)
    cod_modelo = Column(VARCHAR(8))
    cod_item = Column(VARCHAR(3))
    cod_aforo = Column(NUMBER(2, 0, False))

    @classmethod
    def query(cls):
        return db.session.query(cls)
    
class StTrackingBl(Base):
    __tablename__ = 'st_tracking_bl'
    __table_args__ = (
        Index('idx4_track_bl_st_embarque', 'cod_bl_house', 'empresa'),
        Index('idx1_track_bl_tg_modelo_item', 'cod_item', 'cod_modelo', 'empresa'),
        {'schema': 'stock'}
    )

    cod_bl_house = Column(VARCHAR(30), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False, index=True)
    secuencial = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    observaciones = Column(CHAR(150))
    cod_modelo = Column(VARCHAR(8))
    usuario_crea = Column(VARCHAR(30))
    fecha_crea = Column(DateTime)
    usuario_modifica = Column(VARCHAR(30))
    fecha_modifica = Column(DateTime)
    fecha = Column(DateTime)
    cod_item = Column(VARCHAR(3))

    @classmethod
    def query(cls):
        return db.session.query(cls)

