# coding: utf-8
from sqlalchemy import CHAR, Column, DateTime, Index, VARCHAR, text, Boolean, Index
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from config.database import db

Base = declarative_base(metadata = db.metadata)

class StOrdenCompraCab(Base):
    __tablename__ = 'st_orden_compra_cab'
    __table_args__ = (
        Index('udx1_bodega', 'empresa', 'bodega'),
        Index('udx4_agencia', 'empresa', 'cod_agencia'),
        Index('udx5_tipo_comprobante', 'empresa', 'tipo_comprobante'),
        Index('udx8_tc_opago', 'empresa', 'cod_opago'),
        Index('udx7_tg_modelo_item', 'empresa', 'cod_modelo', 'cod_item'),
        Index('udx3_proveedor', 'empresa', 'cod_proveedor'),
        {'schema': 'stock'}
    )

    cod_po = Column(VARCHAR(9), primary_key=True, nullable=False)
    tipo_comprobante = Column(VARCHAR(2), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_proveedor = Column(VARCHAR(14))
    nombre = Column(VARCHAR(100))
    usuario_crea = Column(VARCHAR(20), index=True)
    fecha_crea = Column(DateTime)
    usuario_modifica = Column(VARCHAR(20))
    fecha_modifica = Column(DateTime)
    proforma = Column(VARCHAR(30))
    bodega = Column(NUMBER(4, 0, False))
    cod_agencia = Column(NUMBER(4, 0, False))
    ciudad = Column(VARCHAR(60))
    fecha_estimada_produccion = Column(DateTime, comment='FECHA ESTIMAD A DEL 1ER EMBARQUE (INFORMATIVO)')
    fecha_estimada_puerto = Column(DateTime, comment='FECHA ESTIMAD A DEL 1ER EMBARQUE (INFORMATIVO)')
    fecha_estimada_llegada = Column(DateTime, comment='FECHA ESTIMAD A DEL 1ER EMBARQUE (INFORMATIVO)')
    cod_item = Column(VARCHAR(3))
    cod_modelo = Column(VARCHAR(8))
    cod_opago = Column(VARCHAR(9))

    @classmethod
    def query(cls):
        return db.session.query(cls)

class StOrdenCompraDet(Base):
    __tablename__ = 'st_orden_compra_det'
    __table_args__ = (
        Index('udx1_producto', 'empresa', 'cod_producto'),
        Index('udx2_unidad_medida', 'empresa', 'unidad_medida'),
        {'schema': 'stock'}
    )

    cod_po = Column(VARCHAR(9), primary_key=True, nullable=False)
    tipo_comprobante = Column(VARCHAR(2), primary_key=True, nullable=False)
    secuencia = Column(NUMBER(6, 0, False), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_producto = Column(VARCHAR(14))
    nombre = Column(VARCHAR(200))
    costo_sistema = Column(NUMBER(16, 6, True))
    fob = Column(NUMBER(16, 6, True))
    cantidad_pedido = Column(NUMBER(9, 0, False))
    saldo_producto = Column(NUMBER(16, 6, True))
    unidad_medida = Column(VARCHAR(8))
    usuario_crea = Column(VARCHAR(30))
    fecha_crea = Column(DateTime)
    usuario_modifica = Column(VARCHAR(30))
    fecha_modifica = Column(DateTime)
    fob_total = Column(NUMBER(16, 6, True))
    nombre_i = Column(VARCHAR(200))
    nombre_c = Column(VARCHAR(200))
    exportar = Column(Boolean, default = True)
    nombre_mod_prov = Column(VARCHAR(50))
    nombre_comercial = Column(VARCHAR(50))
    costo_cotizado = Column(NUMBER(16, 6, True))
    fecha_costo = Column(DateTime)
    cod_producto_modelo = Column(VARCHAR(14))

    @classmethod
    def query(cls):
        return db.session.query(cls)
    
'''class StOrdenCompraTracking(Base):
    __tablename__ = 'st_orden_compra_tracking'
    __table_args__ = {'schema': 'stock'}

    cod_po = Column(VARCHAR(9), primary_key=True, nullable=False)
    tipo_comprobante = Column(VARCHAR(2), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    observaciones = Column(VARCHAR(150))
    fecha_cambio = Column(DateTime)
    estado = Column(VARCHAR(3))
    usuario_crea = Column(VARCHAR(30), index=True)
    fecha_crea = Column(DateTime)
    usuario_modifica = Column(VARCHAR(30))
    fecha_modifica = Column(DateTime)
    
    @classmethod
    def query(cls):
        return db.session.query(cls)'''
    
class StPackinglist(Base):
    __tablename__ = 'st_packinglist'
    __table_args__ = (
        Index('udx2_packing_embarques_bl', 'codigo_bl_house', 'empresa'),
        Index('ind_oackinglist01', 'empresa', 'cod_producto'),
        Index('ind_packinglist_ocompracab', 'cod_po', 'tipo_comprobante', 'empresa'),
        Index('udx1_packing_st_u_import', 'empresa', 'unidad_medida'),
        Index('udx3_packinglist_tc_valoracion', 'cod_liquidacion', 'cod_tipo_liquidacion', 'empresa'),
        {'schema': 'stock'}
    )

    codigo_bl_house = Column(VARCHAR(30), primary_key=True, nullable=False)
    secuencia = Column(NUMBER(9, 0, False), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_po = Column(VARCHAR(9))
    tipo_comprobante = Column(VARCHAR(2))
    cod_producto = Column(VARCHAR(14))
    cantidad = Column(NUMBER(asdecimal=False))
    fob = Column(NUMBER(14, 2, True))
    unidad_medida = Column(VARCHAR(8))
    cod_liquidacion = Column(VARCHAR(9))
    cod_tipo_liquidacion = Column(VARCHAR(3))
    usuario_crea = Column(VARCHAR(30), index=True)
    fecha_crea = Column(DateTime)
    usuario_modifica = Column(VARCHAR(30))
    fecha_modifica = Column(DateTime)

    @classmethod
    def query(cls):
        return db.session.query(cls)
    
class TcOpago(Base):
    __tablename__ = 'tc_opago'
    __table_args__ = (
        Index('opago$cuenta', 'cod_cuenta', 'aa', 'empresa'),
        Index('idx_tc_opago_liquidacion', 'empresa', 'cod_liquidacion'),
        Index('idx_tc_opago_persona', 'empresa', 'cod_tipo_persona_so', 'cod_persona_so'),
        Index('uk_tc_opago_factura', 'empresa', 'ruc', 'nro_autorizacion_contribuyente', 'factura_manual', 'es_anulado', 'cod_tipo_comprobante_coa', unique=True),
        Index('idx_tc_opago_agencia', 'empresa', 'cod_agencia'),
        Index('idx_tc_opago_st_cta_cc', 'empresa', 'aa', 'cod_cuenta', 'cod_cto_costo'),
        {'schema': 'contabilidad'}
    )

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_opago = Column(VARCHAR(9), primary_key=True, nullable=False)
    fecha_solicitud = Column(DateTime, nullable=False)
    cod_tipo_persona_so = Column(VARCHAR(3), nullable=False)
    cod_persona_so = Column(VARCHAR(14), nullable=False)
    ruc = Column(VARCHAR(13), index=True, server_default=text("NULL"))
    nro_autorizacion_contribuyente = Column(VARCHAR(49), server_default=text("NULL"))
    cod_tipo_comprobante_coa = Column(VARCHAR(2), index=True)
    factura_manual = Column(VARCHAR(20), nullable=False)
    cod_destino_coa = Column(VARCHAR(2), index=True)
    cod_provincia_coa = Column(VARCHAR(2), index=True)
    cod_categoria_gas = Column(NUMBER(3, 0, False), nullable=False)
    beneficiario = Column(VARCHAR(100), nullable=False, index=True)
    cod_cuenta = Column(VARCHAR(14))
    aa = Column(NUMBER(4, 0, False))
    cod_cto_costo = Column(VARCHAR(6))
    concepto = Column(VARCHAR(150), nullable=False)
    es_pagado = Column(NUMBER(1, 0, False))
    es_anulado = Column(VARCHAR(1))
    es_nacional = Column(NUMBER(1, 0, False))
    cod_tipo_liquidacion = Column(VARCHAR(3))
    cod_liquidacion = Column(VARCHAR(9))
    cod_agencia = Column(NUMBER(4, 0, False), nullable=False)
    cod_divisa = Column(VARCHAR(20), index=True)
    es_extrapresupuesto = Column(NUMBER(1, 0, False))
    fecha_extrapresupuesto = Column(DateTime)
    aud_fecha = Column(DateTime)
    aud_usuario = Column(VARCHAR(30))
    aud_terminal = Column(VARCHAR(50))
    tipo = Column(VARCHAR(2))
    es_envio_mail = Column(NUMBER(1, 0, False))
    fecha_revisa_presupuesto = Column(DateTime)
    clave_acceso = Column(VARCHAR(49))
    cod_liq_compra = Column(VARCHAR(9))
    cod_tipo_liq_compra = Column(VARCHAR(2))
    usuario_extrapresupuesto = Column(VARCHAR(30))

    @classmethod
    def query(cls):
        return db.session.query(cls)
    
class TcValoracion(Base):
    __tablename__ = 'tc_valoracion'
    __table_args__ = {'schema': 'contabilidad'}

    cod_liquidacion = Column(VARCHAR(9), primary_key=True, nullable=False)
    cod_tipo_liquidacion = Column(VARCHAR(3), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_cuenta = Column(VARCHAR(14), nullable=False)
    aa = Column(NUMBER(4, 0, False), nullable=False)
    cod_centro_costo = Column(VARCHAR(6))
    fecha = Column(DateTime)
    es_liquidado = Column(VARCHAR(1))
    cod_tipo_persona = Column(VARCHAR(3))
    cod_persona = Column(VARCHAR(14))
    nombre = Column(VARCHAR(50))
    factura_manual = Column(VARCHAR(9))
    cod_persona_sol = Column(VARCHAR(14))
    cod_tipo_persona_sol = Column(VARCHAR(3))
    presupuesto_cerrado = Column(NUMBER(1, 0, False), server_default=text("""\
0
"""))
    es_anulado = Column(NUMBER(1, 0, False), server_default=text("""\
0
"""))
    numero_dau = Column(VARCHAR(30))
    numero_liquidacion = Column(VARCHAR(30))
    fecha_dau = Column(DateTime)
    numero_bl = Column(VARCHAR(30))
    cod_valoracion_precede = Column(VARCHAR(9))
    tipo_valoracion_precede = Column(VARCHAR(2))
    tipo_proveedor = Column(VARCHAR(3))
    numero_carta = Column(VARCHAR(30))
    icoterm = Column(VARCHAR(3), comment='VIENE DE TG_MODELO_ITEM COD_MODELO=ICOTERM')

    @classmethod
    def query(cls):
        return db.session.query(cls)
    
class StTracking(Base):
    __tablename__ = 'st_tracking'
    __table_args__ = (
        Index('idx_st_tracking_st_ord_ccab', 'cod_po', 'tipo_comprobante', 'empresa'),
        Index('idx1_tracking_tg_modelo_item', 'empresa', 'cod_modelo', 'cod_item'),
        {'schema': 'stock'}
    )

    cod_po = Column(VARCHAR(9), primary_key=True, nullable=False)
    tipo_comprobante = Column(VARCHAR(2), primary_key=True, nullable=False)
    secuencia = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_modelo = Column(VARCHAR(8))
    cod_item = Column(VARCHAR(3))
    observaciones = Column(CHAR(150))
    fecha = Column(DateTime)
    usuario_crea = Column(VARCHAR(30))
    fecha_crea = Column(DateTime)
    usuario_modifica = Column(VARCHAR(30))
    fecha_modifica = Column(DateTime)

    @classmethod
    def query(cls):
        return db.session.query(cls)