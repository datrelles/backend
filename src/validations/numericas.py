from src.exceptions.validation import categoria_excepcion, validation_error


def validar_longitud(numero: int | float, digitos_enteros: int, digitos_decimales=0, es_exacta=False):
    """
    Valida la cantidad de dígitos de un número, enteros y opcionalmente los decimales.

        Args:
            numero (int | float): Número a validar.
            digitos_enteros (int): Cantidad de digitos enteros a validar.
            digitos_decimales (int): Cantidad de digitos decimales a validar.
            es_exacta (bool): Bandera para determinar si la validación es exacta o verifica límites máximos.
        Returns:
            bool: Resultado de la validación.
    """
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


def validar_number(clave, valor, digitos_enteros, digitos_decimales=0):
    try:
        valor = float(valor) if digitos_decimales else int(valor)
    except Exception as e:
        raise validation_error(clave, categoria_excepcion.TIPO.value)
    if not validar_longitud(valor, digitos_enteros, digitos_decimales):
        raise validation_error(clave, categoria_excepcion.LONGITUD.value)
    return valor
