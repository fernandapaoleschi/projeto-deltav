import cv2
from detectors.base_detector import ShapeDetector
from config import vision_config as settings

class SquareDetector(ShapeDetector):
    def __init__(self):
        super().__init__("quadrado")

    def detect(self, contour):
        #Detecta um quadrado verificando se o polígono aproximado tem 4 vértices e se sua proporção (largura/altura) é próxima de 1
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, settings.APPROX_POLY_FACTOR * peri, True)
        
        if len(approx) == 4:
            # Calcula a caixa delimitadora para verificar a proporção
            (x, y, w, h) = cv2.boundingRect(approx)
            
            # Evita divisão por zero
            if h == 0: 
                return False
            
            aspect_ratio = w / float(h)
            
            # Um quadrado verdadeiro tem uma proporção próxima a 1
            return 0.90 <= aspect_ratio <= 1.10
            
        return False