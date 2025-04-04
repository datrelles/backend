from src.models.categoria_excepcion import categoria_excepcion


class validation_error(Exception):
    def __init__(self, **kwargs):
        if 'campo' in kwargs and 'categoria' in kwargs:
            self.campo, self.categoria = kwargs['campo'], kwargs['categoria']
            if self.categoria == categoria_excepcion.longitud.value:
                self.longitud = kwargs['longitud']
        elif 'campos' in kwargs:
            self.campos = kwargs['campos']
        self.mensaje = self.__generar_mensaje()
        super().__init__(self.mensaje)

    def __str__(self):
        return self.mensaje

    def __generar_mensaje(self):
        mensaje = 'Los atributos provistos son inválidos'
        if hasattr(self, 'campo') and hasattr(self, 'categoria'):
            mensaje = f'El campo {self.campo}'
            match self.categoria:
                case categoria_excepcion.faltante.value:
                    mensaje = f'{mensaje} no fue provisto'
                case categoria_excepcion.tipo.value:
                    mensaje = f'{mensaje} no es del tipo requerido'
                case categoria_excepcion.longitud.value:
                    mensaje = f'{mensaje} debe contener máximo {self.longitud} caracteres'
                case _:
                    mensaje = f'{mensaje} es inválido'
        elif hasattr(self, 'campos'):
            mensaje = f'Los siguientes campos no fueron provistos: {', '.join(self.campos)}'
        return mensaje
