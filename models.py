"""Definition of models used in the app"""
import datetime

class Nadador:
    """Represents a swimmer.

    Attributes:
        nombre_apellido (str): The swimmer's full name.
        sexo (str): The swimmer's gender.
        id_categoria (int): The swimmer's category identifier.
        id_club (int): The swimmer's club identifier.
    """
    def __init__(self, nombre_apellido, sexo, id_categoria, id_club):
        self.id_nadador = None
        self.nombre_apellido = nombre_apellido
        self.sexo = sexo
        self.id_categoria = id_categoria
        self.id_club = id_club
        self.categoria = None
        self.club = None

class NadadorPrueba:
    """Represents a swimmer's participation in a specific swimming event.

    Attributes:
        id_nadador (int): The swimmer's identifier.
        id_prueba (int): The identifier of the swimming event.
        fecha (str): The date of the participation.
        tiempo_preinscripcion (str): The pre-registration time for the event.

    """
    def __init__(self, id_prueba: int, tiempo_preinscripcion: str):
        self.id_nadador = None
        self.id_prueba = id_prueba
        self.descripcion = None
        self.fecha = datetime.date.today().strftime("%Y-%m-%d")
        self.tiempo_preinscripcion = tiempo_preinscripcion
        self.tiempo_competencia = None
