from sqlalchemy import Column, DateTime, Index, VARCHAR, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship,deferred
from src.config.database import db

Base = declarative_base(metadata = db.metadata)
class Cliente(Base):
    __tablename__ = 'cliente'

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_cliente = Column(VARCHAR(14), primary_key=True, nullable=False)
    cod_tipo_identificacion = Column(NUMBER(2))
    nombre = Column(VARCHAR(100), nullable=False)
    apellido1 = Column(VARCHAR(100), nullable=False)
    ruc = Column(VARCHAR(13))
    @classmethod
    def query(cls):
        return db.session.query(cls)