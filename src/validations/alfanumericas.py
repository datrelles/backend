from src.exceptions import validation_error
from src.enums import categoria_excepcion
from datetime import datetime


def validar_varchar(clave, valor, longitud, es_requerido=True, valores_permitidos=None):
    if es_requerido:
        if valor is None:
            raise validation_error(campo=clave, categoria=categoria_excepcion.FALTANTE.value)
        if valor == '':
            raise validation_error(campo=clave, categoria=categoria_excepcion.VACIO.value)
    else:
        if valor == '' or valor is None:
            return None
    if not isinstance(valor, str):
        raise validation_error(campo=clave, categoria=categoria_excepcion.TIPO.value)
    if len(valor) > longitud:
        raise validation_error(campo=clave, categoria=categoria_excepcion.LONGITUD.value, longitud=longitud)
    if valores_permitidos and valor not in valores_permitidos:
        raise validation_error(campo=clave, categoria=categoria_excepcion.VALORES_PERMITIDOS.value,
                               valores_permitidos=valores_permitidos)
    return valor


def validar_fecha(clave, valor, es_requerido=True, formato="%Y-%m-%d"):
    if es_requerido:
        if valor is None:
            raise validation_error(campo=clave, categoria=categoria_excepcion.FALTANTE.value)
        if valor == '':
            raise validation_error(campo=clave, categoria=categoria_excepcion.VACIO.value)
    else:
        if valor == '' or valor is None:
            return None
    try:
        return datetime.strptime(valor, formato)
    except Exception:
        raise validation_error(campo=clave, categoria=categoria_excepcion.TIPO.value)


def validar_hora(clave, valor, es_requerido=True, formato="%H:%M", devuelve_string=True):
    if es_requerido:
        if valor is None:
            raise validation_error(campo=clave, categoria=categoria_excepcion.FALTANTE.value)
        if valor == '':
            raise validation_error(campo=clave, categoria=categoria_excepcion.VACIO.value)
    else:
        if valor == '' or valor is None:
            return None
    try:
        nuevo_valor = datetime.strptime(valor, formato)
        return valor if devuelve_string else nuevo_valor
    except Exception:
        raise validation_error(campo=clave, categoria=categoria_excepcion.TIPO.value)
