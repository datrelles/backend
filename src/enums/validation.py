from enum import Enum


class CustomEnum(Enum):
    @classmethod
    def values(cls):
        return {e.value for e in cls}


class categoria_excepcion(CustomEnum):
    FALTANTE = 'faltante'
    VACIO = 'vacio'
    TIPO = 'tipo'
    VALOR_POSITIVO = 'valor_positivo'
    LONGITUD = 'longitud'
    DIGITOS = 'digitos'
    VALORES_PERMITIDOS = 'valores_permitidos'
    NO_REQUERIDOS = 'no_requeridos'


class tipo_estado(CustomEnum):
    ACTIVO = 1
    INACTIVO = 0


class tipo_factor(CustomEnum):
    PARAMETRO = 'PAR'
    VALOR_FIJO = 'VAL'
    OPERADOR = 'OPE'


class operador(CustomEnum):
    SUMA = '+'
    RESTA = '-'
    MULTIPLICACION = '*'
    DIVISION = '/'


class tipo_retorno(CustomEnum):
    NUMERO = 'NUMBER'
    VARCHAR = 'VARCHAR2'


class tipo_objeto(CustomEnum):
    FUNCION = 'FUN'


class tipo_parametro(CustomEnum):
    VARIABLE = 'VARIABLE'
    CARACTER = 'CARACTER'
    NUMERO = 'NUMERO'
