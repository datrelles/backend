from src.exceptions.validation import categoria_excepcion, validation_error


def validar_varchar(clave, valor, longitud, es_requerido=True):
    if es_requerido:
        if valor is None:
            raise validation_error(campo=clave, categoria=categoria_excepcion.faltante.value)
        if valor is '':
            raise validation_error(campo=clave, categoria=categoria_excepcion.vacio.value)
    else:
        if valor is '' or valor is None:
            return None
    if not isinstance(valor, str):
        raise validation_error(campo=clave, categoria=categoria_excepcion.tipo.value)
    if len(valor) > longitud:
        raise validation_error(campo=clave, categoria=categoria_excepcion.longitud.value, longitud=longitud)
    return valor
