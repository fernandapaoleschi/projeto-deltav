import cv2
import numpy as np
from config import aruco_config as aruco_settings

class MarkerManager:
   
    def __init__(self):
        # Carrega as configurações do arquivo de settings
        self.dictionary = aruco_settings.ARUCO_DICTIONARY
        self.parameters = aruco_settings.ARUCO_PARAMETERS
        self.target_ids = set(aruco_settings.TARGET_IDS) # Usar set para busca rápida

    def _preprocess(self, frame):
        
        # Converter para escala de cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Aplicar um Limiar Adaptativo (Adaptive Thresholding)
        processed_image = cv2.adaptiveThreshold(gray, 255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2 )
        return processed_image

    def detect_markers(self, frame):
    
        # Aplica o pré-processamento
        processed_frame = self._preprocess(frame)
        
        # Detecta os marcadores
        (corners, ids, rejected) = cv2.aruco.detectMarkers(
            processed_frame, 
            self.dictionary, 
            parameters=self.parameters
        )

        # Filtra os marcadores encontrados para incluir apenas os nossos alvos
        filtered_corners = []
        filtered_ids = []
        
        if ids is not None:
            for i, corner_set in zip(ids.flatten(), corners):
                if i in self.target_ids:
                    filtered_ids.append([i]) # Mantém o formato de lista
                    filtered_corners.append(corner_set)

        if not filtered_ids:
            return None, None

        return np.array(filtered_corners), np.array(filtered_ids)

    def draw_markers(self, frame, corners, ids):
        
        if ids is not None and corners is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids, (0, 255, 0))
        
        return frame