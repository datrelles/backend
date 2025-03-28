from sqlalchemy import Column, DateTime, Index, VARCHAR, text, PrimaryKeyConstraint, ForeignKeyConstraint, UniqueConstraint
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