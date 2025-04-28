import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

def configure_logging(app):

    log_level = os.getenv('LOGGING_LEVEL', 'INFO').upper()
    log_file_path = os.getenv('LOGGING_FILE_PATH', '/home/backend/logs/backend.log')
    max_bytes = int(os.getenv('LOGGING_MAX_BYTES', 5242880))  # 5MB
    backup_count = int(os.getenv('LOGGING_BACKUP_COUNT', 5))

    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    handler = RotatingFileHandler(log_file_path, maxBytes=max_bytes, backupCount=backup_count)
    handler.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    handler.setFormatter(formatter)

    if not app.logger.handlers:
        app.logger.addHandler(handler)

    app.logger.setLevel(log_level)

    app.logger.info('Logging configurado correctamente.')
