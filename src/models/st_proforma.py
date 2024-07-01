from sqlalchemy import Column, DateTime, Index, VARCHAR, text, ForeignKey
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

Base = declarative_base(metadata=db.metadata)

class st_proforma(Base):
    __tablename__ = 'st_proforma'
    __table_args__ = (
        Index('IDX_PROFOR_AGENCIA', 'empresa', 'cod_agencia'),
        Index('IDX_PROFOR_CLI_USU_VER_CAM_A', 'usuario_ver_campo'),
        Index('IDX_PROFOR_CLI_USU_VER_CAM_S', 'usuario_sol_ver_campo'),
        Index('IDX_PROFOR_CLI_USU_VER_TEL_A', 'usuario_ver_telefonica'),
        Index('IDX_PROFOR_CLI_USU_VER_TEL_S', 'usuario_sol_ver_telefonica'),
        Index('IDX_PROFOR_DIVISA', 'cod_divisa'),
        Index('IDX_PROFOR_FORMA_PAGO', 'empresa', 'cod_forma_pago'),
        Index('IDX_PROFOR_LIQUIDACION', 'empresa', 'cod_liquidacion'),
        Index('IDX_PROFORMA_COMPROBANTE_VERIF', 'cod_comprobante_ver', 'tipo_comprobante_ver', 'empresa'),
        Index('IDX_PROFORMA_POLCRE', 'cod_politica', 'empresa'),
        Index('IDX_PROFORMA_TARCRE', 'empresa', 'cod_tarjeta'),
        Index('IDX_PROFORMA_TIPO_COMP2', 'empresa', 'tipo_comprobante_factura'),
        Index('IDX_PROFOR_PERSONA_CLI', 'empresa', 'cod_tipo_persona', 'cod_persona'),
        Index('IDX_PROFOR_PERSONA_GAR', 'empresa', 'cod_tipo_persona_gar', 'cod_persona_gar'),
        Index('IDX_PROFOR_TIPO_COMPROBANTE', 'empresa', 'tipo_comprobante'),
        Index('IDX_PROFOR_TIPO_IDEN_CLI', 'cod_tipo_identificacion', 'empresa'),
        Index('IDX_PROFOR_TIPO_IDEN_GAR', 'cod_tipo_identificacion_gar', 'empresa'),
        {'schema': 'stock'}
    )

    cod_comprobante = Column(VARCHAR(9), primary_key=True, nullable=False)
    tipo_comprobante = Column(VARCHAR(2), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_agencia = Column(NUMBER(4))
    fecha = Column(DateTime)
    cod_forma_pago = Column(VARCHAR(3))
    comprobante_manual = Column(VARCHAR(9))
    cod_liquidacion = Column(VARCHAR(9))
    cod_divisa = Column(VARCHAR(20))
    cod_tipo_identificacion = Column(NUMBER(2))
    cod_tipo_persona = Column(VARCHAR(3))
    cod_persona = Column(VARCHAR(14))
    cod_tipo_persona_age = Column(VARCHAR(3))
    cod_persona_age = Column(VARCHAR(14))
    cod_tipo_identificacion_gar = Column(NUMBER(2))
    cod_tipo_persona_gar = Column(VARCHAR(3))
    cod_persona_gar = Column(VARCHAR(14))
    num_cuotas = Column(NUMBER(2))
    num_cuotas_gratis = Column(NUMBER(2))
    dias_validez = Column(NUMBER(2))
    entrada = Column(NUMBER(14, 2))
    otros = Column(NUMBER(14, 2))
    descuento = Column(NUMBER(14, 2))
    iva = Column(NUMBER(14, 2))
    financiamiento = Column(NUMBER(14, 2))
    valor = Column(NUMBER(14, 2))
    es_anulado = Column(NUMBER(1))
    es_invalido = Column(NUMBER(1))
    es_facturado = Column(NUMBER(1))
    es_aprobado = Column(NUMBER(1))
    useridc = Column(VARCHAR(3))
    descuento_usuario = Column(NUMBER(14, 2))
    useridc_autoriza_descuento = Column(VARCHAR(3))
    cod_bodega_ingreso = Column(NUMBER(4))
    cod_subbodega_ingreso = Column(NUMBER(3))
    cod_bodega_egreso = Column(NUMBER(4))
    cod_subbodega_egreso = Column(NUMBER(4))
    cantidad_mov = Column(NUMBER(4), default=0)
    cantidad_mov_completo = Column(NUMBER(4), default=0)
    cod_tarjeta = Column(VARCHAR(3))
    num_tarjeta = Column(VARCHAR(30))
    num_recap = Column(VARCHAR(15))
    num_voucher = Column(VARCHAR(15))
    num_autorizacion = Column(VARCHAR(15))
    cod_politica = Column(NUMBER(2))
    rebate = Column(NUMBER(14, 2))
    tipo_comprobante_factura = Column(VARCHAR(2))
    nombre_persona = Column(VARCHAR(50))
    fecha_vencimiento1 = Column(DateTime)
    por_interes = Column(NUMBER(7, 4))
    num_poliza = Column(VARCHAR(20))
    num_cupon = Column(VARCHAR(20))
    base_imponible = Column(NUMBER(14, 2))
    base_excenta = Column(NUMBER(14, 2))
    tipo_comprobante_ver = Column(VARCHAR(2))
    cod_comprobante_ver = Column(VARCHAR(9))
    cod_comprobante_ref = Column(VARCHAR(13))
    cod_tipo_comprobante_ref = Column(VARCHAR(2))
    cod_comprobante_convenio = Column(NUMBER(8))
    es_verificado = Column(NUMBER(1), server_default=text("0"))
    fecha_sol_ver_telefonica = Column(DateTime)
    usuario_sol_ver_telefonica = Column(VARCHAR(20))
    fecha_ver_telefonica = Column(DateTime)
    usuario_ver_telefonica = Column(VARCHAR(20))
    fecha_sol_ver_campo = Column(DateTime)
    usuario_sol_ver_campo = Column(VARCHAR(20))
    fecha_ver_campo = Column(DateTime)
    usuario_ver_campo = Column(VARCHAR(20))
    fecha_negacion = Column(DateTime)
    porcentaje_aumento = Column(NUMBER(5, 2))
    usuario_autoriza_por = Column(VARCHAR(20))
    es_detenido = Column(NUMBER(1))
    es_banco = Column(NUMBER(1))
    ice = Column(NUMBER(14, 2))

    @classmethod
    def query(cls):
        return db.session.query(cls)

class st_proforma_movimiento(Base):
    __tablename__ = 'st_proforma_movimiento'
    __table_args__ = (
        Index('IDX_PROFOR_MOV_ESTADO', 'cod_estado_producto', 'empresa'),
        Index('IDX_PROFOR_PRODUCTO', 'empresa', 'cod_producto'),
        Index('IDX_PROFOR_PROFORMA', 'cod_comprobante', 'tipo_comprobante', 'empresa'),
        Index('IDX_PROFOR_UNIDAD_PRODUCTO', 'empresa', 'cod_producto', 'cod_unidad'),
        Index('IND_PROFORMA_M_GAR', 'cod_producto_gar', 'empresa'),
        Index('XIF34ST_PROFORMA_MOVIMIENTO', 'cod_producto', 'cod_unidad', 'empresa'),
        {'schema': 'stock'}
    )

    cod_comprobante = Column(VARCHAR(9), primary_key=True, nullable=False)
    tipo_comprobante = Column(VARCHAR(2), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    secuencia = Column(NUMBER(4), primary_key=True, nullable=False)
    cod_producto = Column(VARCHAR(14), nullable=False)
    cod_unidad = Column(VARCHAR(8), nullable=False)
    es_serie = Column(NUMBER(1), nullable=False)
    cod_estado_producto = Column(VARCHAR(2), nullable=False)
    cantidad = Column(NUMBER(14, 2), nullable=False)
    cantidad_serie = Column(NUMBER(4), default=0, nullable=False)
    precio_lista = Column(NUMBER(14, 2), nullable=False)
    costo = Column(NUMBER(14, 2), nullable=False)
    precio = Column(NUMBER(14, 2), nullable=False)
    descuento = Column(NUMBER(14, 2), nullable=False)
    iva = Column(NUMBER(14, 2), nullable=False)
    financiamiento = Column(NUMBER(14, 2), nullable=False)
    valor = Column(NUMBER(14, 2), nullable=False)
    rebate = Column(NUMBER(14, 2))
    por_descuento = Column(NUMBER(10, 6))
    por_max_descuento = Column(NUMBER(10, 6))
    es_iva = Column(NUMBER(1), default=1)
    aplica_promocion = Column(NUMBER(1))
    rebate_promocion = Column(NUMBER(14, 2))
    por_descuento_promocion = Column(NUMBER(10, 6))
    cantidad_despacho = Column(NUMBER(14, 2))
    tipo_promocion = Column(VARCHAR(1))
    num_cupon = Column(VARCHAR(20))
    cod_promocion = Column(NUMBER(4))
    ice = Column(NUMBER(14, 2))
    codigo_combo = Column(NUMBER(4))
    cantidad_promocion = Column(NUMBER(14, 2))
    tipo_comprobante_lote = Column(VARCHAR(2))
    cod_comprobante_lote = Column(VARCHAR(9))
    por_descuento_producto = Column(NUMBER(10, 6), comment='% DESCUENTO POR PRODUCTO DE OTROS')
    descuento_producto = Column(NUMBER(14, 2), comment='DESCUENTO POR PRODUCTO DE OTROS')
    es_regalo = Column(NUMBER(1))
    descuento_detalle = Column(NUMBER(14, 2))
    precio_unitario_xml = Column(NUMBER(18, 6))
    descuento_xml = Column(NUMBER(14, 2))
    precio_total_sin_impuesto_xml = Column(NUMBER(14, 2))
    iva_xml = Column(NUMBER(14, 2))
    ice_xml = Column(NUMBER(14, 2))
    base_imponible_iva = Column(NUMBER(14, 2))
    base_imponible_ice = Column(NUMBER(14, 2))
    costo_promo = Column(NUMBER(14, 2))
    cod_producto_xml = Column(VARCHAR(14))
    cod_porcentaje_iva = Column(NUMBER(1), comment='0=TARIFA 0%; 2=12%; 6=NO OBJETO IVA ; 7=EXCENTO IVA')
    cod_producto_gar = Column(VARCHAR(14))
    secuencia_factura = Column(NUMBER(4))
    secuencia_factura_m = Column(NUMBER(4))

    @classmethod
    def query(cls):
        return db.session.query(cls)

class st_cab_datafast(Base):
    __tablename__ = 'st_cab_datafast'
    __table_args__ = {'schema': 'stock'}

    empresa = Column(NUMBER(2), nullable=False)
    id_transaction = Column(VARCHAR(255), primary_key=True, nullable=False)
    payment_type = Column(VARCHAR(10))
    payment_brand = Column(VARCHAR(40))
    total = Column(NUMBER(10, 2))
    sub_total = Column(NUMBER(10, 2))
    discount_percentage = Column(NUMBER(10, 2))
    discount_amount = Column(NUMBER(10, 2))
    currency = Column(VARCHAR(3))
    batch_no = Column(VARCHAR(10))
    id_guia_servientrega = Column(VARCHAR(255))
    card_type = Column(VARCHAR(10))
    bin_card = Column(VARCHAR(6))
    last_4_digits = Column(VARCHAR(4))
    holder = Column(VARCHAR(100))
    expiry_month = Column(VARCHAR(2))
    expiry_year = Column(VARCHAR(4))
    acquirer_code = Column(VARCHAR(20))
    client_type_id = Column(VARCHAR(2))
    client_name = Column(VARCHAR(100))
    client_last_name = Column(VARCHAR(100))
    client_id = Column(VARCHAR(20))
    client_address = Column(VARCHAR(255))
    cost_shiping_calculate = Column(NUMBER(10, 2))
    shiping_discount = Column(NUMBER(10, 2))
    cod_orden_ecommerce = Column(VARCHAR(24))
    cod_comprobante = Column(VARCHAR(24))
    fecha = Column(DateTime, nullable=False)

    @classmethod
    def query(cls):
        return db.session.query(cls)

class st_det_datafast(Base):
    __tablename__ = 'st_det_datafast'
    __table_args__ = {'schema': 'stock'}

    empresa = Column(NUMBER(2), primary_key=True, nullable=False)
    id_transaction = Column(VARCHAR(32), ForeignKey('stock.st_cab_datafast.id_transaction'), primary_key=True, nullable=False)
    cod_producto = Column(VARCHAR(20), primary_key=True, nullable=False)
    price = Column(NUMBER(10, 2))
    quantity = Column(NUMBER(10))
    @classmethod
    def query(cls):
        return db.session.query(cls)

class st_cab_deuna(Base):
    __tablename__ = 'st_cab_deuna'
    __table_args__ = {'schema': 'stock'}

    empresa = Column(NUMBER(2), primary_key=True, nullable=False)
    id_transaction = Column(VARCHAR(255), primary_key=True, nullable=False)
    internal_transaction_reference = Column(VARCHAR(255))
    amount = Column(NUMBER(10, 2))
    currency = Column(VARCHAR(3))
    id_guia_servientrega = Column(VARCHAR(255))
    client_type_id = Column(VARCHAR(2))
    client_name = Column(VARCHAR(100))
    client_last_name = Column(VARCHAR(100))
    client_id = Column(VARCHAR(20))
    client_address = Column(VARCHAR(255))
    cost_shiping = Column(NUMBER(10, 2))
    cod_orden_ecommerce = Column(VARCHAR(24))
    cod_comprobante = Column(VARCHAR(24))
    fecha = Column(DateTime)

    @classmethod
    def query(cls):
        return db.session.query(cls)

class st_det_deuna(Base):
    __tablename__ = 'st_det_deuna'
    __table_args__ = {'schema': 'stock'}

    empresa = Column(NUMBER(2), primary_key=True, nullable=False)
    id_transaction = Column(VARCHAR(32), ForeignKey('stock.st_cab_deuna.id_transaction'), primary_key=True, nullable=False)
    code = Column(VARCHAR(20), primary_key=True, nullable=False)
    quantity = Column(NUMBER(10))

    @classmethod
    def query(cls):
        return db.session.query(cls)