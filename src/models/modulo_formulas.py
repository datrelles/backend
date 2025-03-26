from sqlalchemy import Column, DateTime, Index, VARCHAR, text, Integer, PrimaryKeyConstraint, ForeignKey, \
    ForeignKeyConstraint, column
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from src.config.database import db

Base = declarative_base(metadata=db.metadata)
SCHEMA_NAME = 'stock'

class CustomBase(Base):
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


class Proceso(CustomBase):
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


class Formula(CustomBase):
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


class Parametro(CustomBase):
    __tablename__ = 'st_parametros_formulas'
    __table_args__ = {'schema': SCHEMA_NAME}

    empresa = Column(NUMBER(precision=2), primary_key=True)
    cod_parametro = Column(VARCHAR(8), primary_key=True)
    nombre = Column(VARCHAR(60), nullable=False)
    definicion = Column(VARCHAR(1000))
    estado = Column(NUMBER(precision=2), nullable=False, default=1)
    audit_usuario_ing = Column(VARCHAR(30), nullable=False, server_default=text("user"))
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @classmethod
    def query(cls):
        return db.session.query(cls)


class ParametrosXProceso(CustomBase):
    __tablename__ = 'st_parametros_x_proceso'
    __table_args__ = (
        PrimaryKeyConstraint('empresa', 'cod_proceso', 'cod_parametro'),
        {'schema': SCHEMA_NAME}
    )

    empresa = Column(NUMBER(precision=2))
    cod_proceso = Column(VARCHAR(8), ForeignKey(f'{SCHEMA_NAME}.st_proceso.cod_proceso'), nullable=False)
    proceso = relationship('Proceso')
    cod_parametro = Column(VARCHAR(8), ForeignKey(f'{SCHEMA_NAME}.st_parametros_formulas.cod_parametro'),
                           nullable=False)
    parametro = relationship('Parametro')
    cod_formula = Column(VARCHAR(8), ForeignKey(f'{SCHEMA_NAME}.st_formulas_procesos.cod_formula'))
    formula = relationship('Formula')
    factores_calculo = relationship('FactoresCalculoParametros',
                                    primaryjoin="and_(FactoresCalculoParametros.empresa == ParametrosXProceso.empresa, "
                                                "FactoresCalculoParametros.cod_proceso == ParametrosXProceso.cod_proceso, "
                                                "FactoresCalculoParametros.cod_parametro == ParametrosXProceso.cod_parametro)",
                                    ) #back_populates='parametros_x_proceso' # no se permite rastreo modificaciones
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


class FactoresCalculoParametros(CustomBase):
    __tablename__ = 'st_factores_calc_parametros'
    __table_args__ = (
        PrimaryKeyConstraint('empresa', 'cod_proceso', 'cod_parametro', 'orden'),
        {'schema': SCHEMA_NAME}
    )

    empresa = Column(NUMBER(precision=2), ForeignKey(f'{SCHEMA_NAME}.st_parametros_x_proceso.empresa'), nullable=False)
    cod_proceso = Column(VARCHAR(8), ForeignKey(f'{SCHEMA_NAME}.st_parametros_x_proceso.cod_proceso'), nullable=False)
    cod_parametro = Column(VARCHAR(8), ForeignKey(f'{SCHEMA_NAME}.st_parametros_x_proceso.cod_parametro'),
                           nullable=False)
    parametros_x_proceso = relationship('ParametrosXProceso',
                                        primaryjoin="and_(FactoresCalculoParametros.empresa == ParametrosXProceso.empresa, "
                                                    "FactoresCalculoParametros.cod_proceso == ParametrosXProceso.cod_proceso, "
                                                    "FactoresCalculoParametros.cod_parametro == ParametrosXProceso.cod_parametro)",
                                        )# back_populates='factores_calculo' # no se permite rastreo modificaciones
    orden = Column(NUMBER(precision=3))
    tipo_operador = Column(VARCHAR(3), nullable=False) # Puede ser: PAR(parámetro), VAL (valor fijo), OPE (operador)
    operador = Column(VARCHAR(1))
    valor_fijo = Column(NUMBER(precision=30, scale=8))
    cod_parametro_operador = Column(VARCHAR(8))
    audit_usuario_ing = Column(VARCHAR(30), nullable=False, server_default=text("user"))
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @classmethod
    def query(cls):
        return db.session.query(cls)
