from src.enums.validaciones import categoria_excepcion, validation_error


def validar_longitud(numero: int | float, digitos_enteros: int, digitos_decimales=0, es_exacta=False):
    try:
        str_numero = str(abs(numero))
        if '.' in str_numero:
            parte_entera, parte_decimal = str_numero.split('.')
        else:
            parte_entera, parte_decimal = str_numero, ""
        if es_exacta:
            if len(parte_entera) != digitos_enteros:
                return False
            if digitos_decimales and len(parte_decimal) != digitos_decimales:
                return False
        else:
            if len(parte_entera) > digitos_enteros:
                return False
            if digitos_decimales and len(parte_decimal) > digitos_decimales:
                return False
        return True
    except Exception as e:
        return False


def validar_number(clave, valor, digitos_enteros, digitos_decimales=0, es_requerido=True, valores_permitidos=None):
    if es_requerido:
        if valor is None:
            raise validation_error(campo=clave, categoria=categoria_excepcion.faltante.value)
        if valor == '':
            raise validation_error(campo=clave, categoria=categoria_excepcion.vacio.value)
    else:
        if not valor:
            return None
    try:
        valor = float(valor) if digitos_decimales else int(valor)
    except Exception as e:
        raise validation_error(campo=clave, categoria=categoria_excepcion.tipo.value)
    if not validar_longitud(valor, digitos_enteros, digitos_decimales):
        raise validation_error(campo=clave, categoria=categoria_excepcion.longitud.value,
                               longitud=digitos_enteros + digitos_decimales)
    if valores_permitidos and not valor in valores_permitidos:
        raise validation_error(campo=clave, categoria=categoria_excepcion.valores_permitidos.value,
                               valores_permitidos=valores_permitidos)
    return valor
