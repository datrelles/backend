from sqlalchemy import Column, VARCHAR, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

Base = declarative_base(metadata=db.metadata)

class alert_email(Base):
    __tablename__ = 'ALERTA_EMAIL'
    __table_args__ = (
        {'schema': 'stock'},
    )

    cod_alerta = Column(VARCHAR(20))
    empresa = Column(VARCHAR(100), primary_key=True, nullable=False)
    usuario_oracle = Column(VARCHAR(100), primary_key=True, nullable=False)
    email = Column(VARCHAR(255))

    @classmethod
    def query(cls):
        return db.session.query(cls)
