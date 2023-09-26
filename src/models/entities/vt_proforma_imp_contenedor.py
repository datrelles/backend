from sqlalchemy import Column, VARCHAR
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db


Base = declarative_base(metadata = db.metadata)

class VtProformaImpContenedor(Base):
    __tablename__ = 'vt_proforma_imp_contenedor'
    __table_args__ = {'schema': 'stock'}

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    tipo_proforma = Column(VARCHAR(5), primary_key=True, nullable=False)
    cod_proforma = Column(VARCHAR(10), primary_key=True, nullable=False)
    secuencia = Column(NUMBER(4), primary_key=True, nullable=False)
    secuencia_prof = Column(NUMBER(4), primary_key=True, nullable=False)

    @classmethod
    def query(cls):
        return db.session.query(cls)