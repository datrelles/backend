from sqlalchemy import (Column, DateTime, Index, VARCHAR, text,
                        PrimaryKeyConstraint, ForeignKeyConstraint, UniqueConstraint, Date, String, Numeric,)
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship,deferred
from src.config.database import db

Base = declarative_base(metadata = db.metadata)
class Cliente(Base):
    __tablename__ = 'cliente'

    empresa = Column(NUMBER(2, 0, False), primary_key=True, nullable=False)
    cod_cliente = Column(VARCHAR(14), primary_key=True, nullable=False)
    cod_tipo_identificacion = Column(NUMBER(2))
    nombre = Column(VARCHAR(100), nullable=False)
    apellido1 = Column(VARCHAR(100), nullable=False)
    ruc = Column(VARCHAR(13))
    @classmethod
    def query(cls):
        return db.session.query(cls)

class st_politica_credito(Base):
    __tablename__ = 'ST_POLITICA_CREDITO'
    __table_args__ = (
        PrimaryKeyConstraint('cod_politica', 'empresa', name='XPKST_POLITICA_CREDITO'),
        ForeignKeyConstraint(
            ['empresa'],
            ['COMPUTO.EMPRESA.EMPRESA'],
            name='FK_POLITICA_CREDITO_EMPRESA'
        ),
    )

    cod_politica = Column(NUMBER(2), nullable=False)
    empresa = Column(NUMBER(2), nullable=False)
    nombre = Column(VARCHAR(50), nullable=False)
    observaciones = Column(VARCHAR(500))
    reite_por_descuento_precio = Column(NUMBER(5, 2))  # e.g. 99.99
    precio_costo = Column(VARCHAR(1))
    # 'precio_costo' may have values 'P' (price list) or 'C' (cost).

    @classmethod
    def query(cls):
        return db.session.query(cls)

class persona(Base):
    __tablename__ = 'PERSONA'
    __table_args__ = (
        PrimaryKeyConstraint('empresa', 'cod_tipo_persona', 'cod_persona', name='PK_PERSONA'),
        ForeignKeyConstraint(
            ['empresa', 'cod_tipo_persona'],
            ['TIPO_PERSONA.EMPRESA', 'TIPO_PERSONA.COD_TIPO_PERSONA'],
            name='FK_PERSONA_TIPO_PERSONA'
        ),
    )

    empresa = Column(NUMBER(2), nullable=False)
    cod_tipo_persona = Column(VARCHAR(3), nullable=False)
    cod_persona = Column(VARCHAR(14), nullable=False)
    nombre = Column(VARCHAR(255))

    @classmethod
    def query(cls):
        return db.session.query(cls)

class st_vendedor(Base):
    __tablename__ = 'ST_VENDEDOR'
    __table_args__ = (
        # Composite Primary Key (7 columns)
        PrimaryKeyConstraint(
            'empresa',
            'cod_tipo_persona_re',
            'cod_responsable',
            'cod_tipo_persona_su',
            'cod_supervisor',
            'cod_tipo_persona',
            'cod_vendedor',
            name='XPKST_VENDEDOR'
        ),
        # Unique Constraints
        UniqueConstraint('cod_persona_rh', name='UK_CL_PERSONA_VENDEDOR'),
        UniqueConstraint('empresa', 'cod_tipo_persona', 'cod_vendedor', name='UK_COD_VENDEDOR'),
        # Foreign Key Constraints
        # Note: The FK_ST_CLI_VEN is disabled / novalidate in the DDL, so you may omit it if it's truly disabled in production
        ForeignKeyConstraint(
            ['empresa', 'cod_bodega'],
            ['BODEGA.EMPRESA', 'BODEGA.BODEGA'],
            name='FK_VENDEDOR_BODEGA'
        ),
        ForeignKeyConstraint(
            ['empresa', 'cod_modelo', 'cod_item'],
            ['COMPUTO.TG_MODELO_ITEM.EMPRESA', 'COMPUTO.TG_MODELO_ITEM.COD_MODELO', 'COMPUTO.TG_MODELO_ITEM.COD_ITEM'],
            name='FK_VENDEDOR_MODELO_ITEM'
        ),
        ForeignKeyConstraint(
            ['empresa', 'cod_tipo_persona_su', 'cod_supervisor', 'cod_tipo_persona_re', 'cod_responsable'],
            ['ST_SUPERVISOR.EMPRESA', 'ST_SUPERVISOR.COD_TIPO_PERSONA', 'ST_SUPERVISOR.COD_SUPERVISOR',
             'ST_SUPERVISOR.COD_TIPO_PERSONA_RE', 'ST_SUPERVISOR.COD_RESPONSABLE'],
            name='FK_VENDEDOR_SUPERVISOR'
        ),
        ForeignKeyConstraint(
            ['empresa', 'useridc'],
            ['COMPUTO.USUARIO_EMPRESA.EMPRESA', 'COMPUTO.USUARIO_EMPRESA.USERIDC'],
            name='FK_VENDEDOR_USUARIO_EMPRESA'
        ),
        ForeignKeyConstraint(
            ['empresa', 'cod_tipo_persona'],
            ['TIPO_PERSONA.EMPRESA', 'TIPO_PERSONA.COD_TIPO_PERSONA'],
            name='R_137'
        ),
        ForeignKeyConstraint(
            ['empresa', 'cod_bodega', 'cod_subbodega'],
            ['SUB_BODEGA.EMPRESA', 'SUB_BODEGA.BODEGA', 'SUB_BODEGA.COD_SUBBODEGA']
        )
    )

    empresa = Column(NUMBER(2), nullable=False)
    cod_tipo_persona = Column(VARCHAR(3), nullable=False)
    cod_vendedor = Column(VARCHAR(14), nullable=False)
    cod_tipo_persona_re = Column(VARCHAR(3), nullable=False)
    cod_responsable = Column(VARCHAR(14), nullable=False)
    cod_tipo_persona_su = Column(VARCHAR(3), nullable=False)
    cod_supervisor = Column(VARCHAR(14), nullable=False)
    nombre = Column(VARCHAR(50), nullable=False)
    apellido1 = Column(VARCHAR(40), nullable=False)
    cedula = Column(VARCHAR(13))
    direccion = Column(VARCHAR(50))
    telefono = Column(VARCHAR(8))
    useridc = Column(VARCHAR(3), nullable=False)
    activo = Column(VARCHAR(1), nullable=False)  # 'S' or 'N'
    cod_cliente = Column(VARCHAR(14))
    aa = Column(NUMBER(4))
    codigo = Column(VARCHAR(14))
    cod_bodega = Column(NUMBER(4))
    cod_subbodega = Column(NUMBER(4))
    es_chofer = Column(VARCHAR(1))  # 'S' or 'N'
    cod_modelo = Column(VARCHAR(8))
    cod_item = Column(VARCHAR(3))
    cod_persona_rh = Column(NUMBER(8))
    costo = Column(NUMBER(14, 2))

    @classmethod
    def query(cls):
        return db.session.query(cls)


class cliente_hor(Base):
    __tablename__ = 'CLIENTE_HOR'
    __table_args__ = (
        # Clave primaria compuesta
        PrimaryKeyConstraint('empresah', 'cod_clienteh', name='PK_CLIENTE_HOR'),
        # ForeignKey deshabilitado en la DB, pero si quisieras reflejarlo:
      {'schema': 'STOCK'}
    )

    # Columns
    empresah                   = Column(Numeric(2, 0), nullable=False)
    cod_clienteh               = Column(String(14),    nullable=False)
    fecha_nacimientoh          = Column(Date)
    zona_geograficah           = Column(String(15))
    direccion_calleh           = Column(String(200))
    telefono1h                 = Column(String(15))
    telefono2h                 = Column(String(15))
    tipo_vivienda              = Column(String(1))
    nombre_dueno_casa          = Column(String(30))
    estado_civilh              = Column(String(1))
    cedula_conyugeh            = Column(String(14))
    nombre_conyugeh            = Column(String(100))
    empresa_conyugeh           = Column(String(60))
    cargo_conyugueh            = Column(String(50))
    fecha_ingreso_conyugeh     = Column(Date)
    direccion_conyugeh         = Column(String(50))
    ciudad_conyugeh            = Column(String(15))
    telefono_conyugeh          = Column(String(15))
    neto_conyugeh              = Column(Numeric(15, 2))
    otros_conyugeh             = Column(Numeric(15, 2))
    activoh                    = Column(String(1))
    e_mailh                    = Column(String(30))
    cod_divisa_netoh           = Column(String(20))
    cod_divisa_otrosh          = Column(String(20))
    observacionesh             = Column(String(255))
    fecha_creacionh            = Column(Date)
    agenciah                   = Column(Numeric(4, 0))
    cod_tipo_clienteh          = Column(String(3))
    tiene_cargosh              = Column(String(1))
    es_clienteh                = Column(String(1))
    es_garanteh                = Column(String(1))
    aplica_modeloh             = Column(String(1))
    empresa_trabajoh           = Column(String(50))
    telefono_empresah          = Column(String(15))
    direccion_empresah         = Column(String(200))
    cargo_empresah             = Column(String(50))
    neto_empresah              = Column(Numeric(14, 2))
    otros_empresah             = Column(Numeric(14, 2))
    direccion_refh             = Column(String(100))
    ruch                       = Column(String(13))
    instruccion                = Column(String(3))
    profesion                  = Column(String(6))
    fono_dueno_casa            = Column(String(15))
    aa_vivienda                = Column(Numeric(4, 0))
    fecha_empresa              = Column(Date)
    numero_casa                = Column(String(20))
    calle_transversal          = Column(String(100))
    fecha_modificacion         = Column(Date)
    gps_zona                   = Column(Numeric(10, 0))  # Ajusta si conoces la precisión real
    gps_x                      = Column(Numeric(10, 0))
    gps_y                      = Column(Numeric(10, 0))
    gps_z                      = Column(Numeric(10, 0))
    es_analfabeto              = Column(Numeric(1, 0), default=0)
    es_venta_cartera           = Column(Numeric(1, 0), default=1)
    numero_dependientes        = Column(Numeric(3, 0), default=0)
    es_sueldo_fijo             = Column(Numeric(1, 0), default=1)
    ocupacion_laboral          = Column(String(6))
    ubicacion_vivienda         = Column(String(6))
    aa_labora                  = Column(Numeric(4, 2))
    valor_adeuda               = Column(Numeric(14, 2))
    valor_gastos               = Column(Numeric(14, 2))
    pagare                     = Column(Numeric(14, 2))
    sexo                       = Column(String(1))
    celular                    = Column(String(15))
    ultimoproducto_comprado    = Column(String(50))
    tipo_tiempo_referencia     = Column(String(1))
    valor_arriendo_casa        = Column(Numeric(14, 2))
    bono_solidario             = Column(Numeric(1, 0))
    giros_exterior             = Column(Numeric(14, 2))
    direccion_cobro            = Column(String(200))
    email_factura              = Column(String(150))
    es_parte_rel_vta           = Column(String(2),  default='NO', nullable=False)
    ci_representante_legal     = Column(String(14))
    nombre_representante_legal = Column(String(100))

    # Clase helper: si usas un objeto de sesión
    @classmethod
    def query(cls):
        return db.session.query(cls)


class tg_tipo_identificacion(Base):
    __tablename__ = 'tg_tipo_identificacion'
    __table_args__ = (
        PrimaryKeyConstraint('cod_tipo_identificacion', 'empresa',  name='XPKTG_TIPO_IDENTIFICACION'),
    )
    cod_tipo_identificacion = Column(NUMBER(2), nullable=False)
    empresa = Column(NUMBER(2), nullable=False)
    nombre = Column(VARCHAR(15), nullable=False)
    formato = Column(VARCHAR(30), nullable=False)
    cod_tipo_identificacion_sri = Column(VARCHAR(2))
    @classmethod
    def query(cls):
        return db.session.query(cls)