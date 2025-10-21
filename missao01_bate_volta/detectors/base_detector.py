from abc import ABC, abstractmethod

class ShapeDetector(ABC):
    """
    Classe Base Abstrata (Interface) para todos os detectores de forma.
    Garante que todas as subclasses tenham um nome e um método detect.
    """
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def detect(self, contour):
        """
        Método que deve ser implementado por cada detector específico.
        Recebe um contorno e retorna True se a forma for detectada, False caso contrário.
        """
        pass