import cv2.aruco as aruco

# --- CONFIGURAÇÃO DO DICIONÁRIO ARUCO ---
ARUCO_DICTIONARY = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)

# --- CONFIGURAÇÃO DOS PARÂMETROS DE DETECÇÃO ---
ARUCO_PARAMETERS = aruco.DetectorParameters_create()

# --- MARCADORES-ALVO DA MISSÃO ---
TARGET_IDS = [2, 3, 4, 5]