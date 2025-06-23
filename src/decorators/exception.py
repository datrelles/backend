from functools import wraps
import logging

from cx_Oracle import DatabaseError
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from src.config.database import db
from src.exceptions import validation_error

logger = logging.getLogger(__name__)


def handle_exceptions(action):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except validation_error as e:
                logger.exception(e)
                return jsonify({'mensaje': str(e)}), 400
            except TypeError as e:
                logger.exception(e)
                return jsonify({'mensaje': 'Los parámetros provistos al recurso de la API son incorrectos'}), 400
            except SQLAlchemyError as e:
                db.session.rollback()
                status_code = 500
                mensaje = f'Ocurrió un error con la base de datos al {action}'
                orig = getattr(e, 'orig', None)
                if isinstance(orig, DatabaseError):
                    error_obj, = orig.args
                    error_code = error_obj.code
                    if 20000 <= error_code <= 20999:
                        status_code = 400
                        parts = [part.strip() for part in error_obj.message.split(':')]
                        for part in parts:
                            if not part.startswith('ORA-'):
                                mensaje = part.split('\n')[0]
                                break
                    elif error_code == 12571:
                        mensaje = "Se perdió conexión con la base de datos"
                logger.exception(f'Ocurrió una excepción con la base de datos al {action}: {e}')
                return jsonify({'mensaje': mensaje}), status_code
            except Exception as e:
                db.session.rollback()
                logger.exception(f'Ocurrió una excepción al {action}: {e}')
                return jsonify(
                    {'mensaje': f'Ocurrió un error al {action}'}), 500

        return wrapper

    return decorator
