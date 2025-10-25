import cv2
from detectors.base_detector import ShapeDetector
from config import vision_config as settings

class CrossDetector(ShapeDetector):
    def __init__(self, solidity_threshold=0.8):
        super().__init__("cruz")
        self.solidity_threshold = solidity_threshold

    def detect(self, contour):
        """Detecta uma cruz padrão (12 vértices) analisando a 'solidez'."""
        area = cv2.contourArea(contour)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)

        if hull_area == 0:
            return False
            
        solidity = float(area) / hull_area
        
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, settings.APPROX_POLY_FACTOR * peri, True)
        
        # A cruz padrão (como a da imagem) terá 12 vértices e é côncava.
        return solidity < self.solidity_threshold and len(approx) == 12