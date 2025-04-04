from src.exceptions.validation import categoria_excepcion, validation_error


def validar_varchar(clave, valor, longitud):
    if valor is None:
        raise validation_error(campo=clave, categoria=categoria_excepcion.faltante.value)
    if not isinstance(valor, str):
        raise validation_error(campo=clave, categoria=categoria_excepcion.tipo.value)
    if len(valor) > longitud:
        raise validation_error(campo=clave, categoria=categoria_excepcion.longitud.value)
    return valor
