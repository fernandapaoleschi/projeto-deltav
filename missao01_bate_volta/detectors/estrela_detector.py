import cv2
from detectors.base_detector import ShapeDetector
from config import settings

class StarDetector(ShapeDetector):
    def __init__(self):
        super().__init__("estrela")

    def detect(self, contour):
        #Detecta uma estrela verificando se a contagem de vértices está no intervalo esperado
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, settings.APPROX_POLY_FACTOR * peri, True)
        
        # Uma estrela de 5 pontas tem 10 vértices.
        return 10 <= len(approx) <= 14