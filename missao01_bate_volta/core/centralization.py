import cv2 as cv
from ..utils.distance_calculate import distance_calculate




class CentralizationController: 
    def __init__(self, shape_manager, camera_width, camera_height):
        
        self.processor =  shape_manager
        self.camera_center_x = camera_width / 2
        self.camera_center_y = camera_height / 2
    

    def get_center_measure(self, contour):
        # retorna o centro e a largura (w) de um contorno
        
        center_x, center_y = None, None
        _, _, w, _ = cv.boundingRect(contour)

        # targets = [] # Lista para armazenar as coordenadas (x, y)

        # min_area_para_considerar = 10 # Ajuste este valor (em pixels) 

        if len(contour) >= 5:
            (x, y), _ = cv.minEnclosingCircle(contour)
            center_x = int(x)
            center_y = int(y)

        else:
            mu = cv.moments(contour)
            if mu['m00'] > 1e-5:
                center_x = int(mu['m10'] / (mu['m00'] + 1e-5))
                center_y = int(mu['m01'] / (mu['m00'] + 1e-5))

        return (center_x, center_y), w 
    
    def calculate_control_errors(self, frame, target_shape_name, target_real_width_cm):
        
       # Achar os contornos do alvo
        _annotated_frame, found_contours = self.processor.process_frame(
            frame, 
            target_shape_name
        )

        if not found_contours:
            return None, None, None # Alvo não encontrado

        # Escolhe o alvo principal (ex: o maior)
        main_target_contour = max(found_contours, key=cv.contourArea)

        # Pega o centro e a largura em pixels (w) desse alvo
        (center_x, center_y), px_width = self.get_center_measure(main_target_contour)

        if center_x is None:
            return None, None, None 

        # Calcula os erros X e Y
        error_x_px = self.camera_center_x - center_x
        error_y_px = self.camera_center_y - center_y 

        distance_z_m = distance_calculate(
            px_width=px_width, 
            real_width_cm=target_real_width_cm
        )

        return error_x_px, error_y_px, distance_z_m
    