import numpy as np
from dataclasses import dataclass
from typing import Optional

@dataclass
class ShapeData:
    
    # Parte que o DETECTOR preenche
    name: str 
    contour: np.ndarray 
    area: float 
    center: tuple[int, int]                 # Centro (via cv.moments)
    bounding_box: tuple[int, int, int, int] # Caixa delimitadora (via cv.boundingRect)

    # Parte que o GERENCIADOR de Centralização pode preencher depois
    px_dimension: Optional[float] = None          # Dimensão principal (via cv.minAreaRect)
    robust_center: Optional[tuple[int, int]] = None # Centro robusto (via cv.minAreaRect)
    distance_z_m: Optional[float] = None          # Distância calculada
    error_x_px: Optional[float] = None          # Erro de centralização X
    error_y_px: Optional[float] = None          # Erro de centralização Y