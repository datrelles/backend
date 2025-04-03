from sqlalchemy.ext.declarative import declarative_base
from src.config.database import db

base = declarative_base(metadata=db.metadata)


class custom_base(base):
    __abstract__ = True

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
