
import cv2
import numpy as np
from detectors.base_detector import ShapeDetector
from config import vision_config as settings
from core.shape_data import ShapeData  
from typing import Optional           


EPS = 1e-9 # Epsilon para evitar divisão por zero

def approx_vertices(contour: np.ndarray, epsilon_ratio: float = 0.02):
    """
    Retorna o contorno aproximado e o número de vértices.
    """
    #
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon_ratio * peri, True)
    return approx, len(approx)

def circularity(contour: np.ndarray) -> float:
    """
    Mede o quão circular é o contorno.
    - 1.0 = círculo perfeito
    """
    #
    area = cv2.contourArea(contour)
    peri = cv2.arcLength(contour, True)
    if peri < EPS:
        return 0.0
    # Fórmula da circularidade
    return 4 * np.pi * area / (peri * peri)

# ==========================================================
# === CLASSE PRINCIPAL DO DETECTOR ===
# ==========================================================

class StarDetector(ShapeDetector):
    def __init__(self):
        #
        super().__init__("estrela")

    def detect(self, contour) -> Optional[ShapeData]:
        """
        Detecta uma estrela (versão robusta e independente)
        usando ângulos agudos, circularidade e número de vértices.
        """

        # --- 1. Coletar Características Geométricas ---
        
        area = cv2.contourArea(contour)
        # Filtro de área mínima (ajuste o valor conforme necessário)
        if area < 100:
            return None

        # Usa a função 'approx_vertices' que COPIAMOS acima
        #
        approx, lados = approx_vertices(contour, epsilon_ratio=settings.APPROX_POLY_FACTOR)
        
        # Usa a função 'circularity' que COPIAMOS acima
        circ = circularity(contour)
        
        # Pega a "taxa de preenchimento" (fill_ratio)
        x, y, w, h = cv2.boundingRect(contour)
        fill_ratio = area / (w * h + EPS) # Usa o EPS local

        
        # --- 2. Aplicar as Regras de Classificação (Lógica do shape_classifier.py) ---
        #
        
        # Regra 1: Checa características gerais (lados, circularidade, preenchimento)
        if circ < 0.75 and fill_ratio < 0.50 and lados >= 8:
            
            # Regra 2: (A mais importante) Verifica os ângulos das pontas
            angles = self._calculate_angles(approx)
            acute_ratio = self._get_acute_angle_ratio(angles)
            
            # Se pelo menos 25% dos ângulos forem agudos (< 70 graus)...
            #
            if acute_ratio >= 0.25:
                # SUCESSO! É uma estrela.
                
                # --- 3. Coletar Dados para ShapeData (Lógica do seu original) ---
                #
                M = cv2.moments(contour)
                if M["m00"] == 0: 
                    return None # Evita divisão por zero
                
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                
                # Retorna o objeto ShapeData preenchido
                #
                return ShapeData(
                    name=self.name,
                    contour=contour,
                    center=center,
                    bounding_box=(x, y, w, h), # Já calculámos o BBox
                    area=area                  # Já calculámos a área
                )
            
        # Falha na detecção (não passou nas regras)
        return None

    # --- Métodos Auxiliares (Copiados do shape_classifier.py) ---

    def _calculate_angles(self, approx):
        """Calcula ângulos entre os vértices aproximados."""
        #
        pts = [p[0] for p in approx]
        angles = []
        for i in range(len(pts)):
            p1 = pts[i - 2]
            p2 = pts[i - 1]
            p3 = pts[i]
            v1 = np.array(p1) - np.array(p2)
            v2 = np.array(p3) - np.array(p2)
            # Adiciona EPS local para segurança
            cosang = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + EPS) 
            ang = np.degrees(np.arccos(np.clip(cosang, -1.0, 1.0)))
            angles.append(ang)
        return angles

    def _get_acute_angle_ratio(self, angles):
        """Proporção de ângulos agudos (< 70°)."""
        #
        return sum(1 for a in angles if a < 70) / max(1, len(angles))