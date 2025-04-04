# coding: utf-8
from sqlalchemy import (Column, DateTime,
                        Index, VARCHAR,
                        NVARCHAR, text, CHAR,
                        Float, Unicode, ForeignKeyConstraint,
                        PrimaryKeyConstraint, CheckConstraint,  and_, ForeignKey, Date )
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.orm import relationship,deferred
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

Base = declarative_base(metadata = db.metadata)


class Empresa(db.Model):
    __tablename__ = 'empresa'
    __table_args__ = {'schema': 'computo'}

    empresa = Column(NUMBER(2, 0, False), primary_key=True)
    nombre = Column(VARCHAR(100), nullable=False)
    pais = Column(VARCHAR(15), nullable=False)
    ciudad = Column(VARCHAR(20), nullable=False)
    direccion = Column(VARCHAR(40), nullable=False)
    telefono1 = Column(NUMBER(8, 0, False))
    telefono2 = Column(NUMBER(8, 0, False))
    fax = Column(NUMBER(8, 0, False))
    iva = Column(NUMBER(5, 2, True))
    ice = Column(NUMBER(5, 2, True))
    ise = Column(NUMBER(5, 2, True))
    contabilidad_consulta_inicial = Column(DateTime, nullable=False)
    contabilidad_consulta_final = Column(DateTime, nullable=False)
    contabilidad_modifica_inicial = Column(DateTime, nullable=False)
    contabilidad_modifica_final = Column(DateTime, nullable=False)
    inventario_consulta_inicial = Column(DateTime, nullable=False)
    inventario_consulta_final = Column(DateTime, nullable=False)
    inventario_modifica_inicial = Column(DateTime, nullable=False)
    inventario_modifica_final = Column(DateTime, nullable=False)
    ruc = Column(VARCHAR(13), nullable=False)
    moneda = Column(VARCHAR(20), nullable=False)
    signo_moneda = Column(VARCHAR(3), nullable=False)
    casilla = Column(VARCHAR(10))
    contador = Column(VARCHAR(40), nullable=False)
    interes = Column(NUMBER(5, 2, True))
    interes_mora = Column(NUMBER(5, 2, True))
    descuento = Column(NUMBER(5, 2, True))
    entrada = Column(NUMBER(5, 2, True))
    mensaje = Column(VARCHAR(100))
    numero_patronal = Column(VARCHAR(10))
    provincia = Column(VARCHAR(20), nullable=False)
    canton = Column(VARCHAR(20), nullable=False)
    parroquia = Column(VARCHAR(20))
    gerente_apellido1 = Column(VARCHAR(20), nullable=False)
    gerente_apellido2 = Column(VARCHAR(20))
    gerente_nombre = Column(VARCHAR(20))
    gerente_cedula = Column(VARCHAR(13))
    iess_patronal = Column(NUMBER(5, 2, True))
    iess_cesantia = Column(NUMBER(5, 2, True))
    iess_secap = Column(NUMBER(5, 2, True))
    iess_iece = Column(NUMBER(5, 2, True))
    comision_vendedores = Column(NUMBER(5, 2, True))
    comision_choferes = Column(NUMBER(5, 2, True))
    comision_supervisor = Column(NUMBER(5, 2, True))
    habitaciones = Column(NUMBER(4, 0, False))
    hotel_consulta_inicial = Column(DateTime, nullable=False)
    hotel_consulta_final = Column(DateTime, nullable=False)
    hotel_modifica_inicial = Column(DateTime, nullable=False)
    hotel_modifica_final = Column(DateTime, nullable=False)
    ecuasoft = Column(VARCHAR(120))
    forma = Column(NUMBER(2, 0, False))
    logo = Column(VARCHAR(50))
    valor_acciones = Column(NUMBER(12, 0, False))
    cod_tipo_persona = Column(VARCHAR(3))
    cod_persona = Column(VARCHAR(14))
    iess_personal = Column(NUMBER(5, 2, True))
    aa_ventas = Column(NUMBER(4, 0, False))
    factor_venta = Column(NUMBER(14, 2, True))
    color = Column(VARCHAR(3))

    def to_dict(empresa):
        return {
            'empresa': empresa.empresa,
            'nombre': empresa.nombre,
            'pais': empresa.pais,
            'ciudad': empresa.ciudad,
            'direccion': empresa.direccion,
            'telefono1': empresa.telefono1,
            'telefono2': empresa.telefono2,
            'fax': empresa.fax,
            'iva': (empresa.iva),
            'ice': (empresa.ice),
            'ise': (empresa.ise),
            'contabilidad_consulta_inicial': str(empresa.contabilidad_consulta_inicial),
            'contabilidad_consulta_final': str(empresa.contabilidad_consulta_final),
            'contabilidad_modifica_inicial': str(empresa.contabilidad_modifica_inicial),
            'contabilidad_modifica_final': str(empresa.contabilidad_modifica_final),
            'inventario_consulta_inicial': str(empresa.inventario_consulta_inicial),
            'inventario_consulta_final': str(empresa.inventario_consulta_final),
            'inventario_modifica_inicial': str(empresa.inventario_modifica_inicial),
            'inventario_modifica_final': str(empresa.inventario_modifica_final),
            'ruc': empresa.ruc,
            'moneda': empresa.moneda,
            'signo_moneda': empresa.signo_moneda,
            'casilla': empresa.casilla,
            'contador': empresa.contador,
            'interes': (empresa.interes),
            'interes_mora': (empresa.interes_mora),
            'descuento': (empresa.descuento),
            'entrada': (empresa.entrada),
            'mensaje': empresa.mensaje,
            'numero_patronal': empresa.numero_patronal,
            'provincia': empresa.provincia,
            'canton': empresa.canton,
            'parroquia': empresa.parroquia,
            'gerente_apellido1': empresa.gerente_apellido1,
            'gerente_apellido2': empresa.gerente_apellido2,
            'gerente_nombre': empresa.gerente_nombre,
            'gerente_cedula': empresa.gerente_cedula,
            'iess_patronal': (empresa.iess_patronal),
            'iess_cesantia': (empresa.iess_cesantia),
            'iess_secap': (empresa.iess_secap),
            'iess_iece': (empresa.iess_iece),
            'comision_vendedores': (empresa.comision_vendedores),
            'comision_choferes': (empresa.comision_choferes),
            'habitaciones': empresa.habitaciones,
            'hotel_consulta_inicial': str(empresa.hotel_consulta_inicial),
            'hotel_consulta_final': str(empresa.hotel_consulta_final),
            'hotel_modifica_inicial': str(empresa.hotel_modifica_inicial),
            'hotel_modifica_final': str(empresa.hotel_modifica_final),
            'ecuasoft': empresa.ecuasoft,
            'forma': empresa.forma,
            'logo': empresa.logo,
            'valor_acciones': (empresa.valor_acciones),
            'cod_tipo_persona': empresa.cod_tipo_persona,
            'cod_persona': empresa.cod_persona,
            'iess_personal' : empresa.iess_personal,
            'aa_ventas': empresa.aa_ventas,
            'factor_venta' : empresa.factor_venta,
            'color' : empresa.color 
        }


class Usuario(Base):
    __tablename__ = 'usuario'
    __table_args__ = {'schema': 'computo'}

    usuario_oracle = Column(VARCHAR(20), primary_key=True)
    apellido1 = Column(VARCHAR(20), nullable=False)
    apellido2 = Column(VARCHAR(20))
    nombre = Column(VARCHAR(20), nullable=False)
    empresa_actual = Column(ForeignKey('computo.empresa.empresa'), nullable=False)
    useridc = Column(VARCHAR(3), nullable=False, unique=True)
    toda_bodega = Column(VARCHAR(1))
    toda_empresa = Column(VARCHAR(1))
    agencia_actual = Column(NUMBER(4, 0, False))
    aa = Column(NUMBER(4, 0, False))
    e_mail = Column(VARCHAR(60))
    password = Column(VARCHAR(110))
    empresa = deferred(relationship(Empresa, backref = 'Usuario'))
    celular = Column(VARCHAR(20))
    @classmethod
    def query(cls):
        return db.session.query(cls)


class tg_rol(Base):
    __tablename__ = 'TG_ROL'
    __table_args__ = (
        {'schema': 'COMPUTO'},  # Esquema COMPUTO
    )
    # Definición de columnas
    empresa = Column(NUMBER(2), ForeignKey('COMPUTO.EMPRESA.EMPRESA'), primary_key=True, nullable=False)
    cod_rol = Column(VARCHAR(9), primary_key=True, nullable=False)
    nombre = Column(VARCHAR(100), nullable=True)
    activo = Column(NUMBER(1), nullable=True)
    descripcion = Column(VARCHAR(200), nullable=True)
    usuario_crea = Column(VARCHAR(14), nullable=True)
    fecha_crea = Column(Date, nullable=True)
    usuario_modifica = Column(VARCHAR(14), nullable=True)
    fecha_modifica = Column(Date, nullable=True)

    # Clase de consulta
    @classmethod
    def query(cls):
        return db.session.query(cls)

class tg_rol_usuario(Base):
        __tablename__ = 'TG_ROL_USUARIO'
        __table_args__ = (
            # Constraint para la llave foránea compuesta hacia TG_ROL
            ForeignKeyConstraint(
                ['cod_rol', 'empresa'],
                ['computo.TG_ROL.cod_rol', 'computo.TG_ROL.empresa']
            ),
            {'schema': 'computo'}  # Esquema en Oracle
        )

        empresa = Column(NUMBER(2), primary_key=True, nullable=False)
        cod_rol = Column(VARCHAR(9), primary_key=True, nullable=False)
        usuario = Column(VARCHAR(20),
                         ForeignKey('computo.usuario.usuario_oracle'),
                         primary_key=True,
                         nullable=False)
        activo = Column(NUMBER(1))
        observacion = Column(VARCHAR(200))
        usuario_crea = Column(VARCHAR(14))
        fecha_crea = Column(Date)
        usuario_modifica = Column(VARCHAR(14))
        fecha_modifica = Column(Date)

        @classmethod
        def query(cls):
            return db.session.query(cls)

class tg_agencia(Base):
    __tablename__ = 'TG_AGENCIA'
    __table_args__ = (
        PrimaryKeyConstraint('empresa', 'cod_agencia', name='XPKTG_AGENCIA'),
        # Llaves foráneas (se definen si las tablas referenciadas están mapeadas y se usará relationship)
        ForeignKeyConstraint(['empresa'], ['COMPUTO.EMPRESA.EMPRESA'], name='FK_AGENCIA_EMPRESA', use_alter=True, deferrable=True, initially='DEFERRED'),
        ForeignKeyConstraint(['empresa', 'cod_grupo_agencia'], ['COMPUTO.TG_GRUPO_AGENCIA.EMPRESA', 'COMPUTO.TG_GRUPO_AGENCIA.COD_GRUPO'], name='FK_AGENCIA_GRUPO_AGENCIA', use_alter=True, deferrable=True, initially='DEFERRED'),
        ForeignKeyConstraint(['cod_categoria_zona', 'empresa_zona', 'secuencia_zona', 'cod_nivel_zona', 'codigo_zona'],
                             ['COMPUTO.TG_CLASIFICACIONES.NIV_CAT_COD_CATEGORIA',
                              'COMPUTO.TG_CLASIFICACIONES.NIV_CAT_EMP_EMPRESA',
                              'COMPUTO.TG_CLASIFICACIONES.NIV_SECUENCIA',
                              'COMPUTO.TG_CLASIFICACIONES.NIV_COD_NIVEL',
                              'COMPUTO.TG_CLASIFICACIONES.CODIGO'],
                             name='FK_AGENCIA_CLASIFICACIONES', use_alter=True, deferrable=True, initially='DEFERRED'),
        CheckConstraint("activo in ('S','N')", name='CK_AGENCIA_ACTIVO'),
        CheckConstraint("TIPO_RELACION_POLCRE IN ('T','E','I','N')", name='CK_AGENCIA_TIPO_RELACION_POLCR'),
        {'schema': 'COMPUTO'}
    )

    empresa = Column(NUMBER(2), nullable=False)
    cod_agencia = Column(NUMBER(4), nullable=False)
    nombre = Column(VARCHAR(50), nullable=False)
    cod_categoria_zona = Column(VARCHAR(2))
    empresa_zona = Column(NUMBER(2))
    secuencia_zona = Column(NUMBER(6))
    cod_nivel_zona = Column(VARCHAR(8))
    codigo_zona = Column(VARCHAR(14))
    direccion = Column(VARCHAR(200))
    observaciones = Column(VARCHAR(200))
    telefono1 = Column(VARCHAR(15))
    telefono2 = Column(VARCHAR(15))
    ruc = Column(VARCHAR(20))
    activo = Column(VARCHAR(1))
    cod_grupo_agencia = Column(VARCHAR(3))
    cod_sitio = Column(VARCHAR(3), nullable=False)
    es_autorizado_sri = Column(NUMBER(1), nullable=False, server_default=text("0"))
    tipo_relacion_polcre = Column(VARCHAR(1), nullable=False, server_default=text("'N'"))

    @classmethod
    def query(cls):
        return db.session.query(cls)

class Orden(Base):
    __tablename__ = 'ORDEN'
    __table_args__ = (
        # Primary Key Constraint
        PrimaryKeyConstraint('empresa', 'bodega', 'tipo_comprobante', name='PK_ORDEN'),
        # Foreign Key Constraints
        ForeignKeyConstraint(
            ['empresa', 'bodega'],
            ['COMPUTO.TG_AGENCIA.EMPRESA', 'COMPUTO.TG_AGENCIA.COD_AGENCIA'],
            name='FK_ORDEN_AGENCIA'
        ),
        ForeignKeyConstraint(
            ['empresa'],
            ['COMPUTO.EMPRESA.EMPRESA'],
            name='FK_ORDEN_EMPRESA'
        ),
        ForeignKeyConstraint(
            ['empresa', 'cod_agencia'],
            ['COMPUTO.TG_AGENCIA.EMPRESA', 'COMPUTO.TG_AGENCIA.COD_AGENCIA'],
            name='FK_ORDEN_TG_AGENCIA'
        ),
        # Schema for the table
        {'schema': 'CONTABILIDAD'}
    )

    empresa = Column(NUMBER(2), nullable=False)
    bodega = Column(NUMBER(4), nullable=False)
    tipo_comprobante = Column(VARCHAR(2), nullable=False)
    sigla_comprobante = Column(VARCHAR(3), nullable=False)
    numero_comprobante = Column(NUMBER(6), nullable=False)
    useridc = Column(VARCHAR(3), nullable=False)
    cod_agencia = Column(NUMBER(4))

    @classmethod
    def query(cls):
        return db.session.query(cls)

