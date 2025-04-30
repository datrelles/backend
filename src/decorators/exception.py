from functools import wraps
import logging
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
                logger.exception(f'Ocurrió una excepción con la base de datos al {action}: {e}')
                return jsonify(
                    {'mensaje': f'Ocurrió un error con la base de datos al {action}'}), 500
            except Exception as e:
                db.session.rollback()
                logger.exception(f'Ocurrió una excepción al {action}: {e}')
                return jsonify(
                    {'mensaje': f'Ocurrió un error al {action}'}), 500

        return wrapper

    return decorator
