# coding: utf-8
from sqlalchemy import Column, Index, VARCHAR, ForeignKey, CheckConstraint, UniqueConstraint, \
    ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

from sqlalchemy import Sequence
from sqlalchemy import DateTime, func
from sqlalchemy.orm import relationship
from src.models.productos import Producto


Base = declarative_base(metadata = db.metadata)

#Endpoints para ingreso de catalogs

class Chasis(Base):
    __tablename__ = 'st_chasis'
    __table_args__ = (
        Index('idx_chasis_codigo', 'codigo_chasis'),
        {'schema': 'stock'}
    )

    codigo_chasis = Column(
        NUMBER(14, 0),
        Sequence('seq_st_chasis', schema='stock'),
        primary_key=True)

    aros_rueda_posterior = Column(VARCHAR(50))
    neumatico_delantero = Column(VARCHAR(50))
    neumatico_trasero = Column(VARCHAR(50))
    suspension_delantera = Column(VARCHAR(50))
    suspension_trasera = Column(VARCHAR(50))
    frenos_delanteros = Column(VARCHAR(50))
    frenos_traseros = Column(VARCHAR(50))
    aros_rueda_delantera = Column(VARCHAR(50))

    usuario_crea = Column(VARCHAR(50))
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_modificacion = Column(DateTime, nullable=True)

    @classmethod
    def query(cls):
        return db.session.query(cls)

class DimensionPeso(Base):
    __tablename__ = 'st_dimensiones_peso'
    __table_args__ = {'schema': 'stock'}

    codigo_dim_peso = Column(
        NUMBER(14, 0),
        Sequence('seq_st_dimensiones_peso', schema='stock'),
        primary_key=True
    )

    altura_total = Column(NUMBER(10))
    longitud_total = Column(NUMBER(10))
    ancho_total = Column(NUMBER(10))
    peso_seco = Column(NUMBER(10))
    usuario_crea = Column(VARCHAR(50))
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_modificacion = Column(DateTime, nullable=True)

    @classmethod
    def query(cls):
        return db.session.query(cls)

class ElectronicaOtros(Base):
    __tablename__ = 'st_electronica_otros'
    __table_args__ = {'schema': 'stock'}

    codigo_electronica = Column(
        NUMBER(14, 0),
        Sequence('seq_st_electronica_otros', schema='stock'),
        primary_key=True
    )

    capacidad_combustible = Column(VARCHAR(70))
    tablero = Column(VARCHAR(70))
    luces_delanteras = Column(VARCHAR(50))
    luces_posteriores = Column(VARCHAR(50))
    garantia = Column(VARCHAR(70))
    velocidad_maxima = Column(VARCHAR(50))
    usuario_crea = Column(VARCHAR(50))
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_modificacion = Column(DateTime, nullable=True)

    @classmethod
    def query(cls):
        return db.session.query(cls)

class Transmision(Base):
    __tablename__ = 'st_transmision'
    __table_args__ = {'schema': 'stock'}

    codigo_transmision = Column(
        NUMBER(14, 0),
        Sequence('seq_st_transmision', schema='stock'),
        primary_key=True
    )

    caja_cambios = Column(VARCHAR(50))
    descripcion_transmision = Column(VARCHAR(150))

    usuario_crea = Column(VARCHAR(50))
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_modificacion = Column(DateTime, nullable=True)

class Imagenes(Base):
    __tablename__ = 'st_imagenes'
    __table_args__ = {'schema': 'stock'}

    codigo_imagen = Column(
        NUMBER(14, 0),
        Sequence('seq_st_imagenes', schema='stock'),
        primary_key=True
    )

    path_imagen = Column(VARCHAR(300), nullable=False)
    descripcion_imagen = Column(VARCHAR(150))

    usuario_crea = Column(VARCHAR(50))
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_modificacion = Column(DateTime, nullable=True)

class TipoMotor(Base):
    __tablename__ = 'st_tipo_motor'
    __table_args__ = {'schema': 'stock'}

    codigo_tipo_motor = Column(
        NUMBER(14, 0),
        Sequence('seq_st_tipo_motor', schema='stock'),
        primary_key=True
    )

    nombre_tipo = Column(VARCHAR(150), nullable=False)
    descripcion_tipo_motor = Column(VARCHAR(150))

class Motor(Base):
    __tablename__ = 'st_motor'
    __table_args__ = {'schema': 'stock'}

    codigo_motor = Column(
        NUMBER(14, 0),
        Sequence('seq_st_motor', schema='stock'),
        primary_key=True
    )

    codigo_tipo_motor = Column(NUMBER(14, 0), ForeignKey('stock.st_tipo_motor.codigo_tipo_motor'), primary_key=True)
    nombre_motor = Column(VARCHAR(100))
    cilindrada = Column(VARCHAR(60))
    caballos_fuerza = Column(VARCHAR(60))
    torque_maximo = Column(VARCHAR(60))
    sistema_combustible = Column(VARCHAR(60))
    arranque = Column(VARCHAR(60))
    sistema_refrigeracion = Column(VARCHAR(60))
    descripcion_motor = Column(VARCHAR(150))

    usuario_crea = Column(VARCHAR(50))
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_modificacion = Column(DateTime, nullable=True)


    tipo_motor = db.relationship('TipoMotor', backref='get_motores', lazy='joined')

class Color(Base):
    __tablename__ = 'st_color_bench'
    __table_args__ = {'schema': 'stock'}

    codigo_color_bench = Column(
        NUMBER(14, 0),
        Sequence('seq_st_color_bench', schema='stock'),
        primary_key=True
    )

    nombre_color = Column(VARCHAR(50), nullable=False)
    usuario_crea = Column(VARCHAR(50))
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_modificacion = Column(DateTime, nullable=True)

class Canal(Base):
    __tablename__ = 'st_canal'
    __table_args__ = {'schema': 'stock'}

    codigo_canal = Column(
        NUMBER(14, 0),
        Sequence('seq_st_canal', schema='stock'),
        primary_key=True
    )

    nombre_canal = Column(VARCHAR(50), nullable=False)
    estado_canal = Column(NUMBER(1)) # 1 ACTIVO 0 INACTIVO
    descripcion_canal = Column(VARCHAR(150))

    usuario_crea = Column(VARCHAR(50))
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_modificacion = Column(DateTime, nullable=True)

class MarcaRepuesto(Base):
    __tablename__ = 'st_marca_repuestos'
    __table_args__ = (
        CheckConstraint("estado_marca_rep IN (0, 1)", name="ck_st_marca_rep_estado"),
        UniqueConstraint("nombre_fabricante", name="uq_st_marca_rep_fabricante"),
        {'schema': 'stock'}
    )

    codigo_marca_rep = Column(
        NUMBER(14, 0),
        Sequence('seq_st_marca_repuestos', schema='stock'),
        primary_key=True
    )
    nombre_comercial = Column(VARCHAR(70), nullable=False)
    estado_marca_rep = Column(NUMBER(1), nullable=False)
    nombre_fabricante = Column(VARCHAR(70), unique=True)
    usuario_crea = Column(VARCHAR(50), nullable=False)
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_modificacion = Column(DateTime, nullable=True)

class ProductoExterno(Base):
    __tablename__ = 'st_producto_externo'
    __table_args__ = (
        CheckConstraint("estado_prod_externo IN (0, 1)", name="ck_st_prod_ext_estado"),
        UniqueConstraint("nombre_producto", "codigo_marca_rep", name="uq_st_prod_ext_nombre"),
        {'schema': 'stock'}
    )

    codigo_prod_externo = Column(VARCHAR(14), primary_key=True)

    codigo_marca_rep = Column(
        NUMBER(14),
        ForeignKey('stock.st_marca_repuestos.codigo_marca_rep'),
        nullable=False
    )

    nombre_producto = Column(VARCHAR(60), nullable=False)
    estado_prod_externo = Column(NUMBER(1))
    descripcion_producto = Column(VARCHAR(150))
    usuario_crea = Column(VARCHAR(50), nullable=False)
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_modificacion = Column(DateTime, nullable=True)

class Linea(Base):
    __tablename__ = 'st_linea'
    __table_args__ = (
        CheckConstraint("estado_linea IN (0, 1)", name="ck_st_linea_estado"),
        UniqueConstraint("nombre_linea", name="uq_st_linea_nombre"),
        {'schema': 'stock'}
    )

    codigo_linea = Column(
        NUMBER(14, 0),
        Sequence('seq_st_linea', schema='stock'),
        primary_key=True
    )
    codigo_linea_padre = Column(NUMBER(14))
    nombre_linea = Column(VARCHAR(50), nullable=False)
    estado_linea = Column(NUMBER(1), nullable=False)
    descripcion_linea = Column(VARCHAR(150))
    usuario_crea = Column(VARCHAR(50), nullable=False)
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_modificacion = Column(DateTime, nullable=True)

class Marca(Base):
    __tablename__ = 'st_marca'
    __table_args__ = (
        UniqueConstraint('nombre_marca', name='uq_st_marca_nombre'),
        CheckConstraint('estado_marca IN (0, 1)', name='ck_st_marca_estado'),
        {'schema': 'stock'}
    )

    codigo_marca = Column(
        NUMBER(14, 0),
        Sequence('seq_st_marca', schema='stock'),
        primary_key=True
    )
    nombre_marca = Column(VARCHAR(150), nullable=False)
    estado_marca = Column(NUMBER(1), nullable=False)
    usuario_crea = Column(VARCHAR(50), nullable=False)
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_modificacion = Column(DateTime, nullable=True)

class Benchmarking(Base):
    __tablename__ = 'st_benchmarking'
    __table_args__ = {'schema': 'stock'}

    empresa = Column(NUMBER(2), nullable=False)
    ram_inicial = Column(VARCHAR(50), nullable=False)
    ram_final = Column(VARCHAR(50))
    codigo_marca = Column(NUMBER(14), nullable=False)
    codigo_benchmarking = Column(NUMBER(14), primary_key=True)

class MatriculacionMarca(Base):
    __tablename__ = 'st_matriculacion_marca'
    __table_args__ = (
        UniqueConstraint('placa', name='uq_st_matriculacion_placa'),
        {'schema': 'stock'}
    )
    codigo_matricula_marca = Column(
        NUMBER(14, 0),
        Sequence('seq_st_matriculacion_marca', schema='stock'),
        primary_key=True)
    codigo_modelo_homologado = Column(
        NUMBER(14),
        ForeignKey('stock.st_modelo_homologado.codigo_modelo_homologado'), nullable=False
    )
    placa = Column(VARCHAR(15), nullable=False)
    fecha_matriculacion = Column(DateTime, nullable=False)
    fecha_facturacion = Column(DateTime, nullable=False)
    detalle_matriculacion = Column(VARCHAR(150))
    usuario_crea = Column(VARCHAR(50), nullable=False)
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_modificacion = Column(DateTime, nullable=True)

class ModeloSRI(Base):
    __tablename__ = 'st_modelo_sri'
    __table_args__ = (
        UniqueConstraint('nombre_modelo', name='uq_st_modelo_sri_nombre'),
        CheckConstraint('anio_modelo BETWEEN 1950 AND 2100', name='ck_st_modelo_sri_anio'),
        CheckConstraint('estado_modelo IN (0, 1)', name='ck_st_modelo_sri_estado'),
        {'schema': 'stock'}
    )

    codigo_modelo_sri = Column(
        NUMBER(14, 0),
        Sequence('seq_st_modelo_sri', schema='stock'),
        primary_key=True
    )
    nombre_modelo = Column(VARCHAR(150), nullable=False)
    anio_modelo = Column(NUMBER(4), nullable=False)
    estado_modelo = Column(NUMBER(1), nullable=False)
    cod_mdl_importacion = Column(VARCHAR(300))
    usuario_crea = Column(VARCHAR(50), nullable=False)
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_modificacion = Column(DateTime, nullable=True)

class ModeloHomologado(Base):
    __tablename__ = 'st_modelo_homologado'
    __table_args__ = {'schema': 'stock'}

    codigo_modelo_homologado = Column(
        NUMBER(14, 0),
        Sequence('seq_st_modelo_homologado', schema='stock'),
        primary_key=True
    )
    codigo_modelo_sri = Column(NUMBER(14), ForeignKey('stock.st_modelo_sri.codigo_modelo_sri'), nullable=False)
    descripcion_homologacion = Column(VARCHAR(150))
    usuario_crea = Column(VARCHAR(50), nullable=False)
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_modificacion = Column(DateTime, nullable=True)

    modelo_sri = relationship("ModeloSRI", backref="homologaciones")

class ModeloComercial(Base):
    __tablename__ = 'st_modelo_comercial'
    __table_args__ = (
        UniqueConstraint('nombre_modelo', name='uq_st_mod_com_nombre'),
        CheckConstraint('anio_modelo BETWEEN 1950 AND 2100', name='ck_st_mod_com_anio'),
        CheckConstraint('estado_modelo IN (0, 1)', name='ck_st_mod_com_estado'),
        {'schema': 'stock'}
    )

    codigo_modelo_comercial = Column(
        NUMBER(14, 0),
        Sequence('seq_st_modelo_comercial', schema='stock'),
        primary_key=True
    )
    codigo_marca = Column(
        NUMBER(14),
        ForeignKey('stock.st_marca.codigo_marca'),
        primary_key=True, nullable=False
    )
    codigo_modelo_homologado = Column(
        NUMBER(14),
        ForeignKey('stock.st_modelo_homologado.codigo_modelo_homologado'),
        nullable=False
    )
    nombre_modelo = Column(VARCHAR(150), nullable=False)
    anio_modelo = Column(NUMBER(4), nullable=False)
    estado_modelo = Column(NUMBER(1), nullable=False)
    usuario_crea = Column(VARCHAR(50), nullable=False)
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_modificacion = Column(DateTime, nullable=True)

    marca = relationship("Marca", backref="modelos_comerciales")
    modelo_homologado = relationship("ModeloHomologado", backref="modelos_comerciales")

class Segmento(Base):
    __tablename__ = 'st_segmento'
    __table_args__ = (
        ForeignKeyConstraint(
            ['codigo_modelo_comercial', 'codigo_marca'],
            ['stock.st_modelo_comercial.codigo_modelo_comercial', 'stock.st_modelo_comercial.codigo_marca'],
            name='fk_seg_modelo'
        ),
        UniqueConstraint('nombre_segmento', 'codigo_modelo_comercial', name='uq_st_segmento_nombre'),
        CheckConstraint('estado_segmento IN (0, 1)', name='ck_seg_estado'),
        {'schema': 'stock'}
    )

    codigo_segmento = Column(NUMBER(14), Sequence('seq_st_segmento', schema='stock'), primary_key=True)
    codigo_linea = Column(NUMBER(14), ForeignKey('stock.st_linea.codigo_linea'), nullable=False, primary_key=True)
    codigo_modelo_comercial = Column(NUMBER(14), nullable=False, primary_key=True)
    codigo_marca = Column(NUMBER(14), ForeignKey('stock.st_marca.codigo_marca'), nullable=False, primary_key=True)

    nombre_segmento = Column(VARCHAR(70), nullable=False)
    estado_segmento = Column(NUMBER(1), nullable=False)
    descripcion_segmento = Column(VARCHAR(150))
    usuario_crea = Column(VARCHAR(50), nullable=False)
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_modificacion = Column(DateTime, nullable=True)

class Version(Base):
    __tablename__ = 'st_version'
    __table_args__ = (
        UniqueConstraint('nombre_version', name='uq_st_version_nombre'),
        CheckConstraint('estado_version IN (0, 1)', name='ck_st_version_estado'),
        {'schema': 'stock'}
    )

    codigo_version = Column(NUMBER(14), Sequence('seq_st_version', schema='stock'), primary_key=True)
    nombre_version = Column(VARCHAR(150), nullable=False)
    descripcion_version = Column(VARCHAR(150))
    estado_version = Column(NUMBER(1), nullable=False)
    usuario_crea = Column(VARCHAR(50), nullable=False)
    usuario_modifica = Column(VARCHAR(50))
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_modificacion = Column(DateTime, nullable=True)

class ModeloVersionRepuesto(Base):
    __tablename__ = 'st_modelo_version_repuesto'
    __table_args__ = (
        PrimaryKeyConstraint(
            'codigo_mod_vers_repuesto',
            'cod_producto',
            'empresa',
            name='pk_st_mod_vers_repuesto'
        ),

        ForeignKeyConstraint(
            ['empresa', 'cod_producto'],
            ['stock.producto.empresa', 'stock.producto.cod_producto'],
            name='fk_st_mod_ver_rep_producto'
        ),
        {'schema': 'stock'}
    )

    codigo_mod_vers_repuesto = Column(NUMBER(14, 0), Sequence('seq_st_modelo_version_repuesto', schema='stock'), nullable=False)
    codigo_prod_externo = Column(VARCHAR(14), ForeignKey('stock.st_producto_externo.codigo_prod_externo'), nullable=False)
    codigo_version = Column(NUMBER(14), ForeignKey('stock.st_version.codigo_version'), nullable=False)
    empresa = Column(NUMBER(2), nullable=False)
    cod_producto = Column(VARCHAR(14), nullable=False)
    descripcion = Column(VARCHAR(150))
    precio_producto_modelo = Column(NUMBER(10,2), nullable=False)
    precio_venta_distribuidor = Column(NUMBER(10,2), nullable=False)

    producto_externo = relationship("ProductoExterno", backref="repuestos_version")
    version = relationship("Version", backref="repuestos_version")
    producto = relationship(Producto, backref="repuestos_modelo_version")

class ClienteCanal(Base):
    __tablename__ = 'st_cliente_canal'
    __table_args__ = (
        PrimaryKeyConstraint(
            'codigo_cliente_canal',
            'codigo_mod_vers_repuesto',
            'cod_producto',
            'empresa',
            name='pk_st_cliente_canal'
        ),
        ForeignKeyConstraint(
            ['codigo_mod_vers_repuesto', 'cod_producto', 'empresa'],
            ['stock.st_modelo_version_repuesto.codigo_mod_vers_repuesto',
             'stock.st_modelo_version_repuesto.cod_producto',
             'stock.st_modelo_version_repuesto.empresa'],
            name='fk_st_cliente_canal_modvers'
        ),
        {'schema': 'stock'}
    )

    codigo_cliente_canal = Column(NUMBER(14), Sequence('seq_st_cliente_canal', schema='stock'))
    codigo_canal = Column(NUMBER(14), nullable=False)
    codigo_mod_vers_repuesto = Column(NUMBER(14), nullable=False)
    empresa = Column(NUMBER(2), nullable=False)
    cod_producto = Column(VARCHAR(14), nullable=False)
    descripcion_cliente_canal = Column(VARCHAR(150))

class ModeloVersion(Base):
    __tablename__ = 'st_modelo_version'
    __table_args__ = (
        UniqueConstraint('nombre_modelo_version', name='uq_mv_nombre_modelo_version'),
        CheckConstraint('anio_modelo_version BETWEEN 1950 AND 2100', name='ck_mv_anio_modelo'),
        ForeignKeyConstraint(
            ['codigo_cliente_canal', 'codigo_mod_vers_repuesto', 'cod_producto', 'empresa'],
            ['stock.st_cliente_canal.codigo_cliente_canal',
             'stock.st_cliente_canal.codigo_mod_vers_repuesto',
             'stock.st_cliente_canal.cod_producto',
             'stock.st_cliente_canal.empresa'],
            name='fk_mv_cliente_canal'
        ),
        ForeignKeyConstraint(
            ['codigo_modelo_comercial', 'codigo_marca'],
            ['stock.st_modelo_comercial.codigo_modelo_comercial',
             'stock.st_modelo_comercial.codigo_marca'],
            name='fk_mv_modelo_comercial'
        ),
        {'schema': 'stock'}
    )

    codigo_modelo_version = Column(NUMBER(14), Sequence('seq_st_modelo_version', schema='stock'), primary_key=True)
    codigo_dim_peso = Column(NUMBER(14), ForeignKey('stock.st_dimensiones_peso.codigo_dim_peso'), nullable=False)
    codigo_imagen = Column(NUMBER(14), ForeignKey('stock.st_imagenes.codigo_imagen'), nullable=False)
    codigo_electronica = Column(NUMBER(14), ForeignKey('stock.st_electronica_otros.codigo_electronica'), nullable=False)
    codigo_motor = Column(NUMBER(14), nullable=False)
    codigo_tipo_motor = Column(NUMBER(14), nullable=False)
    codigo_transmision = Column(NUMBER(14), ForeignKey('stock.st_transmision.codigo_transmision'), nullable=False)
    codigo_color_bench = Column(NUMBER(14), ForeignKey('stock.st_color_bench.codigo_color_bench'), nullable=False)
    codigo_chasis = Column(NUMBER(14), ForeignKey('stock.st_chasis.codigo_chasis'), nullable=False)

    codigo_modelo_comercial = Column(NUMBER(14), nullable=False)
    codigo_marca = Column(NUMBER(14), nullable=False)

    codigo_cliente_canal = Column(NUMBER(14), nullable=False)
    codigo_mod_vers_repuesto = Column(NUMBER(14), nullable=False)
    empresa = Column(NUMBER(2), nullable=False)
    cod_producto = Column(VARCHAR(14), nullable=False)
    codigo_version = Column(NUMBER(14), ForeignKey('stock.st_version.codigo_version'), nullable=False)

    nombre_modelo_version = Column(VARCHAR(50), nullable=False)
    anio_modelo_version = Column(NUMBER(4), nullable=False)
    precio_producto_modelo = Column(NUMBER(10), nullable=False)
    precio_venta_distribuidor = Column(NUMBER(10), nullable=False)





