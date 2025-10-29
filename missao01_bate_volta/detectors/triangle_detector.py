import cv2
from detectors.base_detector import ShapeDetector
from config import vision_config as settings
from core.shape_data import ShapeData
from typing import Optional

class TriangleDetector(ShapeDetector):
    def __init__(self):
        super().__init__("triangulo")

    def detect(self, contour) -> Optional[ShapeData]: # <--- Atualizar assinatura
        """Detecta um triângulo verificando se o polígono aproximado tem 3 vértices"""
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, settings.APPROX_POLY_FACTOR * peri, True)
        
        if len(approx) == 3:
            # SUCESSO então coleta os dados básicos
            area = cv2.contourArea(contour)
            M = cv2.moments(contour)
            
            if M["m00"] == 0: 
                return None # Evita divisão por zero
            
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            bounding_box = cv2.boundingRect(contour) # (x, y, w, h)
            
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