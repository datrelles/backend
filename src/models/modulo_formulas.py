from sqlalchemy import Column, DateTime, Index, VARCHAR, text, Integer, PrimaryKeyConstraint, ForeignKey, \
    ForeignKeyConstraint, column, inspect, Sequence, FetchedValue
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from src.config.database import db
from src.enums import tipo_estado, tipo_retorno, tipo_objeto, tipo_parametro, tipo_factor, operador
from src.enums.validation import paquete_funcion_bd, tipo_cliente
from src.validations import validar_varchar, validar_fecha, validar_number
from src.models.custom_base import custom_base

base = declarative_base(metadata=db.metadata)
schema_name = 'stock'


def validar_empresa(clave, valor):
    return validar_number(clave, valor, 2)


def validar_cod(clave, valor, es_requerido=True):
    codigo = validar_varchar(clave, valor, 8, es_requerido=es_requerido)
    return codigo.upper() if codigo else codigo


def validar_estado(clave, valor, es_requerido=True):
    return validar_number(clave, valor, 1, es_requerido=es_requerido, valores_permitidos=tipo_estado.values())


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


class st_formula_proceso(custom_base):
    __tablename__ = 'st_formula_proceso'
    __table_args__ = {'schema': schema_name}

    empresa = Column(NUMBER(precision=2), primary_key=True)
    cod_formula = Column(VARCHAR(8), primary_key=True)
    nombre = Column(VARCHAR(100), nullable=False)
    tipo_retorno = Column(VARCHAR(3), nullable=False)
    definicion = Column(VARCHAR(2000), nullable=False)
    descripcion = Column(VARCHAR(800))
    estado = Column(NUMBER(precision=1), nullable=False, server_default="1")
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

    @validates('tipo_retorno')
    def validar_tipo_retorno(self, key, value):
        return validar_varchar(key, value, 3, valores_permitidos=tipo_retorno.values())

    @validates('definicion')
    def validar_definicion(self, key, value):
        return validar_varchar(key, value, 2000)

    @validates('descripcion')
    def validar_descripcion(self, key, value):
        return validar_varchar(key, value, 800, es_requerido=False)

    @validates('estado')
    def validar_estado(self, key, value):
        return validar_estado(key, value)


class st_parametro_proceso(custom_base):
    __tablename__ = 'st_parametro_proceso'
    __table_args__ = {'schema': schema_name}

    empresa = Column(NUMBER(precision=2), primary_key=True)
    cod_parametro = Column(VARCHAR(8), primary_key=True)
    nombre = Column(VARCHAR(60), nullable=False)
    color = Column(VARCHAR(6), nullable=False)
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

    @validates('color')
    def validar_color(self, key, value):
        return validar_varchar(key, value, 8)

    @validates('estado')
    def validar_estado(self, key, value):
        return validar_estado(key, value)

    @validates('descripcion')
    def validar_descripcion(self, key, value):
        return validar_varchar(key, value, 1000, es_requerido=False)


class st_parametro_por_proceso(custom_base):
    __tablename__ = 'st_parametro_por_proceso'
    __table_args__ = (
        PrimaryKeyConstraint('empresa', 'cod_proceso', 'cod_parametro'),
        {'schema': schema_name}
    )

    empresa = Column(NUMBER(precision=2))
    cod_proceso = Column(VARCHAR(8), ForeignKey(f'{schema_name}.st_proceso.cod_proceso'), nullable=False)
    proceso = relationship('st_proceso')
    cod_parametro = Column(VARCHAR(8), ForeignKey(f'{schema_name}.st_parametro_proceso.cod_parametro'),
                           nullable=False)
    parametro = relationship('st_parametro_proceso')
    cod_formula = Column(VARCHAR(8), ForeignKey(f'{schema_name}.st_formula_proceso.cod_formula'))
    formula = relationship('st_formula_proceso')
    factores_calculo = relationship('st_factor_calculo_parametro',
                                    primaryjoin="and_(st_parametro_por_proceso.empresa == st_factor_calculo_parametro.empresa, "
                                                "st_parametro_por_proceso.cod_proceso == st_factor_calculo_parametro.cod_proceso, "
                                                "st_parametro_por_proceso.cod_parametro == st_factor_calculo_parametro.cod_parametro)",
                                    )
    orden_imprime = Column(NUMBER(precision=5), nullable=False)
    orden_calculo = Column(NUMBER(precision=5))
    fecha_calculo_inicio = Column(DateTime)
    fecha_calculo_fin = Column(DateTime)
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

    @validates('cod_parametro')
    def validar_cod_parametro(self, key, value):
        return validar_cod(key, value)

    @validates('cod_formula')
    def validar_cod_formula(self, key, value):
        return validar_cod(key, value, es_requerido=False)

    @validates('orden_imprime')
    def validar_orden_imprime(self, key, value):
        return validar_number(key, value, 5)

    @validates('orden_calculo')
    def validar_orden_calculo(self, key, value):
        return validar_number(key, value, 5, es_requerido=False)

    @validates('fecha_calculo_inicio')
    def validar_fecha_calculo_inicio(self, key, value):
        return validar_fecha(key, value, es_requerido=False)

    @validates('fecha_calculo_fin')
    def validar_fecha_calculo_fin(self, key, value):
        return validar_fecha(key, value, es_requerido=False)

    @validates('estado')
    def validar_estado(self, key, value):
        return validar_estado(key, value)


class st_factor_calculo_parametro(custom_base):
    __tablename__ = 'st_factor_calculo_parametro'
    __table_args__ = (
        PrimaryKeyConstraint('empresa', 'cod_proceso', 'cod_parametro', 'orden'),
        {'schema': schema_name}
    )

    empresa = Column(NUMBER(precision=2), ForeignKey(f'{schema_name}.st_parametro_por_proceso.empresa'), nullable=False)
    cod_proceso = Column(VARCHAR(8), ForeignKey(f'{schema_name}.st_parametro_por_proceso.cod_proceso'), nullable=False)
    cod_parametro = Column(VARCHAR(8), ForeignKey(f'{schema_name}.st_parametro_por_proceso.cod_parametro'),
                           nullable=False)
    orden = Column(NUMBER(precision=3))
    cod_parametro_tipo = Column(VARCHAR(8))
    tipo_factor = Column(VARCHAR(3), nullable=False)
    numero = Column(NUMBER(precision=22, scale=8))
    operador = Column(VARCHAR(1))
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

    @validates('cod_parametro_tipo')
    def validar_cod_parametro_tipo(self, key, value):
        return validar_cod(key, value, es_requerido=False)

    @validates('tipo_factor')
    def validar_tipo_factor(self, key, value):
        return validar_varchar(key, value, 3, valores_permitidos=tipo_factor.values())

    @validates('numero')
    def validar_numero(self, key, value):
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
    paquete = Column(VARCHAR(30), nullable=False)
    nombre = Column(VARCHAR(60), nullable=False)
    nombre_base_datos = Column(VARCHAR(30), nullable=False)
    tipo_retorno = Column(VARCHAR(3), nullable=False)
    tipo_objeto = Column(VARCHAR(3), nullable=False, server_default="FUN")
    descripcion = Column(VARCHAR(1000))
    estado = Column(NUMBER(precision=1), nullable=False, server_default="1")
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

    @validates('paquete')
    def validar_paquete(self, key, value):
        return validar_varchar(key, value, 30, valores_permitidos=paquete_funcion_bd.values())

    @validates('nombre')
    def validar_nombre(self, key, value):
        return validar_varchar(key, value, 60)

    @validates('nombre_base_datos')
    def validar_nombre_base_datos(self, key, value):
        return validar_varchar(key, value, 30)

    @validates('tipo_retorno')
    def validar_tipo_retorno(self, key, value):
        return validar_varchar(key, value, 3, valores_permitidos=tipo_retorno.values())

    @validates('tipo_objeto')
    def validar_tipo_objeto(self, key, value):
        return validar_varchar(key, value, 3, valores_permitidos=tipo_objeto.values())

    @validates('descripcion')
    def validar_descripcion(self, key, value):
        return validar_varchar(key, value, 1000, es_requerido=False)

    @validates('estado')
    def validar_estado(self, key, value):
        return validar_estado(key, value)


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
    numero = Column(NUMBER(precision=22, scale=8))
    texto = Column(VARCHAR(20))
    variable = Column(VARCHAR(10))
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

    @validates('numero')
    def validar_numero(self, key, value):
        return validar_number(key, value, 22, 8, es_requerido=False, es_positivo=False)

    @validates('texto')
    def validar_texto(self, key, value):
        return validar_varchar(key, value, 20, es_requerido=False)

    @validates('variable')
    def validar_variable(self, key, value):
        return validar_varchar(key, value, 10, es_requerido=False)


class st_cliente_procesos(custom_base):
    __tablename__ = 'st_cliente_procesos'
    __table_args__ = {'schema': schema_name}

    empresa = Column(NUMBER(precision=2), primary_key=True)
    cod_cliente = Column(VARCHAR(14), primary_key=True)
    cod_modelo = Column(VARCHAR(8), nullable=False)
    tipo_cliente = Column(VARCHAR(3), nullable=False)
    nombre_imprime = Column(VARCHAR(60), nullable=False)
    agrupa_cliente = Column(NUMBER(precision=1), nullable=False, server_default="0")
    nombre_agrupacion = Column(VARCHAR(60))
    audit_usuario_ing = Column(VARCHAR(30), nullable=False, server_default=text("user"))
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @validates('empresa')
    def validar_empresa(self, key, value):
        return validar_empresa(key, value)

    @validates('cod_cliente')
    def validar_cod_cliente(self, key, value):
        return validar_varchar(key, value, 14)

    @validates('cod_modelo')
    def validar_cod_modelo(self, key, value):
        return validar_varchar(key, value, 8, valores_permitidos=tipo_cliente.values())

    @validates('tipo_cliente')
    def validar_tipo_cliente(self, key, value):
        return validar_varchar(key, value, 3)

    @validates('nombre_imprime')
    def validar_nombre_imprime(self, key, value):
        return validar_varchar(key, value, 60)

    @validates('agrupa_cliente')
    def validar_agrupa_cliente(self, key, value):
        return validar_estado(key, value)

    @validates('nombre_agrupacion')
    def validar_nombre_agrupacion(self, key, value):
        return validar_varchar(key, value, 60, False)


class st_modelo_comercial():
    def __init__(self, codigo, codigo_marca, marca, nombre):
        self.codigo = codigo
        self.codigo_marca = codigo_marca
        self.marca = marca
        self.nombre = nombre

    @staticmethod
    def execute_sql(sql, es_escalar=True, params=None):
        if es_escalar:
            return db.session.execute(text(sql), params).scalar()
        else:
            return db.session.execute(text(sql), params)

    def to_dict(self):
        return {
            "codigo": self.codigo,
            "codigo_marca": self.codigo_marca,
            "marca": self.marca,
            "nombre": self.nombre
        }


class st_version_proyeccion(custom_base):
    __tablename__ = 'st_version_proyeccion'
    __table_args__ = {'schema': schema_name}

    empresa = Column(NUMBER(precision=2), primary_key=True)
    cod_version = Column(NUMBER(precision=22), primary_key=True, server_default=FetchedValue())
    nombre = Column(VARCHAR(100), nullable=False)
    audit_usuario_ing = Column(VARCHAR(30), nullable=False, server_default=text("user"))
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @validates('empresa')
    def validar_empresa(self, key, value):
        return validar_empresa(key, value)

    @validates('cod_version')
    def validar_cod_version(self, key, value):
        return validar_number(key, value, 22)

    @validates('nombre')
    def validar_nombre(self, key, value):
        return validar_varchar(key, value, 100)


class st_proyeccion_ppp(custom_base):
    __tablename__ = 'st_proyeccion_ppp'
    __table_args__ = {'schema': schema_name}

    empresa = Column(NUMBER(precision=2), primary_key=True)
    cod_version = Column(NUMBER(precision=22), primary_key=True)
    cod_proceso = Column(VARCHAR(8), primary_key=True)
    cod_parametro = Column(VARCHAR(8), primary_key=True)
    cod_modelo_comercial = Column(NUMBER(precision=14), primary_key=True)
    cod_marca = Column(NUMBER(precision=14), primary_key=True)
    cod_cliente = Column(VARCHAR(14), primary_key=True)
    anio = Column(NUMBER(precision=4), primary_key=True)
    mes = Column(NUMBER(precision=2), primary_key=True)
    numero = Column(NUMBER(precision=22, scale=8))
    texto = Column(VARCHAR(1000))
    fecha = Column(DateTime)
    audit_usuario_ing = Column(VARCHAR(30), nullable=False, server_default=text("user"))
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @validates('numero')
    def validar_numero(self, key, value):
        return validar_number(key, value, 22, 8, es_requerido=False)

    @validates('texto')
    def validar_texto(self, key, value):
        return validar_varchar(key, value, 100, es_requerido=False)

    @validates('fecha')
    def validar_fecha(self, key, value):
        return validar_fecha(key, value, 100, es_requerido=False)


class st_presupuesto_motos_pro(custom_base):
    __tablename__ = 'st_presup_motos_pro'
    __table_args__ = {'schema': schema_name}

    empresa = Column(NUMBER(precision=2), primary_key=True)
    cod_cliente = Column(VARCHAR(14), primary_key=True)
    cod_modelo = Column(VARCHAR(20), primary_key=True)
    anio = Column(NUMBER(precision=4), primary_key=True)
    mes = Column(NUMBER(precision=2), primary_key=True)
    unidades = Column(NUMBER(precision=22, scale=2), nullable=False)
    sell_out = Column(NUMBER(precision=22, scale=2))
    cod_linea = Column(VARCHAR(4))
    cod_tipo_linea = Column(VARCHAR(4))
    audit_usuario_ing = Column(VARCHAR(30), nullable=False, server_default=text("user"))
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @validates('empresa')
    def validar_empresa(self, key, value):
        return validar_empresa(key, value)

    @validates('cod_cliente')
    def validar_cod_cliente(self, key, value):
        return (validar_varchar(key, value, 14))

    @validates('cod_modelo')
    def validar_cod_modelo(self, key, value):
        return (validar_varchar(key, value, 20))

    @validates('anio')
    def validar_anio(self, key, value):
        return validar_number(key, value, 4)

    @validates('mes')
    def validar_mes(self, key, value):
        return validar_number(key, value, 2)

    @validates('unidades')
    def validar_unidades(self, key, value):
        return validar_number(key, value, 22, 2)

    @validates('sell_out')
    def validar_sell_out(self, key, value):
        return validar_number(key, value, 22, 2)

    @validates('cod_linea')
    def validar_cod_linea(self, key, value):
        return validar_varchar(key, value, 4, es_requerido=False)

    @validates('cod_tipo_linea')
    def validar_cod_tipo_linea(self, key, value):
        return validar_varchar(key, value, 4, es_requerido=False)


class st_presupuesto_motos_tipo_cli_pro(custom_base):
    __tablename__ = 'st_presup_motos_tipo_cli_pro'
    __table_args__ = {'schema': schema_name}

    empresa = Column(NUMBER(precision=2), primary_key=True)
    cod_tipo_cliente = Column(VARCHAR(14), primary_key=True)
    cod_modelo = Column(VARCHAR(20), primary_key=True)
    anio = Column(NUMBER(precision=4), primary_key=True)
    mes = Column(NUMBER(precision=2), primary_key=True)
    unidades = Column(NUMBER(precision=22, scale=2), nullable=False)
    sell_out = Column(NUMBER(precision=22, scale=2))
    audit_usuario_ing = Column(VARCHAR(30), nullable=False, server_default=text("user"))
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @validates('empresa')
    def validar_empresa(self, key, value):
        return validar_empresa(key, value)

    @validates('cod_tipo_cliente')
    def validar_cod_tipo_cliente(self, key, value):
        return (validar_varchar(key, value, 3))

    @validates('cod_modelo')
    def validar_cod_modelo(self, key, value):
        return (validar_varchar(key, value, 20))

    @validates('anio')
    def validar_anio(self, key, value):
        return validar_number(key, value, 4)

    @validates('mes')
    def validar_mes(self, key, value):
        return validar_number(key, value, 2)

    @validates('unidades')
    def validar_unidades(self, key, value):
        return validar_number(key, value, 22, 2)

    @validates('sell_out')
    def validar_sell_out(self, key, value):
        return validar_number(key, value, 22, 2)
