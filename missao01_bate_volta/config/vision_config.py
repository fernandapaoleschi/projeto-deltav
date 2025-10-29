import cv2 as cv 
import math
# CONFIGURAÇÕES GERAIS DA APLICAÇÃO

# -- CONFIGURAÇÕES DA CÂMERA --
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# PARÂMETROS DE TAMANHO/DISTÂNCIA
FOCAL_LENGTH_PIXELS = 750

# Objeto da Missão "Bate e Volta"
PLATFORM_WIDTH_CM = 80.0  #  (Quadrados brancos com 80x80cm)

# Objeto da Missão "Coleta e Entrega Guiada"
ARUCO_BOX_WIDTH_CM = 30.0  #  (Caixas com 30x30cm)

# Objeto de Entrega da Missão "Bate e Volta"
WIDTH_CUBE_CM = 5.0  #  (Cubo vermelho com 5x5x5cm)


# -- PARÂMETROS DE DETECÇÃO --
MIN_CONTOUR_AREA = 400
CANNY_THRESHOLD_1 = 50
CANNY_THRESHOLD_2 = 150
APPROX_POLY_FACTOR = 0.02 # Fator para o cv2.approxPolyDP

# -- PARÂMETROS DE DESENHO --
FONT = cv.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.7
FONT_THICKNESS = 2
CONTOUR_COLOR = (0, 255, 0)
CONTOUR_THICKNESS = 3
