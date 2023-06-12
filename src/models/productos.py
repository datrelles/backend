# coding: utf-8
from sqlalchemy import Column, DateTime, Index, VARCHAR, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from config.database import db

Base = declarative_base(metadata = db.metadata)

class Marca(Base):
    __tablename__ = 'marca'
    __table_args__ = {'schema': 'stock'}

    cod_marca = Column(NUMBER(3, 0, False), primary_key=True, nullable=False, index=True)
    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    nombre = Column(VARCHAR(50), nullable=False)
    descuento_promocion = Column(VARCHAR(1))


class Unidad(Base):
    __tablename__ = 'unidad'
    __table_args__ = {'schema': 'stock'}

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_unidad = Column(VARCHAR(8), primary_key=True, nullable=False)
    nombre = Column(VARCHAR(30), nullable=False)


class Producto(Base):
    __tablename__ = 'producto'
    __table_args__ = (
        Index('producto$nombre', 'nombre', 'empresa'),
        Index('producto_02_idx', 'empresa', 'cod_producto_modelo'),
        Index('producto$barra', 'cod_barra', 'empresa'),
        Index('producto_03_idx', 'empresa', 'es_grupo_modelo'),
        Index('producto_01_idx', 'empresa', 'serie', 'cod_producto', 'cod_unidad'),
        Index('producto$marca', 'cod_marca', 'empresa'),
        {'schema': 'stock'}
    )

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_producto = Column(VARCHAR(14), primary_key=True, nullable=False)
    tipo_inventario = Column(VARCHAR(1), nullable=False)
    cod_marca = Column(NUMBER(3, 0, False), nullable=False)
    cod_unidad = Column(VARCHAR(8), nullable=False)
    cod_alterno = Column(VARCHAR(14))
    nombre = Column(VARCHAR(200), nullable=False)
    cod_barra = Column(VARCHAR(13))
    useridc = Column(VARCHAR(3), nullable=False)
    niv_cod_nivel = Column(VARCHAR(8), nullable=False)
    niv_secuencia = Column(VARCHAR(6), nullable=False)
    niv_cat_emp_empresa = Column(VARCHAR(2), nullable=False)
    niv_cat_cod_categoria = Column(VARCHAR(2), nullable=False)
    promedio = Column(NUMBER(12, 2, True), nullable=False)
    presentacion = Column(VARCHAR(8))
    volumen = Column(NUMBER(8, 2, True))
    grado = Column(NUMBER(2, 0, False))
    iva = Column(VARCHAR(1), nullable=False, server_default=text("'S' "))
    referencia = Column(VARCHAR(200))
    partida = Column(VARCHAR(10))
    minimo = Column(NUMBER(12, 2, True))
    maximo = Column(NUMBER(12, 2, True))
    costo = Column(NUMBER(12, 2, True))
    dolar = Column(NUMBER(8, 2, True))
    activo = Column(VARCHAR(1), nullable=False)
    alcohol = Column(VARCHAR(1))
    cod_unidad_r = Column(VARCHAR(8))
    cod_modelo = Column(VARCHAR(8), nullable=False)
    cod_item = Column(VARCHAR(3), nullable=False)
    es_fabricado = Column(VARCHAR(1), nullable=False)
    cod_modelo_cat = Column(VARCHAR(8))
    cod_item_cat = Column(VARCHAR(3))
    cod_unidad_f = Column(VARCHAR(8))
    cantidad = Column(NUMBER(14, 2, True))
    cantidad_i = Column(NUMBER(14, 2, True))
    serie = Column(VARCHAR(1))
    es_express = Column(NUMBER(1, 0, False))
    precio = Column(NUMBER(14, 2, True))
    cod_modelo_cat1 = Column(VARCHAR(8))
    cod_item_cat1 = Column(VARCHAR(3))
    ice = Column(VARCHAR(1), server_default=text("'S'"))
    control_lote = Column(VARCHAR(1), nullable=False, server_default=text("'N' "))
    es_grupo_modelo = Column(NUMBER(1, 0, False), nullable=False, server_default=text("0 "), comment='1 = AGRUPA EN UN MODELO VARIOS CODIGOS DE PRODUCTOS ; 0=NO AGRUPA')
    cod_producto_modelo = Column(VARCHAR(14), comment='CODIGO DEL PRODUCTO QUE AGRUPA UN MISMO MODELO')

    @classmethod
    def query(cls):
        return db.session.query(cls)