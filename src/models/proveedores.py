# coding: utf-8
from sqlalchemy import Column, DateTime, Index, VARCHAR, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship,deferred
from src.config.database import db

Base = declarative_base(metadata = db.metadata)

class TgModelo(Base):
    __tablename__ = 'tg_modelo'
    __table_args__ = (
        Index('modelo$att_din', 'empresa', 'cod_usuario_valores', 'cod_tabla_valores', 'valor_columna'),
        {'schema': 'computo'}
    )

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_modelo = Column(VARCHAR(8), primary_key=True, nullable=False)
    nombre = Column(VARCHAR(30), nullable=False)
    tabla_fuente = Column(VARCHAR(30))
    tabla_relacion = Column(VARCHAR(30))
    observaciones = Column(VARCHAR(2000))
    tipo = Column(VARCHAR(1))
    cod_usuario_enlace = Column(VARCHAR(30))
    cod_tabla_enlace = Column(VARCHAR(30))
    cod_columna_codigo = Column(VARCHAR(255))
    cod_columna_nombre = Column(VARCHAR(255))
    condiciones = Column(VARCHAR(2000))
    cod_usuario_valores = Column(VARCHAR(30))
    cod_tabla_valores = Column(VARCHAR(30))
    cod_columna_valores = Column(VARCHAR(255))
    basado_tabla = Column(VARCHAR(1))
    valor_columna = Column(VARCHAR(30))

    @classmethod
    def query(cls):
        return db.session.query(cls)


class TgModeloItem(Base):
    __tablename__ = 'tg_modelo_item'
    __table_args__ = {'schema': 'computo'}

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_modelo = Column(VARCHAR(8), primary_key=True, nullable=False)
    cod_item = Column(VARCHAR(3), primary_key=True, nullable=False)
    nombre = Column(VARCHAR(50), nullable=False)
    observaciones = Column(VARCHAR(2000))
    tipo = Column(VARCHAR(1))
    orden = Column(NUMBER(2, 0, False))
    
    @classmethod
    def query(cls):
        return db.session.query(cls)


class Proveedor(Base):
    __tablename__ = 'proveedor'

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_proveedor = Column(VARCHAR(14), primary_key=True, nullable=False)
    nombre = Column(VARCHAR(100), nullable=False)
    direccion = Column(VARCHAR(200))
    pais_telefono = Column(VARCHAR(3))
    telefono = Column(VARCHAR(10))
    telefono1 = Column(VARCHAR(10))
    fax = Column(VARCHAR(10))
    e_mail = Column(VARCHAR(50))
    casilla = Column(VARCHAR(10))
    ruc = Column(VARCHAR(13))
    useridc = Column(VARCHAR(3), nullable=False)
    contacto = Column(VARCHAR(50))
    cargo = Column(VARCHAR(30))
    activo = Column(VARCHAR(1))
    direccion_numero = Column(VARCHAR(10))
    interseccion = Column(VARCHAR(50))
    autorizacion_imprenta = Column(VARCHAR(10))
    cod_modelo = Column(VARCHAR(8))
    cod_item = Column(VARCHAR(3))
    tipo_bodega = Column(NUMBER(1, 0, False), nullable=False, server_default=text("3 "))

    #empresa = deferred(relationship(Empresa, backref = 'Proveedor'))
    #tg_modelo_item = deferred(relationship(TgModeloItem, backref = 'TgModeloItem')) 

    @classmethod
    def query(cls):
        return db.session.query(cls)

class ProveedorHor(Base):
    __tablename__ = 'proveedor_hor'

    empresah = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_proveedorh = Column(VARCHAR(14), primary_key=True, nullable=False)
    activoh = Column(VARCHAR(1))
    cod_tipo_proveedorh = Column(VARCHAR(3))
    ruch = Column(VARCHAR(13))
    contactoh = Column(VARCHAR(50))
    cargoh = Column(VARCHAR(3))
    direccion_calleh = Column(VARCHAR(50))
    direccion_numeroh = Column(VARCHAR(20))
    telefono1h = Column(VARCHAR(15))
    faxh = Column(VARCHAR(15))
    e_mailh = Column(VARCHAR(30))
    casillah = Column(VARCHAR(10))
    fecha_creacionh = Column(DateTime)
    agenciah = Column(VARCHAR(2))
    observacionesh = Column(VARCHAR(255))
    useridch = Column(VARCHAR(3))

    @classmethod
    def query(cls):
        return db.session.query(cls)

class TcCoaProveedor(Base):
    __tablename__ = 'tc_coa_proveedor'
    __table_args__ = {'schema': 'contabilidad'}

    ruc = Column(VARCHAR(13), primary_key=True)
    nombre = Column(VARCHAR(100), nullable=False)
    direccion = Column(VARCHAR(60))
    direccion_nro = Column(VARCHAR(10))
    ciudad_matriz = Column(VARCHAR(60))
    cod_tipo_documento = Column(NUMBER(1, 0, False), nullable=False, index=True)
    nombre_fantasia = Column(VARCHAR(50))
    mail = Column(VARCHAR(60))
    teledofo = Column(VARCHAR(14))
    nro_autorizacion_contribuyente = Column(VARCHAR(10))
    es_persona_natural = Column(NUMBER(1, 0, False))
    es_titulo_superior = Column(NUMBER(1, 0, False))
    es_contribuyente_especial = Column(NUMBER(1, 0, False))
    es_lleva_contabilidad = Column(NUMBER(1, 0, False))
    es_sujeto_retencion_renta = Column(NUMBER(1, 0, False))
    telefono = Column(VARCHAR(14))
    fecha_modifica = Column(DateTime)
    useridc = Column(VARCHAR(3))
    es_rise = Column(NUMBER(1, 0, False))
    celular = Column(VARCHAR(14))
    es_iva = Column(NUMBER(1, 0, False))
    parte_rel = Column(VARCHAR(2), nullable=False, server_default=text("'NO' "))
    cod_tipo_contribuyente = Column(NUMBER(2, 0, False), index=True)

    @classmethod
    def query(cls):
        return db.session.query(cls)
    
class TgAgencia(Base):
    __tablename__ = 'tg_agencia'
    __table_args__ = (
        Index('quest_sx_38357d985bf9341e8d', 'cod_agencia', 'empresa'),
        {'schema': 'computo'}
    )

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_agencia = Column(NUMBER(4, 0, False), primary_key=True, nullable=False, index=True)
    nombre = Column(VARCHAR(50), nullable=False, index=True)
    cod_categoria_zona = Column(VARCHAR(2))
    empresa_zona = Column(NUMBER(2, 0, False))
    secuencia_zona = Column(NUMBER(6, 0, False))
    cod_nivel_zona = Column(VARCHAR(8))
    codigo_zona = Column(VARCHAR(14))
    direccion = Column(VARCHAR(200))
    observaciones = Column(VARCHAR(200))
    telefono1 = Column(VARCHAR(15))
    telefono2 = Column(VARCHAR(15))
    ruc = Column(VARCHAR(20))
    activo = Column(VARCHAR(1))
    cod_grupo_agencia = Column(VARCHAR(3))
    cod_sitio = Column(VARCHAR(3), nullable=False)
    es_autorizado_sri = Column(NUMBER(1, 0, False), nullable=False, server_default=text("0 "))
    tipo_relacion_polcre = Column(VARCHAR(1), nullable=False, server_default=text("'N' "))