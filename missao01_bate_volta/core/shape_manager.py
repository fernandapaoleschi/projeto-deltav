import cv2
from config import vision_config as settings
from utils.preprocessing import preprocess_frame  # importa o preprocessing

# Importando as classes dos detectores
from detectors.base_detector import ShapeDetector
from detectors.triangle_detector import TriangleDetector
from detectors.circle_detector import CircleDetector
from detectors.pentagono_detector import PentagonDetector
from detectors.hexagono_detector import HexagonDetector
from detectors.cruz_detector import CrossDetector
from detectors.estrela_detector import StarDetector
from detectors.casa_detector import HouseDetector

class ShapeManager:
    def __init__(self):
        """
        Inicializa o ShapeManager registrando todos os detectores de formas.
        A CHAVE (ex: "estrela") deve ser a mesma string usada no TARGET_SHAPE da missão.
        """
        self.detectors = {
            # Certifique-se que o nome da chave "estrela" é EXATAMENTE
            # o mesmo que o TARGET_SHAPE no seu script de missão.
            "estrela": StarDetector(),
            "cruz": CrossDetector(),
            "casa": HouseDetector(),
            "hexagono": HexagonDetector(),
            "triangulo": TriangleDetector(),
            "pentagono": PentagonDetector(),
            # "circulo": CircleDetector(), # Adicione outros se precisar
        }
        print("[ShapeManager] Detectores registrados:", list(self.detectors.keys()))

    def _find_contours(self, frame):
        """Função auxiliar para encontrar todos os contornos na imagem."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Tenta usar os thresholds do seu config
        canny = cv2.Canny(blur, settings.CANNY_THRESHOLD_1, settings.CANNY_THRESHOLD_2)
        
        contours, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def process_frame(self, frame, target_shape_name: str):
        """
        Processa o frame, encontra todos os contornos e usa o detector
        específico (baseado em target_shape_name) para retornar uma lista de 
        OBJETOS ShapeData.
        """
        
        # 1. Obtém o detector correto baseado no nome
        detector = self.detectors.get(target_shape_name)
        
        if not detector:
            # Isso pode acontecer se o TARGET_SHAPE for "quadrado" mas
            # você só registrou "estrela"
            print(f"[ShapeManager] Aviso: Nenhum detector registado para o nome '{target_shape_name}'")
            return [], frame # Retorna lista vazia

        # 2. Encontra todos os contornos na imagem
        all_contours = self._find_contours(frame)
        
        found_shapes = [] # Esta será a lista de OBJETOS ShapeData

        # 3. Itera sobre todos os contornos encontrados
        for contour in all_contours:
            # Filtra contornos muito pequenos
            area_inicial = cv2.contourArea(contour)
            if area_inicial < settings.MIN_CONTOUR_AREA:
                continue
                
            # 4. Tenta detetar a forma usando o detector específico
            #    Ex: chama StarDetector.detect(contour)
            shape_data = detector.detect(contour) 
            
            # 5. Se o detector retornar um objeto (sucesso!), adiciona à lista
            if shape_data is not None:
                found_shapes.append(shape_data)

        # 6. Retorna a lista de objetos ShapeData encontrados
        #    ESTA LISTA AGORA TEM OBJETOS COM O ATRIBUTO .area
        
        # (Opcional) Desenha os contornos encontrados
        annotated_frame = frame.copy()
        for shape in found_shapes:
            cv2.drawContours(annotated_frame, [shape.contour], -1, (0, 255, 0), 2)
            cv2.putText(annotated_frame, shape.name, shape.center, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Retorna a lista de OBJETOS e o frame anotado
        return annotated_frame, found_shapes

    @staticmethod
    def _draw_detection(frame, contour, name):
        """Desenha o contorno e o nome da forma no frame."""
        x, y, w, h = cv2.boundingRect(contour)
        cv2.drawContours(frame, [contour], -1, settings.CONTOUR_COLOR, settings.CONTOUR_THICKNESS)
        cv2.putText(
            frame, name.capitalize(),
            (x, y - 10),
            settings.FONT, settings.FONT_SCALE,
            settings.CONTOUR_COLOR, settings.FONT_THICKNESS
        )
