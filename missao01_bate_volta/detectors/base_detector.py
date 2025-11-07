from abc import ABC, abstractmethod
from typing import Optional
from core.shape_data import ShapeData # Importa nossa nova estrutura

class ShapeDetector(ABC):
    
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def detect(self, contour) -> Optional[ShapeData]:
        
        pass