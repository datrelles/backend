from sqlalchemy import Column, DateTime, Index, VARCHAR, text, CHAR, Float
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

Base = declarative_base(metadata = db.metadata)

class tc_doc_elec_recibidos(Base):
    __tablename__ = 'tc_doc_elec_recibidos'
    __table_args__ = (
        Index("RUC_COMPROBANTE","ruc_emisor", "serie_comprobante"),
        {'schema': 'contabilidad'}
    )
    ruc_emisor = Column(VARCHAR(13), primary_key=True, nullable=False)
    serie_comprobante = Column(VARCHAR(50), primary_key=True, nullable=False)
    comprobante = Column(VARCHAR(50))
    razon_social_emisor = Column(VARCHAR(255))
    fecha_emision = Column(DateTime)
    fecha_autorizacion = Column(DateTime)
    tipo_emision = Column(VARCHAR(50))
    numero_documento_modificado = Column(VARCHAR(50))
    identificacion_receptor = Column(VARCHAR(13))
    clave_acceso = Column(VARCHAR(100))
    numero_autorizacion = Column(VARCHAR(100))
    importe_total = Column(Float)
    iva = Column(Float)
    valor_sin_impuestos = Column(Float)
    @classmethod
    def query(cls):
        return db.session.query(cls)


class vc_opago(Base):
    __tablename__ = 'vc_opago'
    __table_args__ = {'schema': 'contabilidad'}

    # Ejemplo de mapeo. Ajustar longitudes/tipos de columna según tu BD.
    es_pagado = Column(NUMBER, nullable=True)
    empresa = Column(VARCHAR(50), primary_key=True)          # o ajusta el primary_key según requieras
    cod_opago = Column(VARCHAR(50), primary_key=True)
    secuencia = Column(NUMBER, primary_key=True)
    saldo = Column(Float)
    cod_categoria_gas = Column(VARCHAR(50))
    ruc = Column(VARCHAR(13))
    beneficiario = Column(VARCHAR(255))
    es_anulado = Column(VARCHAR(1))
    factura_manual = Column(VARCHAR(50))

    fecha_factura = Column(DateTime)     # Proviene de NVL(NVL(NVL(D.FECHA_EMISION,a.fecha_factura), V.FECHA_FACTURA), L.FECHA)
    vencimiento = Column(DateTime)
    fecha_apr = Column(DateTime)
    fecha_reg = Column(DateTime)
    fecha_pag = Column(DateTime)

    cod_tipo_comprobante_co = Column(VARCHAR(50))
    cod_comprobante_co = Column(VARCHAR(50))
    cod_agencia = Column(VARCHAR(50))
    cod_tipo_comprobante_pa = Column(VARCHAR(50))
    cod_comprobante_pa = Column(VARCHAR(50))
    concepto = Column(VARCHAR(1000))

    es_sugerido = Column(NUMBER)
    razon_sugerido = Column(VARCHAR(255))
    es_aprobado = Column(NUMBER)
    fecha_aprueba_pago = Column(DateTime)
    usuario_aprueba_pago = Column(VARCHAR(50))

    fecha_revision = Column(DateTime)
    useridc_revisado = Column(VARCHAR(50))  # c.revisado_por
    cod_comprobante_ret = Column(VARCHAR(50))

    valor_pago = Column(Float)  # nvl(a.base0,0)+nvl(a.base12,0)+...

    cod_comprobantes_pago = Column(VARCHAR(2000))  # Subquery concatenado, ajusta el tamaño
    useridc_reg = Column(VARCHAR(50))   # u_reg.usuario_oracle
    useridc_apr = Column(VARCHAR(50))   # u_apr.usuario_oracle
    useridc_pag = Column(VARCHAR(50))   # u_pag.usuario_oracle

    es_revisado = Column(NUMBER)        # decode(...)
    es_registrado = Column(NUMBER)      # decode(...)
    comprobante_cabecera = Column(VARCHAR(50))
    tipo_comprobante = Column(NUMBER)

    @classmethod
    def query(cls):
        return db.session.query(cls)
