import cv2
from detectors.base_detector import ShapeDetector
from config import settings

class TriangleDetector(ShapeDetector):
    def __init__(self):
        super().__init__("triangulo")

    def detect(self, contour):
        #Detecta um triângulo verificando se o polígono aproximado tem 3 vértices
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, settings.APPROX_POLY_FACTOR * peri, True)
        
        return len(approx) == 3