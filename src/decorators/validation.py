from functools import wraps
import logging
from flask import request
from flask import jsonify
from werkzeug.exceptions import BadRequest

logger = logging.getLogger(__name__)


def validate_json():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            mensaje = 'La información proporcionada'
            try:
                data = request.get_json()
                if isinstance(data, dict):
                    return func(*args, data=data, **kwargs)
                mensaje = '{} está incompleta'.format(mensaje)
            except BadRequest:
                mensaje = '{} tiene un formato inválido'.format(mensaje)
            logger.error(mensaje)
            return jsonify({'mensaje': mensaje}), 400

        return wrapper

    return decorator
