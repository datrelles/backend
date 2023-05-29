# coding: utf-8
from sqlalchemy import CHAR, Column, DateTime, Index, VARCHAR, text, Boolean
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from config.database import db

Base = declarative_base(metadata = db.metadata)

class StOrdenCompraCab(Base):
    __tablename__ = 'st_orden_compra_cab'

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_po = Column(VARCHAR(9), primary_key=True, nullable=False)
    tipo_comprobante = Column(VARCHAR(2), nullable=False)
    cod_proveedor = Column(VARCHAR(14))
    nombre = Column(VARCHAR(100))
    proforma = Column(VARCHAR(30))
    invoice = Column(VARCHAR(30))
    bl_no = Column(VARCHAR(10))
    cod_po_padre = Column(VARCHAR(10))
    usuario_crea = Column(VARCHAR(20))
    fecha_crea = Column(DateTime)
    usuario_modifica = Column(VARCHAR(20))
    fecha_modifica = Column(DateTime)
    cod_modelo = Column(VARCHAR(8))
    cod_item = Column(VARCHAR(3))
    bodega = Column(NUMBER(4),nullable=False)
    cod_agencia = Column(NUMBER(4),nullable=False)
    ciudad = Column(VARCHAR(60))
    estado = Column(VARCHAR(100))

    @classmethod
    def query(cls):
        return db.session.query(cls)

class StOrdenCompraDet(Base):
    __tablename__ = 'st_orden_compra_det'

    cod_po = Column(VARCHAR(9), primary_key=True, nullable=False)
    secuencia = Column(NUMBER(6), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_producto = Column(VARCHAR(14))
    cod_producto_modelo = Column(CHAR(50))
    nombre = Column(VARCHAR(200))
    nombre_i = Column(VARCHAR(200))
    nombre_c = Column(VARCHAR(200))
    costo_sistema = Column(NUMBER(14, 2, True))
    fob = Column(NUMBER(14, 2, True))
    fob_total = Column(NUMBER(14, 2, True))
    cantidad_pedido = Column(NUMBER(14, 2, True))
    saldo_producto = Column(NUMBER(14, 2, True))
    unidad_medida = Column(VARCHAR(8))
    usuario_crea = Column(VARCHAR(30))
    fecha_crea = Column(DateTime)
    usuario_modifica = Column(VARCHAR(30))
    fecha_modifica = Column(DateTime)
    exportar = Column(Boolean, default=True)
    nombre_mod_prov = Column(VARCHAR(50))
    nombre_comercial = Column(VARCHAR(50))

    @classmethod
    def query(cls):
        return db.session.query(cls)
    
class StOrdenCompraTracking(Base):
    __tablename__ = 'st_orden_compra_tracking'
    __table_args__ = {'schema': 'stock'}

    cod_po = Column(VARCHAR(9), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    observaciones = Column(CHAR(150))
    fecha_pedido = Column(DateTime)
    fecha_transito = Column(DateTime)
    fecha_puerto = Column(DateTime)
    fecha_llegada = Column(DateTime)
    fecha_en_bodega = Column(DateTime)
    estado = Column(VARCHAR(30))
    buque = Column(VARCHAR(15))
    naviera = Column(VARCHAR(15))
    flete = Column(NUMBER(15, 0, False))
    agente_aduanero = Column(VARCHAR(20))
    puerto_origen = Column(VARCHAR(20))
    usuario_crea = Column(VARCHAR(30))
    fecha_crea = Column(DateTime)
    usuario_modifica = Column(VARCHAR(30))
    fecha_modifica = Column(DateTime)

    @classmethod
    def query(cls):
        return db.session.query(cls)
    
class StPackinglist(Base):
    __tablename__ = 'st_packinglist'
    __table_args__ = {'schema': 'stock'}

    cod_po = Column(VARCHAR(9), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    secuencia = Column(VARCHAR(10), primary_key=True, nullable=False)
    cod_producto = Column(VARCHAR(14))
    cantidad = Column(NUMBER(asdecimal=False))
    fob = Column(NUMBER(14, 2, True))
    cod_producto_modelo = Column(VARCHAR(14))
    unidad_medida = Column(VARCHAR(8))
    usuario_crea = Column(VARCHAR(3))
    fecha_crea = Column(DateTime)
    usuario_modifica = Column(CHAR(30))
    fecha_modifica = Column(DateTime)

    @classmethod
    def query(cls):
        return db.session.query(cls)