from src.models.categoria_excepcion import categoria_excepcion


class validation_error(Exception):
    def __init__(self, campo: str, categoria: str):
        self.campo = campo
        self.categoria = categoria
        self.mensaje = self.__generar_mensaje()
        super().__init__(self.mensaje)

    def __str__(self):
        return self.mensaje

    def __generar_mensaje(self):
        mensaje = f'El campo {self.campo}'
        match self.categoria:
            case categoria_excepcion.tipo.value:
                mensaje = f'{mensaje} no es del tipo requerido'
            case categoria_excepcion.longitud.value:
                mensaje = f'{mensaje} excede la longitud permitida'
            case _:
                mensaje = f'{mensaje} es inválido'
        return mensaje
