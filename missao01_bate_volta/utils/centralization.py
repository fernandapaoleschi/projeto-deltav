import cv2 as cv
from utils.distance_calculate import distance_calculate


class CentralizationController: 
    def __init__(self, shape_manager, camera_width, camera_height):
        
        self.shape_processor =  shape_manager
        self.camera_center_x = camera_width / 2
        self.camera_center_y = camera_height / 2
    

    def get_center_measure(self, contour):
        """ 
        Retorna o centro e a "medida" (largura/altura máx. em pixels)
        de um contorno usando um retângulo de área mínima (robusto à rotação).
        """
        #    Retorna: ((centro_x, centro_y), (largura_px, altura_px), angulo_rotacao)
        (x, y), (width, height), angle = cv.minAreaRect(contour)

        # 2. Extrai o centro (preciso e robusto à rotação)
        center_x = int(x)
        center_y = int(y)

        # Obter a dimensão principal do objeto para o cálculo da distância
        px_width = max(width, height)

        if px_width == 0:
            return (None, None), 0

        return (center_x, center_y), px_width
    
    def calculate_control_errors(self, frame, target_shape_name, target_real_width_cm): # será chamada pela máquina de estados 
        """Calcula os erros não 3 dimensões"""

        # Achar os contornos do alvo
        _annotated_frame, found_contours = self.shape_processor.process_frame(
            frame, 
            target_shape_name
        )

        if not found_contours:
            return None, None, None # Return None se found_contours estiver vazia -> Alvo não encontrado

        # Escolhe o alvo principal (o maior)
        main_target_contour = max(found_contours, key=cv.contourArea)

        # Pega o centro e a largura em pixels (w) desse alvo
        (center_x, center_y), px_width = self.get_center_measure(main_target_contour)

        if center_x is None:
            return None, None, None # Falha no cálculo do centro 

        # Calcula os erros X e Y
        error_x_px = self.camera_center_x - center_x
        error_y_px = self.camera_center_y - center_y 

        distance_z_m = distance_calculate( px_width = px_width, real_width_cm = target_real_width_cm)

        return error_x_px, error_y_px, distance_z_m
    