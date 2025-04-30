from sqlalchemy import Column, DateTime, Index, VARCHAR, text, Integer, PrimaryKeyConstraint, ForeignKey, \
    ForeignKeyConstraint, column, inspect
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from src.config.database import db
from src.enums import tipo_estado, tipo_retorno, tipo_objeto, tipo_parametro
from src.validations import validar_varchar, validar_fecha, validar_number
from src.models.custom_base import custom_base

base = declarative_base(metadata=db.metadata)
schema_name = 'stock'


def validar_empresa(clave, valor):
    return validar_number(clave, valor, 2)


def validar_cod(clave, valor, es_requerido=True):
    return validar_varchar(clave, valor, 8, es_requerido=es_requerido)


def validar_estado(clave, valor, es_requerido=True):
    return validar_number(clave, valor, 1, valores_permitidos=tipo_estado.values())


class st_proceso(custom_base):
    __tablename__ = 'st_proceso'
    __table_args__ = {'schema': schema_name}

    empresa = Column(NUMBER(precision=2), primary_key=True)
    cod_proceso = Column(VARCHAR(8), primary_key=True)
    nombre = Column(VARCHAR(30), nullable=False)
    estado = Column(NUMBER(precision=1), nullable=False, server_default="1")
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

    @validates('estado')
    def validar_estado(self, key, value):
        return validar_estado(key, value)


class st_formula(custom_base):
    __tablename__ = 'st_formulas_procesos'
    __table_args__ = {'schema': schema_name}

    empresa = Column(NUMBER(precision=2), primary_key=True)
    cod_formula = Column(VARCHAR(8), primary_key=True)
    nombre = Column(VARCHAR(100), nullable=False)
    observaciones = Column(VARCHAR(800))
    estado = Column(NUMBER(precision=1), nullable=False, server_default="1")
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
        return validar_varchar(key, value, 800, es_requerido=False)

    @validates('estado')
    def validar_estado(self, key, value):
        return validar_estado(key, value)

    @validates('definicion')
    def validar_definicion(self, key, value):
        return validar_varchar(key, value, 2000)


class st_parametro(custom_base):
    __tablename__ = 'st_parametros_formulas'
    __table_args__ = {'schema': schema_name}

    empresa = Column(NUMBER(precision=2), primary_key=True)
    cod_parametro = Column(VARCHAR(8), primary_key=True)
    nombre = Column(VARCHAR(60), nullable=False)
    descripcion = Column(VARCHAR(1000))
    estado = Column(NUMBER(precision=1), nullable=False, server_default="1")
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
        return validar_varchar(key, value, 1000, es_requerido=False)

    @validates('estado')
    def validar_estado(self, key, value):
        return validar_estado(key, value)


class st_parametros_x_proceso(custom_base):
    __tablename__ = 'st_parametros_x_proceso'
    __table_args__ = (
        PrimaryKeyConstraint('empresa', 'cod_proceso', 'cod_parametro'),
        {'schema': schema_name}
    )

    empresa = Column(NUMBER(precision=2))
    cod_proceso = Column(VARCHAR(8), ForeignKey(f'{schema_name}.st_proceso.cod_proceso'), nullable=False)
    proceso = relationship('st_proceso')
    cod_parametro = Column(VARCHAR(8), ForeignKey(f'{schema_name}.st_parametros_formulas.cod_parametro'),
                           nullable=False)
    parametro = relationship('st_parametro')
    cod_formula = Column(VARCHAR(8), ForeignKey(f'{schema_name}.st_formulas_procesos.cod_formula'))
    formula = relationship('st_formula')
    factores_calculo = relationship('st_factores_calculo_parametros',
                                    primaryjoin="and_(st_parametros_x_proceso.empresa == st_factores_calculo_parametros.empresa, "
                                                "st_parametros_x_proceso.cod_proceso == st_factores_calculo_parametros.cod_proceso, "
                                                "st_parametros_x_proceso.cod_parametro == st_factores_calculo_parametros.cod_parametro)",
                                    )
    orden_calculo = Column(NUMBER(precision=5))
    estado = Column(NUMBER(precision=1), nullable=False, server_default="1")
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
        return validar_cod(key, value, es_requerido=False)

    @validates('orden_calculo')
    def validar_orden_calculo(self, key, value):
        return validar_number(key, value, 5, es_requerido=False)

    @validates('estado')
    def validar_estado(self, key, value):
        return validar_estado(key, value)

    @validates('fecha_calculo_inicio')
    def validar_fecha_calculo_inicio(self, key, value):
        return validar_fecha(key, value, es_requerido=False)

    @validates('fecha_calculo_fin')
    def validar_fecha_calculo_fin(self, key, value):
        return validar_fecha(key, value, es_requerido=False)

    @validates('orden_imprime')
    def validar_orden_imprime(self, key, value):
        return validar_number(key, value, 5)


class st_factores_calculo_parametros(custom_base):
    __tablename__ = 'st_factores_calc_parametros'
    __table_args__ = (
        PrimaryKeyConstraint('empresa', 'cod_proceso', 'cod_parametro', 'orden'),
        {'schema': schema_name}
    )

    empresa = Column(NUMBER(precision=2), ForeignKey(f'{schema_name}.st_parametros_x_proceso.empresa'), nullable=False)
    cod_proceso = Column(VARCHAR(8), ForeignKey(f'{schema_name}.st_parametros_x_proceso.cod_proceso'), nullable=False)
    cod_parametro = Column(VARCHAR(8), ForeignKey(f'{schema_name}.st_parametros_x_proceso.cod_parametro'),
                           nullable=False)
    orden = Column(NUMBER(precision=3))
    tipo_operador = Column(VARCHAR(3), nullable=False)
    operador = Column(VARCHAR(1))
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
        return (validar_number(key, value, 3))

    @validates('valor_fijo')
    def validar_valor_fijo(self, key, value):
        return validar_number(key, value, 22, 8, False, es_positivo=False)


class tg_sistema(custom_base):
    __tablename__ = 'tg_sistema'
    __table_args__ = {'schema': 'computo'}

    cod_sistema = Column(VARCHAR(3), primary_key=True)
    sistema = Column(VARCHAR(50))
    ruta = Column(VARCHAR(200))


class st_funcion(custom_base):
    __tablename__ = 'st_funcion'
    __table_args__ = (
        PrimaryKeyConstraint('empresa', 'cod_funcion'),
        {'schema': schema_name}
    )

    empresa = Column(NUMBER(precision=2))
    cod_funcion = Column(VARCHAR(8))
    cod_modulo = Column(VARCHAR(3), ForeignKey(f'computo.tg_sistema.cod_sistema'), nullable=False)
    nombre = Column(VARCHAR(60), nullable=False)
    nombre_base_datos = Column(VARCHAR(60), nullable=False)
    estado = Column(NUMBER(precision=1), nullable=False, server_default="1")
    observaciones = Column(VARCHAR(1000))
    tipo_retorno = Column(VARCHAR(8), nullable=False)
    tipo_objeto = Column(VARCHAR(3), nullable=False, server_default="FUN")
    audit_usuario_ing = Column(VARCHAR(30), nullable=False, server_default=text("user"))
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @validates('empresa')
    def validar_empresa(self, key, value):
        return validar_empresa(key, value)

    @validates('cod_funcion')
    def validar_cod_funcion(self, key, value):
        return validar_cod(key, value)

    @validates('cod_modulo')
    def validar_cod_modulo(self, key, value):
        return validar_varchar(key, value, 3)

    @validates('nombre')
    def validar_nombre(self, key, value):
        return validar_varchar(key, value, 60)

    @validates('nombre_base_datos')
    def validar_nombre_base_datos(self, key, value):
        return validar_varchar(key, value, 60)

    @validates('estado')
    def validar_estado(self, key, value):
        return validar_estado(key, value)

    @validates('observaciones')
    def validar_observaciones(self, key, value):
        return validar_varchar(key, value, 1000, es_requerido=False)

    @validates('tipo_retorno')
    def validar_tipo_retorno(self, key, value):
        return validar_varchar(key, value, 8, valores_permitidos=tipo_retorno.values())

    @validates('tipo_objeto')
    def validar_tipo_objeto(self, key, value):
        return validar_varchar(key, value, 3, valores_permitidos=tipo_objeto.values())


class st_parametro_funcion(custom_base):
    __tablename__ = 'st_parametro_funcion'
    __table_args__ = (
        PrimaryKeyConstraint('empresa', 'cod_funcion', 'secuencia'),
        {'schema': schema_name}
    )

    empresa = Column(NUMBER(precision=2), ForeignKey(f'{schema_name}.st_funcion.empresa'))
    cod_funcion = Column(VARCHAR(8), ForeignKey(f'{schema_name}.st_funcion.cod_funcion'))
    secuencia = Column(NUMBER(precision=10))
    tipo_parametro = Column(VARCHAR(30), nullable=False)
    variable = Column(VARCHAR(10))
    fijo_caracter = Column(VARCHAR(20))
    fijo_numero = Column(NUMBER(precision=30, scale=8))
    audit_usuario_ing = Column(VARCHAR(30), nullable=False, server_default=text("user"))
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @validates('empresa')
    def validar_empresa(self, key, value):
        return validar_empresa(key, value)

    @validates('cod_funcion')
    def validar_cod_funcion(self, key, value):
        return validar_cod(key, value)

    @validates('secuencia')
    def validar_secuencia(self, key, value):
        return validar_number(key, value, 10)

    @validates('tipo_parametro')
    def validar_tipo_parametro(self, key, value):
        return validar_varchar(key, value, 30, valores_permitidos=tipo_parametro.values())

    @validates('variable')
    def validar_variable(self, key, value):
        return validar_varchar(key, value, 10, es_requerido=False)

    @validates('fijo_caracter')
    def validar_fijo_caracter(self, key, value):
        return validar_varchar(key, value, 20, es_requerido=False)

    @validates('fijo_numero')
    def validar_fijo_numero(self, key, value):
        return validar_number(key, value, 22, 8, es_requerido=False, es_positivo=False)
