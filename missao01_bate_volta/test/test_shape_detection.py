# ----------------------------------------------------
# 🧠 Missão Delta V — Teste de Detecção de Formas
# ----------------------------------------------------
# Usa a webcam para testar todos os detectores do sistema.
# ----------------------------------------------------

import cv2
import numpy as np

# Importa o pré-processamento
from utils.preprocessing import preprocess_frame

# Importa todos os detectores
from detectors.triangle_detector import TriangleDetector
from detectors.quadrado_detector import SquareDetector
from detectors.pentagono_detector import PentagonDetector
from detectors.hexagono_detector import HexagonDetector
from detectors.estrela_detector import StarDetector
from detectors.cruz_detector import CrossDetector
from detectors.circle_detector import CircleDetector
from detectors.casa_detector import HouseDetector

# ----------------------------------------------------
# ⚙️ CONFIGURAÇÕES GERAIS
# ----------------------------------------------------
WINDOW_NAME = "Missão Delta V — Teste Webcam"
FONT = cv2.FONT_HERSHEY_SIMPLEX
MIN_AREA = 800  # área mínima para evitar ruídos

# Lista de detectores ativos
DETECTORS = [
    TriangleDetector(),
    SquareDetector(),
    PentagonDetector(),
    HexagonDetector(),
    StarDetector(),
    CrossDetector(),
    CircleDetector(),
    HouseDetector(),
]

# ----------------------------------------------------
# 🔍 Função principal de processamento
# ----------------------------------------------------
def process_frame(frame):
    # Pré-processa o frame para destacar as formas
    morph = preprocess_frame(frame)

    # Encontra contornos
    contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Percorre os contornos encontrados
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < MIN_AREA:
            continue

        detected_shape = None

        # Testa cada detector
        for detector in DETECTORS:
            if detector.detect(contour):
                detected_shape = detector.name
                break  # para no primeiro que detectar algo

        if detected_shape:
            # Calcula o centro do contorno
            M = cv2.moments(contour)
            cx = int(M["m10"] / M["m00"]) if M["m00"] != 0 else 0
            cy = int(M["m01"] / M["m00"]) if M["m00"] != 0 else 0

            # Desenha o contorno e o nome da forma
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
            cv2.putText(frame, detected_shape, (cx - 60, cy - 10), FONT, 0.7, (0, 255, 255), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

    return frame, morph


# ----------------------------------------------------
# 🚀 LOOP PRINCIPAL — CAPTURA DA WEBCAM
# ----------------------------------------------------
def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # webcam padrão (índice 0)

    if not cap.isOpened():
        print("❌ Erro: não foi possível acessar a webcam.")
        return

    print("✅ Webcam iniciada — pressione 'q' para encerrar.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("❌ Erro ao capturar imagem.")
            break

        # Processa o frame
        processed_frame, morph = process_frame(frame)

        # Exibe os resultados
        cv2.imshow(WINDOW_NAME, processed_frame)
        cv2.imshow("Pré-processamento", morph)

        # Sai ao pressionar 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("🛑 Sistema encerrado manualmente.")
            break

    cap.release()
    cv2.destroyAllWindows()


# ----------------------------------------------------
# 🧩 PONTO DE ENTRADA
# ----------------------------------------------------
if __name__ == "__main__":
    main()
