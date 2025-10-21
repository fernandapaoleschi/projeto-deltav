from abc import ABC, abstractmethod

class BaseMission(ABC):
    """
    Classe Base Abstrata (Interface) para todas as missões.
    Garante que toda missão tenha um método 'run' para ser executado.
    """
    def __init__(self, shape_manager, camera):
        self.shape_manager = shape_manager
        self.camera = camera
        print(f"Iniciando missão: {self.__class__.__name__}")

    @abstractmethod
    def run(self):
        """
        O ponto de entrada principal para executar a lógica da missão.
        """
        pass