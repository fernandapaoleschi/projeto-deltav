import cv2
from detectors.base_detector import ShapeDetector
from config import settings

class CrossDetector(ShapeDetector):
    def __init__(self, solidity_threshold=0.8):
        super().__init__("cruz")
        self.solidity_threshold = solidity_threshold

    def detect(self, contour):
        #Detecta uma cruz analisando a 'solidez' do contorno
        area = cv2.contourArea(contour)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)

        if hull_area == 0:
            return False
            
        solidity = float(area) / hull_area
        
        # Confirma a complexidade com a contagem de vértices
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, settings.APPROX_POLY_FACTOR * peri, True)
        
        # Uma cruz é côncava (baixa solidez) e tem mais de 6 vértices
        return solidity < self.solidity_threshold and len(approx) > 6