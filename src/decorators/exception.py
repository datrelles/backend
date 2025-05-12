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
            except SQLAlchemyError as e:
                db.session.rollback()
                error_message = ""
                orig = getattr(e, 'orig', None)
                if isinstance(orig, DatabaseError):
                    error_obj, = orig.args
                    error_code = error_obj.code
                    if 20000 <= error_code <= 20999:
                        parts = error_obj.message.split(':', 2)
                        error_message = parts[2].strip().split('\n', 1)[0] if len(parts) == 3 else error_obj.message
                logger.exception(f'Ocurrió una excepción con la base de datos al {action}: {e}')
                return jsonify(
                    {
                        'mensaje': f'Ocurrió un error con la base de datos al {action}{f': {error_message}' if error_message else ''}'}), 500
            except Exception as e:
                db.session.rollback()
                logger.exception(f'Ocurrió una excepción al {action}: {e}')
                return jsonify(
                    {'mensaje': f'Ocurrió un error al {action}'}), 500

        return wrapper

    return decorator
