import cv2 as cv
from utils.distance_calculate import distance_calculate
from utils.conversions import convert_pixel_error_to_meters
from core.shape_data import ShapeData 
from typing import Optional          

class CentralizationController: 
    """
         Processa um frame para localizar a forma-alvo principal.
        
        Se a forma (`target_shape_name`) for encontrada, calcula:
        1. Erros de centralização (X, Y) em pixels e metros.
        2. Distância Z (em metros) até o alvo.

        Args:
            frame (np.ndarray): O frame da imagem a ser analisado.
            target_shape_name (str): O nome da forma a ser procurada.
            target_real_width_cm (float): A largura física real do alvo em cm.

        Returns:
            Optional[ShapeData]: Um objeto `ShapeData` com todos os dados
            de controle (erros, distância) ou `None` se o alvo não
            for encontrado.
     """
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
        
        print(robust_center_x)
        print(robust_center_y)
        print(px_width)        
        
        
        if robust_center_x is None:
            return None # Falha no cálculo do centro 

        # Calcula os erros X e Y em PIXELS
        error_x_px = self.camera_center_x - robust_center_x
        error_y_px = self.camera_center_y - robust_center_y 
        
        # Calcula a distância Z (usando distance_calculate)
        distance_z_m = distance_calculate(
            px_width=px_width, 
            real_width_cm=target_real_width_cm
        )

        # --- 3. CHAME A NOVA FUNÇÃO PARA CONVERTER ---
        error_x_m, error_y_m = convert_pixel_error_to_meters(
            error_x_px, 
            error_y_px, 
            distance_z_m)

        main_target_shape.px_dimension = px_width
        main_target_shape.robust_center = (robust_center_x, robust_center_y)
        main_target_shape.distance_z_m = distance_z_m
        
        # Salva os erros em PIXELS
        main_target_shape.error_x_px = error_x_px 
        main_target_shape.error_y_px = error_y_px
        
        # erros em metros
        main_target_shape.error_x_m = error_x_m 
        main_target_shape.error_y_m = error_y_m

       # Retorna o objeto ShapeData ---
        return main_target_shape