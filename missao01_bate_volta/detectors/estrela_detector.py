import cv2
from detectors.base_detector import ShapeDetector
from config import vision_config as settings
from core.shape_data import ShapeData  
from typing import Optional           

class StarDetector(ShapeDetector):
    def __init__(self):
        super().__init__("estrela")

    def detect(self, contour) -> Optional[ShapeData]:
        """Detecta uma estrela verificando se a contagem de vértices está no intervalo esperado"""
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, settings.APPROX_POLY_FACTOR * peri, True)
        
        num_vertices = len(approx)
        
    
        if 10 <= num_vertices <= 14:
            # SUCESSO! Coleta os dados básicos
            area = cv2.contourArea(contour)
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
            
        # Falha na detecção
        return None