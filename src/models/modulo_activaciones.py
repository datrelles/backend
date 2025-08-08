from sqlalchemy import Column, text, VARCHAR, DateTime
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.orm import declarative_base, validates
from src.config.database import db
from src.enums import tipo_estado
from src.models.custom_base import custom_base
from src.validations import validar_number, validar_varchar
from src.validations.alfanumericas import validar_hora

base = declarative_base(metadata=db.metadata)
schema_name = 'stock'


def validar_empresa(clave, valor):
    return validar_number(clave, valor, 2)


def validar_estado(clave, valor, es_requerido=True):
    return validar_number(clave, valor, 1, es_requerido=es_requerido, valores_permitidos=tipo_estado.values())


class st_activacion(custom_base):
    __tablename__ = 'st_activacion'
    __table_args__ = {'schema': schema_name}

    cod_activacion = Column(NUMBER(precision=22), primary_key=True)
    empresa = Column(NUMBER(precision=2))
    cod_promotor = Column(VARCHAR(20))
    cod_tienda = Column(NUMBER(precision=2))
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

    @validates('cod_tienda')
    def validar_cod_tienda(self, key, value):
        return validar_number(key, value, 2)

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

    @validates('total_minutos')
    def validar_total_minutos(self, key, value):
        return validar_number(key, value, 4, 0)

    @validates('num_exhi_motos')
    def validar_num_exhi_motos(self, key, value):
        return validar_number(key, value, 3, 0)
