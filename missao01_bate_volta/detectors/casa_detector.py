import cv2
from detectors.base_detector import ShapeDetector
from utils.geometry import calculate_angle # Importa a função da pasta de utilidades
from config import vision_config as settings # Importa o fator de aproximação configurado

class HouseDetector(ShapeDetector):
    def __init__(self):
        super().__init__("casa")

    def detect(self, contour):
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, settings.APPROX_POLY_FACTOR * peri, True)

        if len(approx) != 5:
            return False

        vertices = approx.squeeze()
        angles = [calculate_angle(vertices[i], vertices[(i + 1) % 5], vertices[(i + 2) % 5]) for i in range(5)]
        
        TOLERANCE_ANGLE = 15
        num_right = sum(1 for ang in angles if (90 - TOLERANCE_ANGLE) <= ang <= (90 + TOLERANCE_ANGLE))
        num_obtuse = sum(1 for ang in angles if ang > (90 + TOLERANCE_ANGLE))
        num_acute = sum(1 for ang in angles if ang < (90 - TOLERANCE_ANGLE))
        
        return num_right == 2 and num_obtuse == 2 and num_acute == 1