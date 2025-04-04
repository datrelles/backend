from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db
from src.exceptions.validation import validation_error

base = declarative_base(metadata=db.metadata)


class custom_base(base):
    __abstract__ = True

    def __init__(self, **kwargs):
        requeridos = {
            col.name for col in self.__table__.columns if
            not col.nullable and col.default is None and col.server_default is None
        }
        faltantes = requeridos - kwargs.keys()
        if faltantes:
            raise validation_error(campos=faltantes)
        super().__init__(**kwargs)

    @classmethod
    def query(cls):
        return db.session.query(cls)

    @staticmethod
    def to_list(items: list['custom_base'], excluir_none=False, *args) -> list[dict]:
        return [item.to_dict(excluir_none, *args) for item in items]

    def to_dict(self, excluir_none=False, *args: tuple[str, ...]) -> dict:
        data = {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
        if excluir_none:
            data = {k: v for k, v in data.items() if v is not None}
        for arg in args:
            data[arg] = [item.to_dict() for item in getattr(self, arg, [])]
        return data
