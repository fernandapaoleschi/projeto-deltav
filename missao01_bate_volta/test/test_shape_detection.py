import cv2
from config import vision_config as settings

# Importa diretamente todas as classes de detectores que queremos testar
#from detectors.quadrado_detector import SquareDetector
from detectors.triangle_detector import TriangleDetector
from detectors.circle_detector import CircleDetector
from detectors.pentagono_detector import PentagonDetector
from detectors.hexagono_detector import HexagonDetector
from detectors.cruz_detector import CrossDetector
from detectors.estrela_detector import StarDetector
from detectors.casa_detector import HouseDetector

def run_detection_test():
    """
    Uma função simples para testar todos os detectores de forma simultaneamente.
    """
    print("Iniciando modo de teste de detectores...")
    print("Mostre qualquer forma conhecida para a câmera.")
    print("Pressione 'q' para sair.")

    # 1. Cria uma lista com uma instância de cada detector que queremos testar
    detectors = [
        #SquareDetector(),
        TriangleDetector(),
        CircleDetector(),
        PentagonDetector(),
        HexagonDetector(),
        CrossDetector(),
        StarDetector(),
        HouseDetector(),
    ]

    # 2. Inicializa a câmera com as configurações padrão
    cap = cv2.VideoCapture(settings.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.CAMERA_HEIGHT)

    if not cap.isOpened():
        print("Erro: Não foi possível abrir a câmera.")
        return

    # 3. Loop principal de teste
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        
        # Etapas de pré-processamento (exatamente como no ShapeManager)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, settings.CANNY_THRESHOLD_1, settings.CANNY_THRESHOLD_2)
        contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 4. Lógica de teste: para cada contorno, teste cada detector
        if contours:
            for contour in contours:
                if cv2.contourArea(contour) < settings.MIN_CONTOUR_AREA:
                    continue
                
                # Itera sobre nossa lista de objetos detectores
                for detector in detectors:
                    # Se o método .detect() do objeto retornar True...
                    if detector.detect(contour):
                        # ...desenha o nome da forma e o contorno
                        x, y, w, h = cv2.boundingRect(contour)
                        cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
                        cv2.putText(frame, detector.name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        # Para o loop interno, pois já encontramos a forma deste contorno
                        break 

        cv2.imshow("Teste de Detectores", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_detection_test()