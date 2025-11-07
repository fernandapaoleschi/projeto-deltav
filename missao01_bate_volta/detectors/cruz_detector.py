import cv2
from detectors.base_detector import ShapeDetector
from config import vision_config as settings
from core.shape_data import ShapeData  
from typing import Optional           

class CrossDetector(ShapeDetector):
    def __init__(self, solidity_threshold=0.8):
        super().__init__("cruz")
        self.solidity_threshold = solidity_threshold

    def detect(self, contour) -> Optional[ShapeData]:
        """Detecta uma cruz padrão (12 vértices) analisando a 'solidez'."""
        area = cv2.contourArea(contour)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)

        if hull_area == 0:
            return None # Evita divisão por zero
            
        solidity = float(area) / hull_area
        
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, settings.APPROX_POLY_FACTOR * peri, True)
        
        is_cross = solidity < self.solidity_threshold and len(approx) == 12
        
        if is_cross:
            # SUCESSO! Coleta os dados básicos
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