from config import vision_config as settings

def convert_pixel_error_to_meters(error_x_px: float, error_y_px: float, distance_z_m: float) -> tuple[float, float]:
    """
    Converte um erro em pixels (dx, dy) para um erro em metros (dX, dY)
    usando a distância até o alvo (Z) e a distância focal da câmera (F).

    :param error_x_px: Erro no eixo X, em pixels.
    :param error_y_px: Erro no eixo Y, em pixels.
    :param distance_z_m: Distância (altura) até o alvo, em metros.
    :return: Uma tupla (error_x_m, error_y_m) com os erros em metros.
    """
    
    # Pega a distância focal do seu arquivo de configuração
    focal_px = settings.FOCAL_LENGTH_PIXELS 
    
    if focal_px == 0 or distance_z_m <= 0:
        # Evita divisão por zero ou resultados inválidos se a
        # distância for 0 ou a câmera não estiver calibrada.
        return 0.0, 0.0

   
    # Erro_Metros = (Erro_Pixels * Distancia_Metros) / Distancia_Focal_Pixels
    error_x_m = (error_x_px * distance_z_m) / focal_px
    error_y_m = (error_y_px * distance_z_m) / focal_px
    
    return error_x_m, error_y_m