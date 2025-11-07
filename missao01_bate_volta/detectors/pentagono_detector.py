import cv2
import math
from detectors.base_detector import ShapeDetector
from config import vision_config as settings
from utils.geometry import calculate_angle 
from core.shape_data import ShapeData  
from typing import Optional          

class PentagonDetector(ShapeDetector):
    def __init__(self):
        super().__init__("pentagono")

    def _is_house_signature(self, contour):
        """
        Função auxiliar interna para verificar se o contorno
        tem a assinatura geométrica de uma 'casa'.
        """
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, settings.APPROX_POLY_FACTOR * peri, True)

        # Se não tiver 5 vértices, não pode ser uma casa.
        if len(approx) != 5:
            return False
            
        vertices = approx.squeeze()
        angles = [calculate_angle(vertices[i], vertices[(i + 1) % 5], vertices[(i + 2) % 5]) for i in range(5)]
        
        TOLERANCE_ANGLE = 15
        num_right = sum(1 for ang in angles if (90 - TOLERANCE_ANGLE) <= ang <= (90 + TOLERANCE_ANGLE))
        num_obtuse = sum(1 for ang in angles if ang > (90 + TOLERANCE_ANGLE))
        num_acute = sum(1 for ang in angles if ang < (90 - TOLERANCE_ANGLE))
        
        # Retorna True se a assinatura for de uma casa
        return num_right == 2 and num_obtuse == 2 and num_acute == 1

    def detect(self, contour) -> Optional[ShapeData]: # <--- Atualizar assinatura
        """
        Detecta um pentágono, mas REJEITA se for identificado como uma casa.
        """
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, settings.APPROX_POLY_FACTOR * peri, True)

        # Passo 1: É um pentágono? (Tem 5 lados)
        if len(approx) == 5:
            # Passo 2: Se sim, vamos verificar se é uma casa.
            if self._is_house_signature(contour):
                # É uma casa, ent rejeita
                return None
            else:
                # SUCESSO! É um pentágono de 5 lados que NÃO é uma casa.
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
                
        # Não tem 5 lados, falha na detecção
        return None