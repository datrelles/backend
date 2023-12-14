from sqlalchemy import Column, DateTime, Index, VARCHAR, text, CHAR, Float
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

Base = declarative_base(metadata = db.metadata)

class tc_doc_elec_recibidos(Base):
    __tablename__ = 'tc_doc_elec_recibidos'
    __table_args__ = (
        Index("RUC_COMPROBANTE","ruc_emisor", "serie_comprobante"),
        {'schema': 'computo'}
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

    @classmethod
    def query(cls):
        return db.session.query(cls)

