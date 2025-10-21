import cv2
import math
from detectors.base_detector import ShapeDetector

class CircleDetector(ShapeDetector):

    def __init__(self, circularity_threshold=0.85):
        """
        Inicializa o detector de círculo.
        :param circularity_threshold: O valor mínimo de "circularidade" para ser considerado um círculo.
                                      1.0 é um círculo perfeito.
        """
        super().__init__("circulo")
        self.circularity_threshold = circularity_threshold

    def detect(self, contour):
        # Calcula a área e o perímetro do contorno.
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)

        # Evita divisão por zero se o perímetro for muito pequeno.
        if perimeter == 0:
            return False

        # Calcula a circularidade usando a fórmula.
        circularity = (4 * math.pi * area) / (perimeter ** 2)

        # Um círculo perfeito é 1.0, então valores próximos a isso são o que queremos.
        if circularity >= self.circularity_threshold:
            return True
        
        return False