from src.exceptions.validation import categoria_excepcion, validation_error
from datetime import datetime


def validar_varchar(clave, valor, longitud, es_requerido=True, valores_permitidos=None):
    if es_requerido:
        if valor is None:
            raise validation_error(campo=clave, categoria=categoria_excepcion.faltante.value)
        if valor == '':
            raise validation_error(campo=clave, categoria=categoria_excepcion.vacio.value)
    else:
        if valor == '' or valor is None:
            return None
    if not isinstance(valor, str):
        raise validation_error(campo=clave, categoria=categoria_excepcion.tipo.value)
    if len(valor) > longitud:
        raise validation_error(campo=clave, categoria=categoria_excepcion.longitud.value, longitud=longitud)
    if valores_permitidos and valor not in valores_permitidos:
        raise validation_error(campo=clave, categoria=categoria_excepcion.valores_permitidos.value,
                               valores_permitidos=valores_permitidos)
    return valor


def validar_fecha(clave, valor, es_requerido=True, formato="%Y-%m-%d"):
    if es_requerido:
        if valor is None:
            raise validation_error(campo=clave, categoria=categoria_excepcion.faltante.value)
        if valor == '':
            raise validation_error(campo=clave, categoria=categoria_excepcion.vacio.value)
    else:
        if valor == '' or valor is None:
            return None
    try:
        return datetime.strptime(valor, formato)
    except Exception:
        raise validation_error(campo=clave, categoria=categoria_excepcion.tipo.value)
