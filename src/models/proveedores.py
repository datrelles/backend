# coding: utf-8
from sqlalchemy import Column, DateTime, Index, VARCHAR, text, Date
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

class st_transportistas(Base):
    __tablename__ = 'ST_TRANSPORTISTA'
    __table_args__ = (
        {'schema': 'stock'}  # Ajusta el esquema si es necesario
    )

    cod_transportista = Column(VARCHAR(14), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2, 0, False), nullable=False)
    nombre = Column(VARCHAR(50), nullable=False)
    apellido1 = Column(VARCHAR(40), nullable=False)
    direccion = Column(VARCHAR(50))
    telefono = Column(VARCHAR(20))
    es_activo = Column(NUMBER(1, 0, False), nullable=False, server_default=text("1"))
    placa = Column(VARCHAR(20))
    cod_tipo_identificacion = Column(NUMBER(2, 0, False))
    activo_ecommerce = Column(NUMBER(1, 0, False), server_default=text("0"))

    @classmethod
    def query(cls):
        return db.session.query(cls)

class st_provedor(Base):
    __tablename__ = 'proveedor'
    __table_args__ = (
        Index('PK_PROVEEDOR', 'empresa', 'cod_proveedor'),
        {'schema': 'stock'}
    )

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
    tipo_bodega = Column(NUMBER(1), nullable=False, server_default=text("3"))
    @classmethod
    def query(cls):
        return db.session.query(cls)

class st_proveedor_cuenta(Base):
    __tablename__ = 'st_proveedor_cuenta'
    __table_args__ = (
        Index('IND_PROVEEDOR_CUENTA01', 'codigo', 'aa', 'empresa'),
        {'schema': 'stock'}
    )

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_proveedor = Column(VARCHAR(14), primary_key=True, nullable=False)
    aa = Column(NUMBER(4), primary_key=True, nullable=False)
    codigo = Column(VARCHAR(14), primary_key=True, nullable=False)
    cod_sistema = Column(VARCHAR(3), primary_key=True, nullable=False)
    cod_parametro = Column(VARCHAR(2), primary_key=True, nullable=False)
    codigo_ant = Column(VARCHAR(14))
    codigo_tran = Column(VARCHAR(14))
    codigo_tran_ant = Column(VARCHAR(14))
    @classmethod
    def query(cls):
        return db.session.query(cls)

class tc_coa_tipo_contribuyente(Base):
    __tablename__ = 'tc_coa_tipo_contribuyente'
    __table_args__ = (
        {'schema': 'contabilidad'}
    )

    cod_tipo_contribuyente = Column(NUMBER(2), primary_key=True, nullable=False)
    descripcion = Column(VARCHAR(300))
    adicionador_por = Column(VARCHAR(30), server_default=text("USER"))
    fecha_adicion = Column(Date, server_default=text("SYSDATE"))
    @classmethod
    def query(cls):
        return db.session.query(cls)

class st_banco(Base):
    __tablename__ = 'st_banco'
    __table_args__ = (
        Index('PK_ST_BANCO', 'cod_banco'),
        {'schema': 'stock'}
    )

    cod_banco = Column(VARCHAR(3), primary_key=True, nullable=False)
    nombre = Column(VARCHAR(40), nullable=False)
    telefono = Column(VARCHAR(8))
    pais_banco = Column(VARCHAR(20))
    ciudad = Column(VARCHAR(20))
    logo = Column(VARCHAR(50))
    genera_cheque = Column(VARCHAR(1))
    activa_banco = Column(VARCHAR(1))
    es_multicash = Column(NUMBER(1))

    @classmethod
    def query(cls):
        return db.session.query(cls)

class tc_instituciones_multicash(Base):
    __tablename__ = 'tc_instituciones_multicash'
    __table_args__ = (
        Index('PK_INST_MULTICASH', 'codigo', 'cod_banco'),
        {'schema': 'contabilidad'}
    )

    codigo = Column(VARCHAR(9), primary_key=True, nullable=False)
    nombre = Column(VARCHAR(100), nullable=False)
    cod_banco = Column(VARCHAR(9),  primary_key=True, nullable=False)

    @classmethod
    def query(cls):
        return db.session.query(cls)

class tc_prov_cta_multicash(Base):
    __tablename__ = 'tc_prov_cta_multicash'
    __table_args__ = (
        Index('PK_PROV_CTA_MULTICASH', 'empresa', 'ruc', 'codigo_institucion', 'num_cuenta', 'cod_banco'),
        {'schema': 'contabilidad'}
    )

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    ruc = Column(VARCHAR(20), primary_key=True, nullable=False)
    codigo_institucion = Column(VARCHAR(9), primary_key=True, nullable=False)
    num_cuenta = Column(VARCHAR(50), primary_key=True, nullable=False)
    cod_banco = Column(VARCHAR(3), primary_key=True, nullable=False)
    tipo_cuenta = Column(VARCHAR(10), nullable=False)
    nombre_banco = Column(VARCHAR(150), nullable=False)
    tipo_identificacion = Column(VARCHAR(1))
    identificacion_titular = Column(VARCHAR(20))
    nombre_titular = Column(VARCHAR(100))

    @classmethod
    def query(cls):
        return db.session.query(cls)
