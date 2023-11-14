# coding: utf-8
from sqlalchemy import Column, DateTime, VARCHAR, text, Index, TIMESTAMP
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

Base = declarative_base(metadata = db.metadata)

class TiOpenAuthorization(Base):
    __tablename__ = 'ti_open_authorization'
    __table_args__ = (
        Index('PK_TI_OAUTH', 'usuario_oracle'),
        {'schema': 'computo'}
    )

    usuario_oracle = Column(VARCHAR(20), primary_key=True)
    email = Column(VARCHAR(300), nullable=False)
    cuenta_whatsapp = Column(VARCHAR(200))
    nro_whatsapp = Column(VARCHAR(15))
    ip_autentica = Column(VARCHAR(15))
    fecha_registro = Column(TIMESTAMP, primary_key=True)
    nombre_host = Column(VARCHAR(50))
    token = Column(VARCHAR(7))
    valida = Column(NUMBER(1, 0, False), nullable=False)
    mantiene_sesion = Column(NUMBER(1, 0, False), nullable=False)
    navegador_so = Column(VARCHAR(100))

    @classmethod
    def query(cls):
        return db.session.query(cls)
