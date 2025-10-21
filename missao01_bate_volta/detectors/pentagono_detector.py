import cv2
from detectors.base_detector import ShapeDetector
from config import settings

class PentagonDetector(ShapeDetector):
    def __init__(self):
        super().__init__("pentagono")

    def detect(self, contour):
        # Detecta um pentágono verificando se o polígono aproximado tem 5 vértices
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, settings.APPROX_POLY_FACTOR * peri, True)
        
        return len(approx) == 5