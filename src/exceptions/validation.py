from src.enums import categoria_excepcion


class validation_error(Exception):
    def __init__(self, **kwargs):
        if 'campo' in kwargs and 'categoria' in kwargs:
            self.campo, self.categoria = kwargs['campo'], kwargs['categoria']
            match (self.categoria):
                case categoria_excepcion.LONGITUD.value:
                    self.longitud = kwargs['longitud']
                case categoria_excepcion.DIGITOS.value:
                    self.enteros, self.decimales = kwargs['enteros'], kwargs['decimales']
                case categoria_excepcion.VALORES_PERMITIDOS.value:
                    self.valores_permitidos = kwargs['valores_permitidos']
        elif 'faltantes' in kwargs:
            self.faltantes = kwargs['faltantes']
        elif 'no_requeridos' in kwargs:
            self.no_requeridos = kwargs['no_requeridos']
        self.mensaje = self.__generar_mensaje()
        super().__init__(self.mensaje)

    def __str__(self):
        return self.mensaje

    def __generar_mensaje(self):
        mensaje = 'Los atributos provistos son inválidos'
        if hasattr(self, 'campo') and hasattr(self, 'categoria'):
            mensaje = f'El campo {self.campo}'
            match self.categoria:
                case categoria_excepcion.FALTANTE.value:
                    mensaje = f'{mensaje} no fue provisto'
                case categoria_excepcion.VACIO.value:
                    mensaje = f'{mensaje} está vacío'
                case categoria_excepcion.TIPO.value:
                    mensaje = f'{mensaje} no es del tipo requerido'
                case categoria_excepcion.VALOR_POSITIVO.value:
                    mensaje = f'{mensaje} solo admite valores positivos'
                case categoria_excepcion.LONGITUD.value:
                    mensaje = f'{mensaje} permite hasta {self.longitud} caracteres'
                case categoria_excepcion.DIGITOS.value:
                    aviso_decimales = f'y {self.decimales} decimales' if self.decimales else 'sin decimales'
                    mensaje = f'{mensaje} permite hasta {self.enteros} dígitos enteros {aviso_decimales}'
                case categoria_excepcion.VALORES_PERMITIDOS.value:
                    mensaje = f'{mensaje} no coincide con ninguno de los valores permitidos: {', '.join(self.valores_permitidos)}'
                case _:
                    mensaje = f'{mensaje} es inválido'
        elif hasattr(self, 'faltantes'):
            mensaje = f'Faltan los siguientes campos: {', '.join(self.faltantes)}'
        elif hasattr(self, 'no_requeridos'):
            mensaje = f'Los siguientes campos no son requeridos: {', '.join(self.no_requeridos)}'
        return mensaje
