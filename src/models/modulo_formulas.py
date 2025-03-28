from sqlalchemy import Column, DateTime, Index, VARCHAR, text, Integer, PrimaryKeyConstraint, ForeignKey, \
    ForeignKeyConstraint, column
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from src.config.database import db
from src.exceptions.validation import validation_error
from src.models.categoria_excepcion import categoria_excepcion
from src.validations.alfanumericas import validar_varchar
from src.validations.numericas import validar_number

TIPOS_OPE_VALIDOS = {'PAR', 'VAL', 'OPE'}  # PAR: parámetro, VAL: valor fijo, OPE: operador
OPERADORES_VALIDOS = {'+', '-', '*', '/'}

Base = declarative_base(metadata=db.metadata)
SCHEMA_NAME = 'stock'


def validar_empresa(clave, valor):
    return validar_number(clave, valor, 2)


def validar_cod(clave, valor):
    return validar_varchar(clave, valor, 8)


class custom_base(Base):
    """
    Clase base personalizada que contiene métodos para convertir objetos SQLAlchemy en diccionarios y listas.
    """

    __abstract__ = True  # Parámetro para omitir creación de tabla

    @classmethod
    def query(cls):
        """
        Crea un objeto para realizar consultas en la base de datos.
        """
        return db.session.query(cls)

    @staticmethod
    def to_list(items: list['custom_base'], excluir_none=False, *args) -> list[dict]:
        """
        Convierte una lista de objetos SQLAlchemy en una lista de diccionarios.

        Args:
            items (list[custom_base]): Lista de items a convertir en diccionarios y agregar a una lista.
            excluir_none (bool): Bandera para excluir atributos con valor None.
            *args (tuple[str, ...]): Tupla de cadenas con atributos que contienen listas de instancias relacionadas.
        Returns:
            list[dict]: Lista con diccionarios de los items.
        """

        return [item.to_dict(excluir_none, *args) for item in items]

    def to_dict(self, excluir_none=False, *args: tuple[str, ...]) -> dict:
        """
        Convierte un objeto SQLAlchemy en un diccionario.

        Args:
            excluir_none (bool): Bandera para excluir atributos con valor None.
            *args (tuple[str, ...]): Tupla de cadenas con atributos que contienen listas de instancias relacionadas.
        Returns:
            dict: Diccionario del objeto.
        """

        data = {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
        if excluir_none:
            data = {k: v for k, v in data.items() if v is not None}
        for arg in args:
            # Devuelve una lista de diccionarios para cada atributo especificado en *args
            data[arg] = [item.to_dict() for item in getattr(self, arg, [])]
        return data


class st_proceso(custom_base):
    """
    Modelo para representar la tabla 'st_proceso'.
    """

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

    @validates('empresa')
    def validar_empresa(self, key, value):
        return validar_empresa(key, value)

    @validates('cod_proceso')
    def validar_cod_proceso(self, key, value):
        return validar_cod(key, value)

    @validates('nombre')
    def validar_nombre(self, key, value):
        return validar_varchar(key, value, 30)


class st_formula(custom_base):
    """
    Modelo para representar la tabla 'st_formulas_procesos'.
    """

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

    @validates('empresa')
    def validar_empresa(self, key, value):
        return validar_empresa(key, value)

    @validates('cod_formula')
    def validar_cod_formula(self, key, value):
        return validar_cod(key, value)

    @validates('nombre')
    def validar_nombre(self, key, value):
        return validar_varchar(key, value, 100)

    @validates('observaciones')
    def validar_observaciones(self, key, value):
        if value is not None:
            return validar_varchar(key, value, 800)
        return value

    @validates('definicion')
    def validar_definicion(self, key, value):
        return validar_varchar(key, value, 2000)


class st_parametro(custom_base):
    """
    Modelo para representar la tabla 'st_parametros_formulas'.
    """

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

    @validates('empresa')
    def validar_empresa(self, key, value):
        return validar_empresa(key, value)

    @validates('cod_parametro')
    def validar_cod_parametro(self, key, value):
        return validar_cod(key, value)

    @validates('nombre')
    def validar_nombre(self, key, value):
        return validar_varchar(key, value, 60)

    @validates('descripcion')
    def validar_descripcion(self, key, value):
        if value is not None:
            return validar_varchar(key, value, 1000)
        return value


class st_parametros_x_proceso(custom_base):
    """
    Modelo para representar la tabla 'st_parametros_x_proceso'.
    """

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

    @validates('empresa')
    def validar_empresa(self, key, value):
        return validar_empresa(key, value)

    @validates('cod_proceso')
    def validar_cod_proceso(self, key, value):
        return validar_cod(key, value)

    @validates('cod_parametro')
    def validar_cod_parametro(self, key, value):
        return validar_cod(key, value)

    @validates('cod_formula')
    def validar_cod_formula(self, key, value):
        if value is not None:
            return validar_cod(key, value)
        return value

    @validates('orden_calculo')
    def validar_orden_calculo(self, key, value):
        if value is not None:
            return validar_number(key, value, 5)
        return value

    @validates('orden_imprime')
    def validar_orden_imprime(self, key, value):
        return validar_number(key, value, 5)


class st_factores_calculo_parametros(custom_base):
    """
    Modelo para representar la tabla 'st_factores_calc_parametros'.
    """

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

    @validates('empresa')
    def validar_empresa(self, key, value):
        return validar_empresa(key, value)

    @validates('cod_proceso')
    def validar_cod_proceso(self, key, value):
        return validar_cod(key, value)

    @validates('cod_parametro')
    def validar_cod_parametro(self, key, value):
        return validar_cod(key, value)

    @validates('orden')
    def validar_orden(self, key, value):
        if value is not None:
            return validar_number(key, value, 3)
        return value
