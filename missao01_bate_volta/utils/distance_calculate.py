from config import vision_config as settings

def distance_calculate(px_width, real_width_cm ):
    """Calcula a distância real da câmera até um objeto conhecido em cm"""
    if px_width <= 0: # px_width -> w 
        return -1  # Evita divisão por zero

    distancia_cm = (real_width_cm * settings.FOCAL_LENGTH_PIXELS) / px_width

    distancia_m = distancia_cm / 100

    return distancia_m
 
 