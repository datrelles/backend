# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Index, VARCHAR, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

Base = declarative_base(metadata = db.metadata)


class StColor(Base):
    __tablename__ = 'st_color'
    __table_args__ = {'schema': 'stock'}

    cod_color = Column(VARCHAR(3), primary_key=True)
    nombre = Column(VARCHAR(20), nullable=False)


class StProductoDespiece(Base):
    __tablename__ = 'st_producto_despiece'
    __table_args__ = (
        Index('ind$_prod_col_des_desp_d', 'cod_despiece', 'secuencia', 'empresa'),
        Index('ind$_prod_desp_producto', 'empresa', 'cod_producto'),
        {'schema': 'stock'}
    )

    cod_despiece = Column(VARCHAR(20), primary_key=True, nullable=False)
    secuencia = Column(NUMBER(5, 1, True), primary_key=True, nullable=False)
    cod_color = Column(ForeignKey('stock.st_color.cod_color'), primary_key=True, nullable=False, index=True)
    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_producto = Column(VARCHAR(14), nullable=False)
    fecha_creacion = Column(DateTime, server_default=text("""\
SYSDATE
"""))
    creado_por = Column(VARCHAR(30), server_default=text("""\
USER
"""))

    st_color = relationship('StColor')

    @classmethod
    def query(cls):
        return db.session.query(cls)
