from sqlalchemy import Column, DateTime, Index, VARCHAR, text, CHAR
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

Base = declarative_base(metadata = db.metadata)

class StPuertosEmbarque(Base):
    __tablename__ = 'st_puertos_embarque'
    __table_args__ = {'schema': 'stock'}

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_puerto = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    descripcion = Column(VARCHAR(100))

    @classmethod
    def query(cls):
        return db.session.query(cls)

