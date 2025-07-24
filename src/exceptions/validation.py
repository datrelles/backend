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
            mensaje = 'El campo {}'.format(self.campo)
            match self.categoria:
                case categoria_excepcion.FALTANTE.value:
                    mensaje = '{} no fue provisto'.format(mensaje)
                case categoria_excepcion.VACIO.value:
                    mensaje = '{} está vacío'.format(mensaje)
                case categoria_excepcion.TIPO.value:
                    mensaje = '{} no es del tipo requerido'.format(mensaje)
                case categoria_excepcion.VALOR_POSITIVO.value:
                    mensaje = '{} solo admite valores positivos'.format(mensaje)
                case categoria_excepcion.LONGITUD.value:
                    mensaje = '{} permite hasta {} caracteres'.format(mensaje, self.longitud)
                case categoria_excepcion.DIGITOS.value:
                    aviso_decimales = 'y {} decimales'.format(self.decimales) if self.decimales else 'sin decimales'
                    mensaje = '{} permite hasta {} dígitos enteros {}'.format(mensaje, self.enteros, aviso_decimales)
                case categoria_excepcion.VALORES_PERMITIDOS.value:
                    mensaje = '{} no coincide con ninguno de los valores permitidos: {}'.format(mensaje, ', '.join(
                        [str(v) for v in self.valores_permitidos]))
                case _:
                    mensaje = '{} es inválido'.format(mensaje)
        elif hasattr(self, 'faltantes'):
            mensaje = 'Faltan los siguientes campos: {}'.format(', '.join(self.faltantes))
        elif hasattr(self, 'no_requeridos'):
            mensaje = 'Los siguientes campos no son requeridos: {}'.format(', '.join(self.no_requeridos))
        return mensaje
