from sqlalchemy import Column, DateTime, Index, VARCHAR, NVARCHAR, text, CHAR,Float, Unicode, ForeignKey
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db
Base = declarative_base(metadata=db.metadata)

class st_despiece(Base):
    __tablename__ = 'ST_DESPIECE'
    __table_args__ = (
        Index('IDX_DESPIECE_MARCA', 'empresa', 'cod_marca'),
        Index('IND_DESPICE_NIVEL', 'nivel'),
        Index('IND_DESPICE_PADRE', 'cod_despiece_padre', 'empresa'),
        {'schema': 'stock'}
    )
    cod_despiece = Column(VARCHAR(20), primary_key=True)
    empresa = Column(NUMBER(2), primary_key=True)
    nombre_c = Column(VARCHAR(200), nullable=False)
    nombre_i = Column(VARCHAR(200), nullable=False)
    nombre_e = Column(VARCHAR(200), nullable=False)
    nivel = Column(NUMBER(1), nullable=False)
    cod_despiece_padre = Column(VARCHAR(20), nullable=True)
    cod_despice_d = Column(VARCHAR(20))
    nombre_imagen = Column(VARCHAR(50))
    cod_marca = Column(NUMBER(3))
    @classmethod
    def query(cls):
        return db.session.query(cls)

class st_producto_despiece(Base):
    __tablename__ = 'ST_PRODUCTO_DESPIECE'
    __table_args__ = (
        Index('IND_PROD_COL_DES_DESP_D', 'cod_despiece', 'secuencia', 'empresa'),
        Index('IND_PROD_DESP_COLOR', 'cod_color'),
        Index('IND_PROD_DESP_PRODUCTO', 'empresa', 'cod_producto'),
        {'schema': 'stock'}
    )

    cod_despiece = Column(VARCHAR(20), primary_key=True)
    secuencia = Column(NUMBER(precision=5, scale=1), primary_key=True)
    cod_color = Column(VARCHAR(3), primary_key=True)
    empresa = Column(NUMBER(2), primary_key=True)
    cod_producto = Column(VARCHAR(14), nullable=False)
    fecha_creacion = Column(DateTime, server_default='SYSDATE')
    creado_por = Column(VARCHAR(30), server_default='USER')

    @classmethod
    def query(cls):
        return db.session.query(cls)


class st_producto_rep_anio(Base):
    __tablename__ = 'ST_PRODUCTO_REP_ANIO'
    __table_args__ = (
        Index("PK_EMPRESA_PRODUCTO", "empresa", "cod_producto"),
        {'schema': 'stock'}
    )
    empresa = Column(NUMBER(2), nullable=False)
    anio_desde = Column(NUMBER(5), nullable=False)
    anio_hasta = Column(NUMBER(5), nullable=False)
    es_activo = Column(VARCHAR(1), default='1', nullable=False)
    usuario_crea = Column(VARCHAR(20))
    fecha_crea = Column(DateTime)
    usuario_modifica = Column(VARCHAR(20))
    fecha_modificacion = Column(DateTime)
    cod_producto = Column(VARCHAR(14), nullable=False, primary_key=True)
    @classmethod
    def query(cls):
        return db.session.query(cls)

class st_modelo_crecimiento_bi(Base):
    __tablename__ = 'ST_MODELO_CRECIMIENTO_BI'
    __table_args__ = (
        Index("FK_MOD_CRE_BI_DESPIEC", "cod_despiece", "empresa"),
        Index("PK_MOD_CRE_BI", "empresa", "cod_modelo", "periodo"),
        {'schema': 'stock'}
    )

    empresa = Column(NUMBER(precision=2, scale=0), primary_key=True, nullable=False)
    cod_modelo = Column(VARCHAR(14), primary_key=True, nullable=False)
    valor = Column(NUMBER(precision=5, scale=0))
    periodo = Column(NUMBER(precision=4, scale=0), primary_key=True, nullable=False)
    cod_despiece = Column(VARCHAR(20), ForeignKey('stock.ST_DESPIECE.cod_despiece'), nullable=False)
    nivel = Column(NUMBER(precision=1, scale=0), default=3, nullable=False)
    anio = Column(NUMBER(precision=4, scale=0))


    @classmethod
    def query(cls):
        return db.session.query(cls)