from sqlalchemy import Column, text, VARCHAR, DateTime, FetchedValue, ForeignKey, ForeignKeyConstraint, and_
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.orm import declarative_base, validates, relationship, foreign
from src.config.database import db
from src.enums import tipo_estado
from src.models.clientes import Cliente
from src.models.custom_base import custom_base
from src.validations import validar_number, validar_varchar, validar_fecha
from src.validations.alfanumericas import validar_hora

base = declarative_base(metadata=db.metadata)
schema_name = 'stock'


def validar_empresa(clave, valor):
    return validar_number(clave, valor, 2)


def validar_estado(clave, valor, es_requerido=True):
    return validar_number(clave, valor, 1, es_requerido=es_requerido, valores_permitidos=tipo_estado.values())


class st_cliente_direccion_guias(custom_base):
    __tablename__ = 'st_cliente_direccion_guias'
    __table_args__ = {'schema': schema_name}

    empresa = Column(NUMBER(precision=2), primary_key=True)
    cod_cliente = Column(VARCHAR(14), primary_key=True)
    cod_direccion = Column(NUMBER(precision=3), primary_key=True)
    ciudad = Column(VARCHAR(200), nullable=False)
    direccion = Column(VARCHAR(200))
    direccion_larga = Column(VARCHAR(500))
    cod_zona_ciudad = Column(VARCHAR(14))
    es_activo = Column(NUMBER(precision=1), default=1)
    nombre = Column(VARCHAR(100))

    @validates('empresa')
    def validar_empresa(self, key, value):
        return validar_empresa(key, value)

    @validates('cod_cliente')
    def validar_cod_cliente(self, key, value):
        return validar_varchar(key, value, 14)

    @validates('cod_direccion')
    def validar_cod_direccion(self, key, value):
        return validar_number(key, value, 3)

    @validates('ciudad')
    def validar_ciudad(self, key, value):
        return validar_varchar(key, value, 200)

    @validates('direccion')
    def validar_direccion(self, key, value):
        return validar_varchar(key, value, 200, False)

    @validates('direccion_larga')
    def validar_direccion_larga(self, key, value):
        return validar_varchar(key, value, 200, False)

    @validates('cod_zona_ciudad')
    def validar_cod_zona_ciudad(self, key, value):
        return validar_varchar(key, value, 14, False)

    @validates('es_activo')
    def validar_es_activo(self, key, value):
        return validar_number(key, value, 1)

    @validates('nombre')
    def validar_nombre(self, key, value):
        return validar_varchar(key, value, 100, False)


class st_activacion(custom_base):
    __tablename__ = 'st_activacion'
    __table_args__ = (
        ForeignKeyConstraint(['empresa', 'cod_cliente'],
                             ['cliente.empresa', 'cliente.cod_cliente']),
        ForeignKeyConstraint(['empresa', 'cod_cliente', 'cod_tienda'],
                             ['{}.st_cliente_direccion_guias.empresa'.format(schema_name),
                              '{}.st_cliente_direccion_guias.cod_cliente'.format(schema_name),
                              '{}.st_cliente_direccion_guias.cod_direccion'.format(schema_name)]),
        {'schema': schema_name})

    cod_activacion = Column(NUMBER(precision=22), primary_key=True, server_default=FetchedValue())
    empresa = Column(NUMBER(precision=2))
    cod_promotor = Column(VARCHAR(20))
    cod_cliente = Column(VARCHAR(14))
    cliente = relationship(
        Cliente,
        foreign_keys=[empresa, cod_cliente]
    )
    cod_tienda = Column(NUMBER(precision=3))
    tienda = relationship(st_cliente_direccion_guias,
                          foreign_keys=[empresa, cod_cliente, cod_tienda])
    cod_proveedor = Column(VARCHAR(14))
    cod_modelo_act = Column(VARCHAR(8))
    cod_item_act = Column(VARCHAR(3))
    animadora = Column(VARCHAR(150), nullable=False)
    hora_inicio = Column(VARCHAR(5), nullable=False)
    hora_fin = Column(VARCHAR(5), nullable=False)
    fecha_act = Column(DateTime, nullable=False)
    total_minutos = Column(NUMBER(precision=4))
    num_exhi_motos = Column(NUMBER(precision=3))
    audit_usuario_ing = Column(VARCHAR(30), nullable=False, server_default=text("user"))
    audit_fecha_ing = Column(DateTime, nullable=False, server_default=text("sysdate"))
    audit_usuario_mod = Column(VARCHAR(30))
    audit_fecha_mod = Column(DateTime)

    @validates('cod_activacion')
    def validar_cod_activacion(self, key, value):
        return validar_number(key, value, 22)

    @validates('empresa')
    def validar_empresa(self, key, value):
        return validar_empresa(key, value)

    @validates('cod_promotor')
    def validar_cod_promotor(self, key, value):
        return validar_varchar(key, value, 20)

    @validates('cod_cliente')
    def validar_cod_cliente(self, key, value):
        return validar_varchar(key, value, 14)

    @validates('cod_tienda')
    def validar_cod_tienda(self, key, value):
        return validar_number(key, value, 3)

    @validates('cod_proveedor')
    def validar_cod_proveedor(self, key, value):
        return validar_varchar(key, value, 14)

    @validates('cod_modelo_act')
    def validar_cod_modelo_act(self, key, value):
        return validar_varchar(key, value, 8)

    @validates('cod_item_act')
    def validar_cod_item_act(self, key, value):
        return validar_varchar(key, value, 3)

    @validates('animadora')
    def validar_animadora(self, key, value):
        return validar_varchar(key, value, 150)

    @validates('hora_inicio')
    def validar_hora_inicio(self, key, value):
        return validar_hora(key, value)

    @validates('hora_fin')
    def validar_hora_fin(self, key, value):
        return validar_hora(key, value)

    @validates('fecha_act')
    def validar_fecha_act(self, key, value):
        return validar_fecha(key, value)

    @validates('num_exhi_motos')
    def validar_num_exhi_motos(self, key, value):
        return validar_number(key, value, 3, 0)
