import cv2
from detectors.base_detector import ShapeDetector
from config import vision_config as settings

class HexagonDetector(ShapeDetector):
    def __init__(self):
        super().__init__("hexagono")

    def detect(self, contour):
        #Detecta um hexágono verificando se o polígono aproximado tem 6 vértices
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, settings.APPROX_POLY_FACTOR * peri, True)
        
        return len(approx) == 6