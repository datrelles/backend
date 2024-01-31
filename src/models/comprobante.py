from sqlalchemy import Column, Date, Index, VARCHAR, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

Base = declarative_base(metadata = db.metadata)

class Comprobante(Base):
    __tablename__ = 'comprobante'
    __table_args__ = (
        Index('COMP$FECHA', 'fecha'),
        Index('COMP$FECHA_AGENCIA', 'fecha', 'cod_agencia'),
        Index('COMP$LIQUIDACION', 'cod_liquidacion'),
        Index('COMP$PEDIDO', 'cod_comprobante_pedido', 'tipo_comprobante_pedido','empresa'),
        Index('COMP$PERSONA', 'cod_persona'),
        Index('COMPROBANTE_01_IDX', 'tipo_comprobante', 'cod_agencia', 'empresa', 'fecha'),
        Index('IDX_COMPROBANTE_AGENCIA', 'empresa', 'cod_agencia'),
        Index('IDX_COMPROBANTE_LIQUIDACION', 'empresa', 'cod_liquidacion'),
        Index('IDX_COMPROBANTE_PERIODO_COM', 'empresa', 'cod_periodo_comision'),
        Index('IDX_COMPROBANTE_PERSONA', 'empresa', 'cod_tipo_persona', 'cod_persona'),
        Index('IDX_COMPROBANTE_PERSONA_APROB', 'empresa', 'cod_tipo_persona_aprob', 'cod_persona_aprob'),
        Index('IDX_COMPROBANTE_PERSONA_VERIF', 'empresa', 'cod_tipo_persona_verif', 'cod_persona_verif'),
        Index('IDX_COMPROBANTE_PROFORMA', 'empresa', 'tipo_comprobante_pr', 'cod_comprobante_pr'),
        Index('IDX_COMPROBANTE_TARCRE', 'empresa', 'cod_tarjeta'),
        Index('IDX_COMPROBANTE_TIPO_COM', 'empresa', 'tipo_comprobante'),
        Index('IDX_COMPROBANTE_TIPO_DEV_ANT', 'empresa', 'secuen_certificado'),
        Index('IDX_COMPROBANTE_USUARIO_EMPRES', 'empresa', 'useridc'),
        Index('IDX_COMP_BODEGA_EGR', 'empresa', 'cod_bodega_egreso'),
        Index('IDX_COMP_BODEGA_ING', 'empresa', 'cod_bodega_ingreso'),
        Index('IDX_COMP_POLCRE', 'cod_politica', 'empresa'),
        Index('IDX_COMP_SUBBODEGA_EGRE', 'empresa', 'cod_bodega_egreso', 'cod_subbodega_egreso'),
        Index('IDX_COMP_SUBBODEGA_ING', 'empresa', 'cod_bodega_ingreso', 'cod_subbodega_ingreso'),
        Index('PK_COMPROBANTE', 'cod_comprobante', 'tipo_comprobante', 'empresa'),
        Index('QUEST_SX_38357D985BF918E213', 'fecha', 'tipo_comprobante'),
        Index('QUEST_SX_38357D985BF938DDD4', 'numero_pagos'),

        {'schema': 'stock'}
    )

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    tipo_comprobante = Column(VARCHAR(2), primary_key=True, nullable=False)
    cod_comprobante = Column(VARCHAR(9), primary_key=True, nullable=False)
    cod_tipo_persona = Column(VARCHAR(3), nullable=False)
    cod_persona = Column(VARCHAR(14), nullable=False)
    fecha = Column(Date, nullable=False, server_default=text("SYSDATE "))
    pedido = Column(VARCHAR(13))
    iva = Column(NUMBER(14,2), nullable=False)
    valor = Column(NUMBER(14, 2), nullable=False)
    financiamiento = Column(NUMBER(14, 2), nullable=False)
    otros = Column(NUMBER(14, 2), nullable=False)
    descuento = Column(NUMBER(14, 2), nullable=False)
    tipo_iva = Column(VARCHAR(1))
    c_tipo_combrobante = Column(VARCHAR(2))
    c_comprobante =  Column(VARCHAR(9))
    cod_liquidacion = Column(VARCHAR(9), nullable=False)
    useridc = Column(VARCHAR(3), nullable=False)
    factura_manual = Column(VARCHAR(9), nullable=False)
    anulado = Column(VARCHAR(1))
    guia = Column(VARCHAR(9))
    estado_grabado = Column(VARCHAR(1))
    estado_contabilizado = Column(VARCHAR(1))
    nombre_persona = Column(VARCHAR(100))
    certificado = Column(VARCHAR(8))
    secuen_certificado = Column(NUMBER(4))
    orden_compra = Column(VARCHAR(9))
    transportador = Column(VARCHAR(30))
    placa = Column(VARCHAR(7))
    observaciones = Column(VARCHAR(2000))
    entrada = Column(NUMBER(14,2))
    ice = Column(NUMBER(14,2))
    cod_agente = Column(VARCHAR(14))
    cod_divisa = Column(VARCHAR(20), nullable=False)
    valor_divisa = Column(NUMBER(14,2))
    cancelada = Column(VARCHAR(1))
    saldo = Column(NUMBER(14,2))
    cod_agencia = Column(NUMBER(4), nullable=False)
    forma_pago = Column(VARCHAR(3))
    cotizacion = Column(NUMBER(14,2))
    tipo_comprobante_r = Column(VARCHAR(2))
    cod_comprobante_r = Column(VARCHAR(9))
    transferencia = Column(VARCHAR(1))
    aa_cliente = Column(NUMBER(4))
    codigo_cliente = Column(VARCHAR(14))
    estado_comision = Column(VARCHAR(1))
    cod_periodo_comision = Column(NUMBER(6))
    linea_contabilidad = Column(NUMBER(4))
    tipo_comprobante_pr = Column(VARCHAR(3))
    cod_comprobante_pr = Column(VARCHAR(9))
    cod_tipo_persona_gar = Column(VARCHAR(3))
    cod_persona_gar = Column(VARCHAR(14))
    numero_pagos = Column(NUMBER(3), nullable=False)
    cuotas_gratis = Column(NUMBER(4,2), nullable=False)
    dias_atrazo = Column(NUMBER(6,2))
    devolucion_otros = Column(NUMBER(14,2))
    valor_alterno = Column(NUMBER(14,2))
    descuento_promocion = Column(NUMBER(14,2))
    cod_bodega_ingreso = Column(NUMBER(4))
    cod_subbodega_ingreso = Column(NUMBER(3))
    cod_bodega_egreso = Column(NUMBER(4))
    cod_subbodega_egreso = Column(NUMBER(4))
    cod_tarjeta = Column(VARCHAR(3))
    num_tarjeta = Column(VARCHAR(30))
    num_recap = Column(VARCHAR(15))
    num_voucher = Column(VARCHAR(15))
    num_autorizacion = Column(VARCHAR(15))
    cod_politica = Column(NUMBER(2))
    tipo_comprobante_pedido = Column(VARCHAR(2))
    cod_comprobante_pedido = Column(VARCHAR(9))
    fecha_ingreso = Column(Date)
    rebate = Column(NUMBER(14,2))
    base_imponible = Column(NUMBER(14,2))
    base_excenta = Column(NUMBER(14,2))
    cod_caja = Column(NUMBER(3))
    fecha_vencimiento1 = Column(Date)
    por_interes = Column(NUMBER(7,4))
    aud_fecha = Column(Date)
    aud_usuario = Column(VARCHAR(30))
    aud_terminal = Column(VARCHAR(50))
    cod_tipo_persona_aprob = Column(VARCHAR(3))
    cod_persona_aprob = Column(VARCHAR(14))
    cod_tipo_persona_verif = Column(VARCHAR(3))
    cod_persona_verif = Column(VARCHAR(14))
    interes = Column(NUMBER(14,2))
    @classmethod
    def query(cls):
        return db.session.query(cls)

class Movimiento(Base):
    __tablename__ = 'movimiento'
    __table_args__ = (

        Index('IDX_MOVIMIENTO_BODEGA', 'empresa', 'bodega'),
        Index('IDX_MOVIMIENTO_PRODUCTO', 'empresa', 'cod_producto'),
        Index('IDX_MOVIMIENTO_PROMOCION', 'cod_promocion', 'empresa'),
        Index('IDX_MOVIMIENTO_UNIDAD', 'empresa', 'cod_unidad'),
        Index('IDX_MOV_COMP', 'cod_comprobante', 'tipo_comprobante', 'empresa'),
        Index('IDX_MOV_ESTADO_PRODUCTO', 'cod_estado_producto', 'empresa'),
        Index('IDX_MOV_TIPO_INVENTARIO', 'cod_tipo_inventario'),
        Index('IDX_MOV_UBI_BOD', 'ubicacion_bodega', 'bodega', 'empresa'),
        Index('MOV$BODEGA', 'bodega'),
        Index('MOV$BODEMP', 'bodega', 'empresa'),
        Index('MOV$COMPROBANTE', 'cod_comprobante', 'tipo_comprobante'),
        Index('MOV$PRODUCTOFECHA', 'cod_producto', 'fecha'),
        Index('PK_MOVIMIENTO', 'cod_comprobante', 'tipo_comprobante', 'empresa', 'secuencia'),

        {'schema': 'stock'}
    )

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    tipo_comprobante = Column(VARCHAR(2), primary_key=True, nullable=False)
    cod_comprobante = Column(VARCHAR(9), primary_key=True, nullable=False)
    secuencia = Column(NUMBER(4), primary_key=True, nullable=False)
    cod_producto = Column(VARCHAR(14), nullable=False)
    cantidad = Column(NUMBER(14,2), nullable=False)
    debito_credito = Column(NUMBER(1), nullable=False)
    cantidad_i = Column(NUMBER(14,2))
    precio = Column(NUMBER(14,2), nullable=False)
    descuento = Column(NUMBER(14,2), nullable=False)
    costo = Column(NUMBER(17,6))
    bodega = Column(NUMBER(4), nullable=False)
    iva = Column(NUMBER(14,2), nullable=False)
    fecha = Column(Date, nullable=False)
    factura_manual = Column(VARCHAR(9), nullable=False)
    serie = Column(VARCHAR(30))
    grado = Column(NUMBER(5,2))
    cod_subbodega = Column(NUMBER(3))
    temperatura = Column(NUMBER(5,2))
    cod_unidad = Column(VARCHAR(8), nullable=False)
    divisa = Column(NUMBER(14,2), nullable=False)
    anulado = Column(VARCHAR(1), nullable=False)
    cantidad_b = Column(NUMBER(14,2))
    cantidad_i_b = Column(NUMBER(14,2))
    ice = Column(NUMBER(14,2))
    lista = Column(VARCHAR(3))
    total_linea = Column(NUMBER(14,2), nullable=False)
    porce_descuento = Column(NUMBER(10,6))
    valor_alterno = Column(NUMBER(18,6))
    es_serie = Column(NUMBER(1))
    td = Column('T$D', NUMBER(14,2))
    rebate = Column(NUMBER(14,2))
    es_iva = Column(NUMBER(1))
    cod_estado_producto = Column(VARCHAR(2), nullable=False)
    cod_tipo_inventario = Column(NUMBER(2), nullable=False)
    cod_promocion = Column(NUMBER(4))
    ubicacion_bodega = Column(VARCHAR(50))
    cantidad_promocion = Column(NUMBER(14,2))
    tipo_comprobante_lote = Column(VARCHAR(2))
    cod_comprobante_lote = Column(VARCHAR(9))
    descuento_regalo = Column(NUMBER(14,2))
    precio_unitario_xml = Column(NUMBER(18,6))
    descuento_xml = Column(NUMBER(14,2))
    precio_total_sin_impuesto_xml = Column(NUMBER(14,2))
    iva_xml = Column(NUMBER(14,2))
    ice_xml = Column(NUMBER(14,2))
    base_imponible_iva = Column(NUMBER(14,2))
    base_imponible_ice = Column(NUMBER(14,2))
    cod_producto_xml = Column(NUMBER(14))
    cod_porcentaje_iva = Column(NUMBER(1))
    @classmethod
    def query(cls):
        return db.session.query(cls)

