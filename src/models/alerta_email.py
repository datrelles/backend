from sqlalchemy import Column, VARCHAR, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db
from sqlalchemy.dialects.oracle import NUMBER

Base = declarative_base(metadata=db.metadata)

class alerta_email(Base):
    __tablename__ = 'ALERTA_EMAIL'
    __table_args__ = (
        {'schema': 'stock'},
    )

    cod_alerta = Column(VARCHAR(20), nullable=False, primary_key=True)
    empresa = Column(NUMBER(2), primary_key=True, nullable=False)
    usuario_oracle = Column(VARCHAR(100), ForeignKey('computo.usuario.usuario_oracle'), nullable=True)
    email = Column(VARCHAR(255), nullable=True)
    rol = Column(VARCHAR(50), nullable=False, primary_key=True)

    @classmethod
    def query(cls):
        return db.session.query(cls)

class alerta_dias(Base):
    __tablename__ = 'ALERTA_DIAS'
    __table_args__ = (
        {'schema': 'stock'},
    )

    cod_alerta = Column(VARCHAR(20), ForeignKey('stock.alerta_email.cod_alerta'), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2), ForeignKey('stock.alerta_email.empresa'), primary_key=True, nullable=False)
    rol = Column(VARCHAR(50), ForeignKey('stock.alerta_email.rol'), primary_key=True, nullable=False)
    dia = Column(NUMBER(2), primary_key=True, nullable=False)
    hora_inicio = Column(NUMBER(2), primary_key=True, nullable=False)
    hora_final = Column(NUMBER(2), nullable=True)

    @classmethod
    def query(cls):
        return db.session.query(cls)

class alerta_email_type(Base):
    __tablename__ = 'ALERTA_EMAIL_TYPE'
    __table_args__ = (
        {'schema': 'stock'},
    )

    cod_alerta = Column(VARCHAR(20), primary_key=True, nullable=False)
    empresa = Column(NUMBER(2), primary_key=True, nullable=False)
    info = Column(VARCHAR(200), nullable=True)

    @classmethod
    def query(cls):
        return db.session.query(cls)



