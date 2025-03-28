from sqlalchemy import Column, DateTime, Index, VARCHAR, text, ForeignKeyConstraint,  PrimaryKeyConstraint
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

Base = declarative_base(metadata = db.metadata)

class StLote(Base):
    __tablename__ = 'st_lote'
    __table_args__ = (
        Index('IND_ST_LOTE_01', 'empresa', 'cod_agencia'),
        Index('IND_ST_LOTE_02', 'tipo_lote', 'empresa'),
        Index('PK_ST_LOTE', 'cod_comprobante', 'tipo_comprobante', 'empresa'),
        {'schema': 'stock'}
    )

    empresa = Column(NUMBER(2), primary_key=True, nullable=False)
    tipo_comprobante = Column(VARCHAR(2), primary_key=True, nullable=False)
    cod_comprobante = Column(VARCHAR(9), primary_key=True, nullable=False)
    fecha = Column(DateTime, nullable=False)
    descripcion = Column(VARCHAR(200))
    tipo_lote = Column(VARCHAR(2))
    cod_agencia = Column(NUMBER(4))
    usuario_aud = Column(VARCHAR(30))
    fecha_aud = Column(DateTime)
    @classmethod
    def query(cls):
        return db.session.query(cls)

class Sta_Comprobante(Base):
    __tablename__ = 'sta_comprobante'
    __table_args__ = (
        Index('PKCOMPROBANTE', 'cod_comprobante', 'tipo_comprobante', 'empresa'),
        Index('IDXA_COMP_AGENCIA', 'empresa', 'cod_agencia'),
        Index('IDXA_COMP_BODEGA_E', 'empresa', 'cod_bodega_egreso'),
        Index('IDXA_COMP_BODEGA_I', 'empresa', 'cod_bodega_ingreso'),
        Index('IDXA_COMP_LIQUIDACION', 'empresa', 'cod_liquidacion'),
        Index('IDXA_COMP_MOTIVO_TRANSFERENCIA', 'cod_motivo', 'empresa'),
        Index('IDXA_COMP_PERSONA_A', 'empresa', 'cod_tipo_persona_a', 'cod_persona_a'),
        Index('IDXA_COMP_PERSONA_B', 'empresa', 'cod_tipo_persona_b', 'cod_persona_b'),
        Index('IDXA_COMP_SUBBODEGA_I', 'empresa', 'cod_bodega_ingreso', 'cod_subbodega_ingreso'),
        Index('IDXA_COMP_TIPO_COMP', 'empresa', 'tipo_comprobante'),
        Index('IDXA_SUBBODEGA_E', 'empresa', 'cod_bodega_egreso', 'cod_subbodega_egreso'),
        Index('IDX_STA_COMP_EST_PROD_EGR', 'cod_estado_producto_egreso', 'empresa'),
        Index('IDX_STA_COMP_EST_PROD_ING', 'cod_estado_producto_ingreso', 'empresa'),
        {'schema': 'stock'}
    )

    cod_comprobante = Column(VARCHAR(9), primary_key=True, nullable=False)
    tipo_comprobante = Column(VARCHAR(2), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2), primary_key=True, nullable=False)
    cod_agencia = Column(NUMBER(4), nullable=False)
    fecha = Column(DateTime, nullable=False)
    comprobante_manual = Column(VARCHAR(30))
    cod_tipo_persona_a = Column(VARCHAR(3))
    cod_persona_a = Column(VARCHAR(14))
    cod_tipo_persona_b = Column(VARCHAR(3))
    cod_persona_b = Column(VARCHAR(14))
    cod_bodega_ingreso = Column(NUMBER(4))
    cod_subbodega_ingreso = Column(NUMBER(3))
    cod_bodega_egreso = Column(NUMBER(4))
    cod_subbodega_egreso = Column(NUMBER(3))
    cod_liquidacion = Column(VARCHAR(9))
    useridc = Column(VARCHAR(3), nullable=False)
    es_grabado = Column(NUMBER(1), nullable=False, default=0)
    es_anulado = Column(NUMBER(1), nullable=False, default=0)
    tipo_transferencia = Column(VARCHAR(1))
    tipo_comprobante_pedido = Column(VARCHAR(2))
    cod_comprobante_pedido = Column(VARCHAR(9))
    cod_estado_producto_egreso = Column(VARCHAR(2))
    cod_estado_producto_ingreso = Column(VARCHAR(2))
    cod_estado_proceso = Column(VARCHAR(7))
    transportador = Column(VARCHAR(30))
    placa = Column(VARCHAR(30))
    tipo_comprobante_lote = Column(VARCHAR(2))
    cod_comprobante_lote = Column(VARCHAR(9))
    cod_comprobante_ingreso = Column(VARCHAR(9))
    tipo_comprobante_ingreso = Column(VARCHAR(2))
    tipo_identificacion_transporta = Column(NUMBER(2))
    cod_motivo = Column(NUMBER(3))
    ruta = Column(VARCHAR(300))

    @classmethod
    def query(cls):
        return db.session.query(cls)

class Sta_Movimiento(Base):
    __tablename__ = 'sta_movimiento'
    __table_args__ = (
        Index('PKA_MOVIMIENTO', 'cod_comprobante', 'tipo_comprobante', 'empresa', 'cod_secuencia_mov'),
        ForeignKeyConstraint(
            ['cod_comprobante', 'tipo_comprobante', 'empresa'],
            ['stock.sta_comprobante.cod_comprobante', 'stock.sta_comprobante.tipo_comprobante', 'stock.sta_comprobante.empresa'],
            name='FKA_MOV_COMP'
        ),
        {'schema': 'stock'}
    )

    cod_comprobante = Column(VARCHAR(9), primary_key=True, nullable=False)
    tipo_comprobante = Column(VARCHAR(2), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_secuencia_mov = Column(NUMBER(4), primary_key=True, nullable=False)
    cod_producto = Column(VARCHAR(14), nullable=False)
    cod_unidad = Column(VARCHAR(8), nullable=False)
    cantidad = Column(NUMBER(14, 2), nullable=False)
    es_serie = Column(NUMBER(1), nullable=False)
    cod_estado_producto = Column(VARCHAR(2))
    ubicacion_bodega = Column(VARCHAR(50))
    cod_tipo_lote = Column(VARCHAR(2))
    cod_comprobante_lote = Column(VARCHAR(9))
    cod_estado_producto_ing = Column(VARCHAR(2))
    cantidad_pedida = Column(NUMBER(14, 2))

    @classmethod
    def query(cls):
        return db.session.query(cls)

class st_inventario_lote(Base):
    __tablename__ = 'ST_INVENTARIO_LOTE'
    __table_args__ = (
        PrimaryKeyConstraint(
            'cod_producto',
            'cod_unidad',
            'empresa',
            'cod_aamm',
            'cod_bodega',
            'cod_estado_producto',
            'cod_tipo_inventario',
            'tipo_comprobante_lote',
            'cod_comprobante_lote',
            name='PK_ST_INVENTARIO_LOTE'
        ),
        ForeignKeyConstraint(
            ['empresa', 'cod_bodega'],
            ['BODEGA.EMPRESA', 'BODEGA.BODEGA'],
            name='FK_ST_INV_LT_BODEGA'
        ),
        ForeignKeyConstraint(
            ['empresa', 'cod_producto'],
            ['PRODUCTO.EMPRESA', 'PRODUCTO.COD_PRODUCTO'],
            name='FK_ST_INV_LT_PRODUCTO'
        ),
        # If the table is in a specific schema, e.g. 'stock':
        # {'schema': 'stock'}
    )

    cod_producto = Column(VARCHAR(14), nullable=False)
    cod_aamm = Column(NUMBER(6), nullable=False)
    tipo_comprobante_lote = Column(VARCHAR(2), nullable=False)
    cod_comprobante_lote = Column(VARCHAR(9), nullable=False)
    cod_bodega = Column(NUMBER(4), nullable=False)
    cod_unidad = Column(VARCHAR(8), nullable=False)
    empresa = Column(NUMBER(2), nullable=False)
    aa = Column(NUMBER(4), nullable=False)
    mm = Column(NUMBER(2), nullable=False)
    cantidad_ingreso = Column(NUMBER(14, 2), nullable=False)
    cantidad_egreso = Column(NUMBER(14, 2), nullable=False)
    cantidad = Column(NUMBER(14, 2), nullable=False)
    cantidad_ventas = Column(NUMBER(14, 2))
    cantidad_compras = Column(NUMBER(14, 2))
    valor_ventas = Column(NUMBER(14, 2))
    valor_compras = Column(NUMBER(14, 2))
    valor = Column(NUMBER(14, 2))
    valor_costo_ventas = Column(NUMBER(14, 2))
    cod_estado_producto = Column(VARCHAR(2), nullable=False, server_default=text("'A'"))
    cod_tipo_inventario = Column(NUMBER(2), nullable=False, server_default=text("1"))

    @classmethod
    def query(cls):
        return db.session.query(cls)