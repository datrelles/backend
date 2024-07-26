# coding: utf-8
from sqlalchemy import Column, DateTime, Index, VARCHAR, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

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
class st_gen_lista_precio(Base):
    __tablename__ = 'st_gen_lista_precio'
    __table_args__ = {'schema': 'stock'}

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    secuencia = Column(NUMBER(6, 0, False), primary_key=True, nullable=False)
    fecha = Column(DateTime, nullable=False)
    observaciones = Column(VARCHAR(2000))
    useridc = Column(VARCHAR(3), nullable=False)
    precio = Column(NUMBER(14, 2, True))
    ice = Column(NUMBER(14, 2, True))
    cargos = Column(NUMBER(14, 2, True))
    fecha_inicio = Column(DateTime)
    fecha_final = Column(DateTime)
    tipo_generacion = Column(VARCHAR(2))
    fecha_cierre = Column(DateTime)
    @classmethod
    def query(cls):
        return db.session.query(cls)
class st_lista_precio(Base):
    __tablename__ = 'st_lista_precio'
    __table_args__ = (
        Index('idx_lista_precio_agencia', 'empresa', 'cod_agencia'),
        Index('idx_lista_precio_divisa', 'cod_divisa'),
        Index('idx_lista_precio_forma_pago', 'empresa', 'cod_forma_pago'),
        Index('idx_lista_precio_productos', 'empresa', 'cod_producto'),
        Index('idx_lista_precio_region', 'empresa', 'cod_modelo_zona', 'cod_item_zona'),
        Index('idx_lista_precio_tipo_clientes', 'empresa', 'cod_modelo_cli', 'cod_item_cli'),
        Index('idx_lista_precio_unidad', 'empresa', 'cod_unidad'),
        Index('idx_lista_precio_useridc', 'empresa', 'useridc'),
        Index('ind$_lista_precio_borra', 'empresa', 'estado_generacion', 'fecha_inicio'),
        Index('ind$_lista_precio_cod_producto', 'cod_producto', 'empresa'),
        {'schema': 'stock'}
    )

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_producto = Column(VARCHAR(14), primary_key=True, nullable=False)
    cod_modelo_cli = Column(VARCHAR(8), primary_key=True, nullable=False)
    cod_item_cli = Column(VARCHAR(3), primary_key=True, nullable=False)
    cod_modelo_zona = Column(VARCHAR(8), primary_key=True, nullable=False)
    cod_item_zona = Column(VARCHAR(3), primary_key=True, nullable=False)
    cod_agencia = Column(NUMBER(4, 0, False), primary_key=True, nullable=False)
    cod_unidad = Column(VARCHAR(8), primary_key=True, nullable=False)
    cod_forma_pago = Column(VARCHAR(3), primary_key=True, nullable=False)
    cod_divisa = Column(VARCHAR(20), primary_key=True, nullable=False)
    estado_generacion = Column(VARCHAR(1), primary_key=True, nullable=False)
    fecha_inicio = Column(DateTime, primary_key=True, nullable=False)
    fecha_final = Column(DateTime)
    valor = Column(NUMBER(14, 2, False), nullable=False)
    iva = Column(NUMBER(14, 2, True))
    ice = Column(NUMBER(14, 2, True))
    precio = Column(NUMBER(14, 2, False), nullable=False)
    cargos = Column(NUMBER(14, 2, True))
    useridc = Column(VARCHAR(3), nullable=False)
    secuencia_generacion = Column(NUMBER(6, 0, True))
    estado_vida = Column(VARCHAR(1), nullable=False)
    valor_alterno = Column(NUMBER(14, 2, True))
    rebate = Column(NUMBER(14, 2, True))
    aud_fecha = Column(DateTime)
    aud_usuario = Column(VARCHAR(30))
    aud_terminal = Column(VARCHAR(50))

    @classmethod
    def query(cls):
        return db.session.query(cls)