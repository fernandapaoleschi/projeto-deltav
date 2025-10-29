import cv2 as cv
from utils.distance_calculate import distance_calculate
from core.shape_data import ShapeData 
from typing import Optional          

class CentralizationController: 
    
    def __init__(self, shape_manager, camera_width, camera_height):
        self.shape_processor = shape_manager 
        self.camera_center_x = camera_width / 2
        self.camera_center_y = camera_height / 2
    
    def get_center_measure(self, contour):
        (x, y), (width, height), angle = cv.minAreaRect(contour)
        center_x = int(x)
        center_y = int(y)
        px_width = max(width, height)
        if px_width == 0:
            return (None, None), 0
        return (center_x, center_y), px_width
    
    def calculate_control_data(self, frame, target_shape_name, target_real_width_cm) -> Optional[ShapeData]: 
       

        # Processa o frame para detectar formas
        _annotated_frame, found_shapes = self.shape_processor.process_frame(
            frame, 
            target_shape_name
        )

        if not found_shapes:
            return None # Alvo não encontrado

        # Escolhe o alvo principal (o maior)
        main_target_shape: ShapeData = max(found_shapes, key=lambda s: s.area)

        # Pega o centro e a largura em pixels (w) desse alvo
        (robust_center_x, robust_center_y), px_width = self.get_center_measure(main_target_shape.contour)

        if robust_center_x is None:
            return None # Falha no cálculo do centro 

        # Calcula os erros X e Y
        error_x_px = self.camera_center_x - robust_center_x
        error_y_px = self.camera_center_y - robust_center_y 

        # Calcula a distância Z (usando distance_calculate)
        distance_z_m = distance_calculate(
            px_width=px_width, 
            real_width_cm=target_real_width_cm
        )

        #ENRIQUECE O OBJETO SHAPEDATA
        main_target_shape.px_dimension = px_width
        main_target_shape.robust_center = (robust_center_x, robust_center_y)
        main_target_shape.distance_z_m = distance_z_m
        main_target_shape.error_x_px = error_x_px
        main_target_shape.error_y_px = error_y_px

        #Retorna o objeto completo
        return main_target_shape