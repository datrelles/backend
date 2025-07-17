# db_connection.py
from src import oracle # tu wrapper, o cambia a cx_Oracle si usas directo
from os import getenv

def get_oracle_connection():
    """
    Returns a new Oracle database connection using environment variables.
    """
    user = getenv("USERORA")
    password = getenv("PASSWORD")
    # Puedes agregar aquí más config, como host/DSN/port si lo necesitas
    return oracle.connection(user, password)


