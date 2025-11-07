import math

def calculate_angle(p1, p2, p3):
    
    #Calcula o ângulo (em graus) no vértice p2, formado pelas linhas p1-p2 e p3-p2.
   
    v1 = (p1[0] - p2[0], p1[1] - p2[1])
    v2 = (p3[0] - p2[0], p3[1] - p2[1])
    angle_rad = math.atan2(v2[1], v2[0]) - math.atan2(v1[1], v1[0])
    angle_deg = math.degrees(angle_rad)
    return abs(angle_deg) if abs(angle_deg) <= 180 else 360 - abs(angle_deg)