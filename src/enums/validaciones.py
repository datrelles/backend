from enum import Enum


class CustomEnum(Enum):
    @classmethod
    def values(cls):
        return {e.value for e in cls}


class categoria_excepcion(CustomEnum):
    faltante = 'faltante'
    vacio = 'vacio'
    tipo = 'tipo'
    longitud = 'longitud'
    valores_permitidos = 'valores_permitidos'
    no_requeridos = 'no_requeridos'


class tipo_estado(CustomEnum):
    activo = 1
    inactivo = 0


class tipo_operador(CustomEnum):
    parametro = 'PAR'
    valor = 'VAL'
    operador = 'OPE'


class operador(CustomEnum):
    suma = '+'
    resta = '-'
    multiplicacion = '*'
    division = '/'


class tipo_retorno(CustomEnum):
    numero = 'NUMBER'
    varchar = 'VARCHAR2'


class tipo_objeto(CustomEnum):
    funcion = 'FUN'


class tipo_parametro(CustomEnum):
    variable = 'VARIABLE'
    caracter = 'CARACTER'
    numero = 'NUMERO'
