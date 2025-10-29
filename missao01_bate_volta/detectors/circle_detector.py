import cv2
import math
from detectors.base_detector import ShapeDetector
from core.shape_data import ShapeData  
from typing import Optional          

class CircleDetector(ShapeDetector):

    def __init__(self, circularity_threshold=0.85):
        """
        Inicializa o detector de círculo.
        :param circularity_threshold: O valor mínimo de "circularidade" para ser considerado um círculo.
                                      1.0 é um círculo perfeito.
        """
        super().__init__("circulo")
        self.circularity_threshold = circularity_threshold

    def detect(self, contour) -> Optional[ShapeData]:
        # Calcula a área e o perímetro do contorno.
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)

        # Evita divisão por zero se o perímetro for muito pequeno.
        if perimeter == 0:
            return None

        # Calcula a circularidade usando a fórmula.
        circularity = (4 * math.pi * area) / (perimeter ** 2)

        # Um círculo perfeito é 1.0, então valores próximos a isso são o que queremos.
        if circularity >= self.circularity_threshold:
            # SUCESSO! Coleta os dados básicos
            M = cv2.moments(contour)
            
            if M["m00"] == 0: 
                return None # Evita divisão por zero
            
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            bounding_box = cv2.boundingRect(contour)
            
            # Retorna o objeto ShapeData preenchido
            return ShapeData(
                name=self.name,
                contour=contour,
                center=center,
                bounding_box=bounding_box,
                area=area
            )
        
        
        return None