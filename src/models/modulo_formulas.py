from sqlalchemy import Column, DateTime, Index, VARCHAR, text, Integer, PrimaryKeyConstraint, ForeignKey, \
    ForeignKeyConstraint, column
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from src.config.database import db

TIPOS_OPE_VALIDOS = {'PAR', 'VAL', 'OPE'}  # PAR: parámetro, VAL: valor fijo, OPE: operador
OPERADORES_VALIDOS = {'+', '-', '*', '/'}

Base = declarative_base(metadata=db.metadata)
SCHEMA_NAME = 'stock'


class custom_base(Base):
    """
    Clase personalizada para que contenga la definición del método que serializa el objeto.
    """
    __abstract__ = True  # Parámetro para omitir creación de tabla

    def to_dict(self, excluir_none=False):
        """
        Convierte el modelo en un diccionario serializable.
        """
        data = {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
        if excluir_none:
            data = {k: v for k, v in data.items() if v is not None}
        return data

    @classmethod
    def to_list(cls, items):
        """
        Convierte un listado de objetos Query en una lista.
        """
        return [obj.to_dict() for obj in items]


class st_proceso(custom_base):
    __tablename__ = 'st_proceso'
    __table_args__ = {'schema': SCHEMA_NAME}

    empresa = Column(NUMBER(precision=2), primary_key=True)
    cod_proceso = Column(VARCHAR(8), primary_key=True)
    nombre = Column(VARCHAR(30), nullable=False)
    estado = Column(NUMBER(precision=2), nullable=False, default=1)
    audit_usuario_ing = Column(VARCHAR(30), nullable=False, server_default=text("user"))
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @classmethod
    def query(cls):
        return db.session.query(cls)


class st_formula(custom_base):
    __tablename__ = 'st_formulas_procesos'
    __table_args__ = {'schema': SCHEMA_NAME}

    empresa = Column(NUMBER(precision=2), primary_key=True)
    cod_formula = Column(VARCHAR(8), primary_key=True)
    nombre = Column(VARCHAR(100), nullable=False)
    observaciones = Column(VARCHAR(800))
    estado = Column(NUMBER(precision=2), nullable=False, default=1)
    definicion = Column(VARCHAR(2000), nullable=False)
    audit_usuario_ing = Column(VARCHAR(30), nullable=False, server_default=text("user"))
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @classmethod
    def query(cls):
        return db.session.query(cls)


class st_parametro(custom_base):
    __tablename__ = 'st_parametros_formulas'
    __table_args__ = {'schema': SCHEMA_NAME}

    empresa = Column(NUMBER(precision=2), primary_key=True)
    cod_parametro = Column(VARCHAR(8), primary_key=True)
    nombre = Column(VARCHAR(60), nullable=False)
    descripcion = Column(VARCHAR(1000))
    estado = Column(NUMBER(precision=2), nullable=False, default=1)
    audit_usuario_ing = Column(VARCHAR(30), nullable=False, server_default=text("user"))
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @classmethod
    def query(cls):
        return db.session.query(cls)


class st_parametros_x_proceso(custom_base):
    __tablename__ = 'st_parametros_x_proceso'
    __table_args__ = (
        PrimaryKeyConstraint('empresa', 'cod_proceso', 'cod_parametro'),
        {'schema': SCHEMA_NAME}
    )

    empresa = Column(NUMBER(precision=2))
    cod_proceso = Column(VARCHAR(8), ForeignKey(f'{SCHEMA_NAME}.st_proceso.cod_proceso'), nullable=False)
    proceso = relationship('st_proceso')
    cod_parametro = Column(VARCHAR(8), ForeignKey(f'{SCHEMA_NAME}.st_parametros_formulas.cod_parametro'),
                           nullable=False)
    parametro = relationship('st_parametro')
    cod_formula = Column(VARCHAR(8), ForeignKey(f'{SCHEMA_NAME}.st_formulas_procesos.cod_formula'))
    formula = relationship('st_formula')
    factores_calculo = relationship('st_factores_calculo_parametros',
                                    primaryjoin="and_(st_parametros_x_proceso.empresa == st_factores_calculo_parametros.empresa, "
                                                "st_parametros_x_proceso.cod_proceso == st_factores_calculo_parametros.cod_proceso, "
                                                "st_parametros_x_proceso.cod_parametro == st_factores_calculo_parametros.cod_parametro)",
                                    )
    orden_calculo = Column(NUMBER(precision=5))
    estado = Column(NUMBER(precision=2), nullable=False, default=1)
    fecha_calculo_inicio = Column(DateTime)
    fecha_calculo_fin = Column(DateTime)
    orden_imprime = Column(NUMBER(precision=5), nullable=False)
    audit_usuario_ing = Column(VARCHAR(30), nullable=False, server_default=text("user"))
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @classmethod
    def query(cls):
        return db.session.query(cls)


class st_factores_calculo_parametros(custom_base):
    __tablename__ = 'st_factores_calc_parametros'
    __table_args__ = (
        PrimaryKeyConstraint('empresa', 'cod_proceso', 'cod_parametro', 'orden'),
        {'schema': SCHEMA_NAME}
    )

    empresa = Column(NUMBER(precision=2), ForeignKey(f'{SCHEMA_NAME}.st_parametros_x_proceso.empresa'), nullable=False)
    cod_proceso = Column(VARCHAR(8), ForeignKey(f'{SCHEMA_NAME}.st_parametros_x_proceso.cod_proceso'), nullable=False)
    cod_parametro = Column(VARCHAR(8), ForeignKey(f'{SCHEMA_NAME}.st_parametros_x_proceso.cod_parametro'),
                           nullable=False)
    orden = Column(NUMBER(precision=3))
    tipo_operador = Column(VARCHAR(3), nullable=False)  # Solo acepta: TIPOS_OPE_VALIDOS
    operador = Column(VARCHAR(1))  # Solo acepta: OPERADORES_VALIDOS
    valor_fijo = Column(NUMBER(precision=30, scale=8))
    cod_parametro_operador = Column(VARCHAR(8))
    audit_usuario_ing = Column(VARCHAR(30), nullable=False, server_default=text("user"))
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @classmethod
    def query(cls):
        return db.session.query(cls)
