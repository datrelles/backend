# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Index, VARCHAR
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.orm import relationship,deferred
from sqlalchemy.ext.declarative import declarative_base
from config.database import db
from models.users import Empresa

Base = declarative_base(metadata = db.metadata)
#metadata = Base.metadata


class AdParametrosReport(Base):
    __tablename__ = 'ad_parametros_report'
    __table_args__ = {'schema': 'jaher'}

    cod_servidor = Column(NUMBER(2, 0, False), primary_key=True)
    servidor = Column(VARCHAR(100), nullable=False)
    puerto = Column(NUMBER(6, 0, False), nullable=False)


class Document(Base):
    __tablename__ = 'document'
    __table_args__ = {'schema': 'computo'}

    forma = Column(VARCHAR(8), primary_key=True)
    descripcion = Column(VARCHAR(60), nullable=False)
    departamento = Column(VARCHAR(12), nullable=False)
    fecha = Column(DateTime, nullable=False)
    usuario_final = Column(VARCHAR(20), nullable=False)
    estado = Column(VARCHAR(1))
    programador = Column(VARCHAR(3))
    menu = Column(VARCHAR(40))
    horas = Column(NUMBER(5, 2, True))
    documentado = Column(VARCHAR(1))
    tipo_modulo = Column(VARCHAR(1), nullable=False)
    consulta_inicio = Column(VARCHAR(1))
    orientacion = Column(VARCHAR(1))
    cod_sistema = Column(VARCHAR(3))
    cod_servidor = Column(ForeignKey('jaher.ad_parametros_report.cod_servidor'))

    ad_parametros_report = relationship('AdParametrosReport')


class TipoComprobante(Base):
    __tablename__ = 'tipo_comprobante'
    __table_args__ = (
        Index('tipo_comprobante_01_idx', 'tipo', 'empresa'),
        {'schema': 'contabilidad'}
    )

    empresa = Column(ForeignKey('computo.empresa.empresa'), primary_key=True, nullable=False, index=True)
    tipo = Column(VARCHAR(2), primary_key=True, nullable=False)
    nombre = Column(VARCHAR(40))
    tsc = Column(VARCHAR(1))
    titulo_impresion_1 = Column(VARCHAR(40))
    titulo_impresion_2 = Column(VARCHAR(40))
    titulo_impresion_3 = Column(VARCHAR(40))
    titulo_impresion_4 = Column(VARCHAR(40))
    cod_sistema = Column(VARCHAR(3))
    cod_parametro = Column(VARCHAR(2))
    forma = Column(ForeignKey('computo.document.forma'))
    tiene_cheque = Column(VARCHAR(1))

    empresa1 =  deferred(relationship(Empresa, backref = 'TipoComprobante'))
    document =  deferred(relationship(Document, backref = 'Document'))

    @classmethod
    def query(cls):
        return db.session.query(cls)
