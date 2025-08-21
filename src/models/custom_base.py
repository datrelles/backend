from collections.abc import Iterable

from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db
from sqlalchemy import text, inspect
from src.exceptions import validation_error

base = declarative_base(metadata=db.metadata)


def es_objeto_mapeado(obj):
    try:
        inspect(obj)
        return True
    except NoInspectionAvailable:
        return False


class custom_base(base):
    __abstract__ = True

    def __init__(self, **kwargs):
        requeridos = {
            col.name for col in self.__table__.columns if
            not col.nullable and col.default is None and col.server_default is None
        }
        keys = kwargs.keys()
        faltantes = requeridos - keys
        if faltantes:
            raise validation_error(faltantes=faltantes)
        no_requeridos = set()
        for key in keys - requeridos:
            columna = self.__table__.columns.get(key)
            if columna is None or (columna is not None and columna.server_default is not None):
                no_requeridos.add(key)
        if no_requeridos:
            raise validation_error(no_requeridos=no_requeridos)
        super().__init__(**kwargs)

    @classmethod
    def query(cls):
        return db.session.query(cls)

    @staticmethod
    def to_list(items: list['custom_base'], atributos_anidados: list = None, excluir_none=False) -> list[dict]:
        return [item.to_dict(atributos_anidados, excluir_none) for item in items]

    def to_dict(self, atributos_anidados: list = None, excluir_none=False) -> dict:
        data = {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
        if excluir_none:
            data = {k: v for k, v in data.items() if v is not None}
        if atributos_anidados:
            for atr_ani in atributos_anidados:
                atributo = getattr(self, atr_ani, None)
                if atributo is None:
                    data[atr_ani] = None
                else:
                    data[atr_ani] = [
                        item.to_dict() if getattr(item, 'to_dict', None) else {c.key: getattr(item, c.key) for c in
                                                                               inspect(item).mapper.column_attrs} for
                        item in atributo] if isinstance(atributo, Iterable) else atributo.to_dict() if getattr(atributo,
                                                                                                               'to_dict',
                                                                                                               None) else {
                        c.key: getattr(atributo, c.key) for c in inspect(atributo).mapper.column_attrs}
        return data

    @staticmethod
    def execute_sql(sql, es_escalar=True, **kwargs):
        if es_escalar:
            return db.session.execute(text(sql), **kwargs).scalar()
        else:
            return db.session.execute(text(sql), **kwargs)
