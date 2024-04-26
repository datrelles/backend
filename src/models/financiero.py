from sqlalchemy import Column, DateTime, ForeignKey, Index, VARCHAR
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.orm import relationship,deferred
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db
from src.models.users import Empresa

Base = declarative_base(metadata = db.metadata)

class StFinCabCredito(Base):
    __tablename__ = 'st_fin_cab_credito'
    __table_args__ = (
        Index('IDX_FIN_CAB_CRED_EMPRESA', 'empresa'),
        Index('IDX_FIN_CAB_CRED_FIN_CLIENTE', 'empresa', 'id_cliente'),
        Index('IDX_FIN_CAB_CRED_TG_MOD_ITEM', 'empresa', 'cod_modelo', 'cod_item'),
        Index('IDX_FIN_CAB_CRED_TIPO_COMP', 'empresa', 'tipo_comprobante'),
        Index('IDX_FIN_CAB_CRED_USUARIO', 'usuario_crea'),
        Index('PK_FIN_CAB_CREDITO', 'empresa', 'cod_comprobante', 'tipo_comprobante', 'nro_operacion'),
        {'schema': 'stock'}
    )

    empresa = Column(NUMBER(2), primary_key=True, nullable=False)
    cod_comprobante = Column(VARCHAR(9), primary_key=True, nullable=False)
    tipo_comprobante = Column(VARCHAR(2), primary_key=True, nullable=False)
    nro_operacion = Column(VARCHAR(30), primary_key=True, nullable=False)
    tipo_id_cliente = Column(VARCHAR(4), nullable=False)
    id_cliente = Column(VARCHAR(30), nullable=False)
    capital_original = Column(NUMBER(14,5))
    saldo_capital = Column(NUMBER(14,5))
    fecha_emision = Column(DateTime)
    fecha_vencimiento = Column(DateTime)
    plazo_credito = Column(NUMBER(10))
    tasa_interes = Column(NUMBER(14,5))
    tasa_mora = Column(NUMBER(14, 5))
    nro_cuota_total = Column(NUMBER(10))
    nro_cuotas_pagadas = Column(NUMBER(10))
    nro_cuotas_mora = Column(NUMBER(10))
    base_calculo = Column(NUMBER(14, 5))
    cod_modelo = Column(VARCHAR(8))
    cod_item = Column(VARCHAR(3))
    usuario_crea = Column(VARCHAR(20))
    fecha_crea = Column(DateTime)
    usuario_modifica = Column(VARCHAR(20))
    fecha_modifica = Column(DateTime)
    @classmethod
    def query(cls):
        return db.session.query(cls)

class StFinDetCredito(Base):
    __tablename__ = 'st_fin_det_credito'
    __table_args__ = (
        Index('IDX_FIN_DET_CRED_EMPRESA', 'empresa'),
        Index('IDX_FIN_DET_CRED_CLIENTE', 'empresa', 'id_cliente'),
        Index('IDX_FIN_DET_CRED_TIPO_COMP', 'empresa', 'tipo_comprobante'),
        Index('IDX_FIN_DET_CRED_FIN_CAB_CRED', 'empresa', 'cod_comprobante', 'tipo_comprobante', 'nro_operacion'),
        Index('IDX_FIN_DET_CRED_USUARIO', 'usuario_crea'),
        Index('PK_FIN_DET_CREDITO', 'empresa', 'cod_comprobante', 'tipo_comprobante', 'nro_operacion', 'nro_pago'),

        {'schema': 'stock'}
    )

    empresa = Column(NUMBER(2), primary_key=True, nullable=False)
    cod_comprobante = Column(VARCHAR(9), primary_key=True, nullable=False)
    tipo_comprobante = Column(VARCHAR(2), primary_key=True, nullable=False)
    nro_operacion = Column(VARCHAR(30), primary_key=True, nullable=False)
    id_cliente = Column(VARCHAR(30), nullable=False)
    nro_pago = Column(NUMBER(5), primary_key=True, nullable=False)
    fecha_inicio_cuota = Column(DateTime)
    fecha_vencimiento_cuota = Column(DateTime)
    plazo_cuota = Column(NUMBER(5))
    valor_capital = Column(NUMBER(14, 5))
    valor_interes = Column(NUMBER(14, 5))
    valor_mora = Column(NUMBER(14, 5))
    valor_cuota = Column(NUMBER(14, 5))
    estado_cuota = Column(VARCHAR(30))
    usuario_crea = Column(VARCHAR(20))
    fecha_crea = Column(DateTime)
    usuario_modifica = Column(VARCHAR(20))
    fecha_modifica = Column(DateTime)
    @classmethod
    def query(cls):
        return db.session.query(cls)

class StFinClientes(Base):
    __tablename__ = 'st_fin_clientes'
    __table_args__ = (
        Index('IDX_FIN_CLIENTES_EMPRESA', 'empresa'),
        Index('IDX_FIN_CLIENTES_USUARIO', 'usuario_crea'),
        Index('PK_FIN_CLIENTES', 'empresa', 'id_cliente'),
        {'schema': 'stock'}
    )

    empresa = Column(NUMBER(2), primary_key=True, nullable=False)
    id_cliente = Column(VARCHAR(30), primary_key=True, nullable=False)
    pais_origen = Column(VARCHAR(10))
    primer_apellido = Column(VARCHAR(200))
    segundo_apellido = Column(VARCHAR(200))
    primer_nombre = Column(VARCHAR(200))
    segundo_nombre = Column(VARCHAR(200))
    calle_principal = Column(VARCHAR(300))
    calle_secundaria = Column(VARCHAR(300))
    numero_casa = Column(VARCHAR(100))
    ciudad = Column(VARCHAR(100))
    numero_celular = Column(VARCHAR(30))
    numero_convencional = Column(VARCHAR(30))
    direccion_electronica = Column(VARCHAR(100))
    usuario_crea = Column(VARCHAR(20))
    fecha_crea = Column(DateTime)
    usuario_modifica = Column(VARCHAR(20))
    fecha_modifica = Column(DateTime)

    @classmethod
    def query(cls):
        return db.session.query(cls)

class StFinPagos(Base):
    __tablename__ = 'st_fin_pagos'
    __table_args__ = (
        Index('IDX_FIN_PAGOS_EMPRESA', 'empresa'),
        Index('IDX_FIN_PAGOS_FIN_CAB_DET', 'empresa', 'cod_comprobante', 'tipo_comprobante', 'nro_operacion', 'nro_cuota'),
        Index('IDX_FIN_PAGOS_FIN_CLIENTES', 'empresa', 'id_cliente'),
        Index('PK_FIN_PAGOS', 'empresa', 'cod_comprobante', 'tipo_comprobante', 'nro_operacion', 'nro_cuota', 'secuencia'),
        Index('IDX_FIN_PAGOS_USUARIO', 'usuario_crea'),
        {'schema': 'stock'}
    )
    empresa = Column(NUMBER(2), primary_key=True, nullable=False)
    cod_comprobante = Column(VARCHAR(9), primary_key=True, nullable=False)
    tipo_comprobante = Column(VARCHAR(2), primary_key=True, nullable=False)
    nro_operacion = Column(VARCHAR(30), primary_key=True, nullable=False)
    nro_cuota = Column(NUMBER(5), primary_key=True, nullable=False)
    secuencia = Column(NUMBER(6), primary_key=True, nullable=False)
    id_cliente = Column(VARCHAR(30), nullable=False)
    fecha_pago = Column(DateTime)
    valor_total_cuota = Column(NUMBER(14, 5))
    valor_pagado_capital = Column(NUMBER(14, 5))
    valor_pagado_interes = Column(NUMBER(14, 5))
    valor_pagado_mora = Column(NUMBER(14, 5))
    fecha_registro = Column(DateTime)
    usuario_crea = Column(VARCHAR(20))
    fecha_crea = Column(DateTime)
    usuario_modifica = Column(VARCHAR(20))
    fecha_modifica = Column(DateTime)

    @classmethod
    def query(cls):
        return db.session.query(cls)