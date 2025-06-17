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
    NUMERO = 'NUM'
    OPERADOR = 'OPE'


class operador(CustomEnum):
    SUMA = '+'
    RESTA = '-'
    MULTIPLICACION = '*'
    DIVISION = '/'


class tipo_retorno(CustomEnum):
    NUMERO = 'NUM'
    TEXTO = 'TEX'
    FECHA = 'FEC'


class tipo_objeto(CustomEnum):
    FUNCION = 'FUN'


class tipo_parametro(CustomEnum):
    NUMERO = 'NUM'
    TEXTO = 'TEX'
    VARIABLE = 'VAR'


class paquete_funcion_bd(CustomEnum):
    PROCESOS = "PK_PROCESOS"


class tipo_cliente(CustomEnum):
    CLI1 = "CLI1"
