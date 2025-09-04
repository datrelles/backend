from sqlalchemy import Column, DateTime, Index, VARCHAR, text, Integer, PrimaryKeyConstraint, ForeignKey, \
    ForeignKeyConstraint, column
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from src.config.database import db
from src.enums import categoria_excepcion, tipo_estado
from src.exceptions import validation_error
from src.validations import validar_varchar, validar_number
from src.models.custom_base import custom_base

base = declarative_base(metadata=db.metadata)
schema_name = 'stock'


def validar_empresa(clave, valor):
    return validar_number(clave, valor, 2)


def validar_cod_14(clave, valor):
    return validar_varchar(clave, valor, 14)


def validar_estado(clave, valor, es_requerido=True):
    return validar_number(clave, valor, 1, valores_permitidos=tipo_estado.values())


class st_cabecera_consignacion(custom_base):
    __tablename__ = 'st_cab_param_consig'
    __table_args__ = {'schema': schema_name}

    empresa = Column(NUMBER(precision=2), primary_key=True)
    cod_cliente = Column(VARCHAR(14), primary_key=True)
    max_unidades = Column(NUMBER(precision=6), nullable=False)
    tiempo_repo = Column(NUMBER(precision=6), nullable=False)
    estado = Column(NUMBER(precision=1), nullable=False, server_default="1")
    audit_usuario_ing = Column(VARCHAR(30), nullable=False)
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @validates('empresa')
    def validar_empresa(self, key, value):
        return validar_empresa(key, value)

    @validates('cod_cliente')
    def validar_cod_cliente(self, key, value):
        return validar_cod_14(key, value)

    @validates('max_unidades')
    def validar_max_unidades(self, key, value):
        return validar_number(key, value, 6)

    @validates('tiempo_repo')
    def validar_tiempo_repo(self, key, value):
        return validar_number(key, value, 6)

    @validates('estado')
    def validar_estado(self, key, value):
        return validar_estado(key, value)


class st_detalle_consignacion(custom_base):
    __tablename__ = 'st_det_param_consig'
    __table_args__ = {'schema': schema_name}

    empresa = Column(NUMBER(precision=2), primary_key=True)
    cod_cliente = Column(VARCHAR(14), primary_key=True)
    cod_agencia = Column(NUMBER(4), primary_key=True)
    cod_modelo_version = Column(VARCHAR(14), primary_key=True)
    porcentaje_part = Column(NUMBER(precision=5, scale=2), nullable=False)
    tiempo_repo = Column(NUMBER(precision=6), nullable=False)
    audit_usuario_ing = Column(VARCHAR(30), nullable=False)
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @validates('empresa')
    def validar_empresa(self, key, value):
        return validar_empresa(key, value)

    @validates('cod_cliente')
    def validar_cod_cliente(self, key, value):
        return validar_cod_14(key, value)

    @validates('cod_agencia')
    def validar_cod_agencia(self, key, value):
        return validar_number(key, value, 4)

    @validates('cod_modelo_version')
    def validar_cod_modelo_version(self, key, value):
        return validar_cod_14(key, value)

    @validates('porcentaje_part')
    def validar_porcentaje_part(self, key, value):
        return validar_number(key, value, 5, 2)

    @validates('tiempo_repo')
    def validar_tiempo_repo(self, key, value):
        return validar_number(key, value, 6)
