import cv2
import numpy as np


#  FUNÇÃO PRINCIPAL: PRÉ-PROCESSAMENTO DO FRAME

def preprocess_frame(frame, blur_size=(5, 5), canny_t1=50, canny_t2=150, morph_kernel=(5, 5)):
    """
    Aplica o pipeline de pré-processamento para detecção de formas.

    Etapas:
      Converte a imagem para tons de cinza
      Aplica suavização (Gaussian Blur)
      Detecta bordas com o algoritmo de Canny
      Aplica fechamento morfológico para remover ruídos pequenos

    Retorna:
        morph (np.ndarray): imagem binária processada (usada para encontrar contornos)
    """

    # Converte para escala de cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # uavização (reduz ruído e falsos contornos)
    blurred = cv2.GaussianBlur(gray, blur_size, 0)

    #  Detector de bordas Canny
    edges = cv2.Canny(blurred, canny_t1, canny_t2)

    # Fechamento morfológico (junta bordas quebradas) 
    kernel = np.ones(morph_kernel, np.uint8)
    morph = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    return morph


# 🧩 OPÇÃO 2: PRÉ-PROCESSAMENTO COM LIMIAR ADAPTATIVO

def adaptive_threshold_preprocess(frame, block_size=21, C=5):
    """
    Alternativa ao Canny — útil em ambientes com iluminação irregular.

    Parâmetros:
        block_size: tamanho do bloco usado para calcular o limiar local
        C: constante subtraída do limiar médio (ajusta sensibilidade)

    Retorna:
        morph (np.ndarray): imagem binária pós-fechamento morfológico
    """

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    binary = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        block_size, C
    )

    kernel = np.ones((5, 5), np.uint8)
    morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    return morph
