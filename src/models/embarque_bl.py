# coding: utf-8
from sqlalchemy import Column, DateTime, Index, VARCHAR, text, CHAR
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

Base = declarative_base(metadata = db.metadata)

class StPuertosEmbarque(Base):
    __tablename__ = 'st_puertos_embarque'
    __table_args__ = {'schema': 'stock'}

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_puerto = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    descripcion = Column(VARCHAR(100))

    @classmethod
    def query(cls):
        return db.session.query(cls)
    
class StEmbarquesBl(Base):
    __tablename__ = 'st_embarques_bl'
    __table_args__ = (
        Index('ind_embaques_tg_modelo_item', 'cod_item', 'cod_modelo', 'empresa'),
        Index('ind_embarques_bl03', 'cod_puerto_embarque', 'empresa'),
        Index('ind_embarques_naviera', 'empresa', 'naviera'),
        Index('ind_embarques_bl02', 'cod_puerto_desembarque', 'empresa'),
        Index('ind_embarques_tipo_aforo', 'empresa', 'cod_aforo'),
        Index('ind_embarques_regimen', 'cod_regimen' ),
        Index('ind_embarques_bl01', 'cod_proveedor'),
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
    naviera = Column(VARCHAR(9))
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
    cod_regimen = Column(NUMBER(3, 0, False), index=True)
    nro_mrn = Column(VARCHAR(40))
    bl_house_manual = Column(VARCHAR(30))

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

class StEmbarqueContenedores(Base):
    __tablename__ = 'st_embarque_contenedores'
    __table_args__ = (
        Index('pk_st_embarque_contenedores', 'nro_contenedor', 'codigo_bl_house', 'empresa'),
        Index('udx1_fk_st_emb_cont_st_emb_bl', 'codigo_bl_house', 'empresa'),
        Index('udx2_st_emb_cont_empresa', 'empresa'),
        Index('udx3_st_emb_con_st_tipo_con', 'cod_tipo_contenedor', 'empresa'),
        Index('udx4_st_emb_cont_tg_mod_item', 'cod_modelo', 'cod_item', 'empresa'),
        {'schema': 'stock'}
    )

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False, index=True)
    codigo_bl_house = Column(VARCHAR(30), primary_key=True, nullable=False, index=True)
    nro_contenedor = Column(VARCHAR(15), primary_key=True, nullable=False, index=True)
    cod_tipo_contenedor = Column(VARCHAR(10))
    peso = Column(NUMBER(11,3))
    volumen = Column(NUMBER(6,2))
    line_seal = Column(VARCHAR(15))
    shipper_seal = Column(VARCHAR(15))
    es_carga_suelta = Column(NUMBER(1))
    observaciones = Column(VARCHAR(150))
    usuario_crea = Column(VARCHAR(30))
    fecha_crea = Column(DateTime)
    usuario_modifica = Column(VARCHAR(30))
    fecha_modifica = Column(DateTime)
    fecha_bodega = Column(DateTime)
    cod_modelo = Column(VARCHAR(8))
    cod_item = Column(VARCHAR(3))
    @classmethod
    def query(cls):
        return db.session.query(cls)

class StTrackingContenedores(Base):
    __tablename__ = 'st_tracking_contenedores'
    __table_args__ = (
        Index('idx1_track_cont_tg_modelo_item', 'cod_item', 'cod_modelo', 'empresa'),
        Index('pk_st_tracking_contenedores', 'nro_contenedor', 'empresa', 'secuencial'),
        Index('idx3_track_cont_empresa', 'empresa'),
        Index('idx4_track_cont_st_emb_cont', 'nro_contenedor', 'empresa', 'codigo_bl_house'),
        {'schema': 'stock'}
    )

    nro_contenedor = Column(VARCHAR(30), primary_key=True, nullable=False)
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
    codigo_bl_house = Column(VARCHAR(30))
    @classmethod
    def query(cls):
        return db.session.query(cls)
class StTipoContenedor(Base):
    __tablename__ = 'st_tipo_contenedor'
    __table_args__ = (
        Index('fk_tipo_cont_empresa', 'empresa'),
        Index('pk_st_tipo_contenedor', 'cod_tipo_contenedor', 'empresa'),
        {'schema': 'stock'}
    )

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False, index=True)
    cod_tipo_contenedor = Column(VARCHAR(10), primary_key=True, nullable=False, index=True)
    nombre = Column(VARCHAR(100), nullable=False)
    es_activo = Column(NUMBER(1))
    usuario_crea = Column(VARCHAR(30))
    fecha_crea = Column(DateTime)
    @classmethod
    def query(cls):
        return db.session.query(cls)