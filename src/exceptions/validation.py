from src.models.categoria_excepcion import categoria_excepcion


class validation_error(Exception):
    """
    Excepción personalizada para manejar errores de validación y especificar detalles.
    """

    def __init__(self, campo: str, categoria: str):
        """Inicializa la excepción con todos los detalles."""

        self.campo = campo
        self.categoria = categoria
        self.mensaje = self.__generar_mensaje()
        super().__init__(self.mensaje)

    def __str__(self):
        """Devuelve el mensaje cuando se aplica str a la excepción."""
        return self.mensaje

    def __generar_mensaje(self):
        """Genera el mensaje de la causa de la excepción."""

        mensaje = f'El campo {self.campo}'
        match self.categoria:
            case categoria_excepcion.TIPO.value:
                mensaje = f'{mensaje} no es del tipo requerido'
            case categoria_excepcion.LONGITUD.value:
                mensaje = f'{mensaje} excede la longitud permitida'
            case _:
                mensaje = f'{mensaje} es inválido'
        return mensaje
