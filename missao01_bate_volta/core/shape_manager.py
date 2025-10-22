import cv2
from config import settings
from utils.preprocessing import preprocess_frame  # importa o preprocessing

# Importando as classes dos detectores
from detectors.base_detector import ShapeDetector
from detectors.quadrado_detector import SquareDetector
from detectors.triangle_detector import TriangleDetector
from detectors.circle_detector import CircleDetector
from detectors.pentagono_detector import PentagonDetector
from detectors.hexagono_detector import HexagonDetector
from detectors.cruz_detector import CrossDetector
from detectors.estrela_detector import StarDetector
from detectors.casa_detector import HouseDetector

class ShapeManager:
    def __init__(self):
        # Carrega os parâmetros do arquivo de configuração
        self.min_area = settings.MIN_CONTOUR_AREA
        self.canny_t1 = settings.CANNY_THRESHOLD_1
        self.canny_t2 = settings.CANNY_THRESHOLD_2

        # Carrega e instancia todos os detectores disponíveis
        detectors_list = [
            SquareDetector(),
            TriangleDetector(),
            CircleDetector(),
            PentagonDetector(),
            HexagonDetector(),
            CrossDetector(),
            StarDetector(),
            HouseDetector(),
        ]
        self._detectors = {d.name: d for d in detectors_list}

    def get_available_shapes(self):
        return list(self._detectors.keys())

    def process_frame(self, frame, target_shape_name):
        """
        Aplica o pipeline de pré-processamento e tenta detectar
        a forma solicitada.
        """
        # usa o módulo de pré-processamento
        morph = preprocess_frame(
            frame,
            blur_size=(5, 5),
            canny_t1=self.canny_t1,
            canny_t2=self.canny_t2
        )

        contours, _ = cv2.findContours(morph.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detector_obj = self._detectors.get(target_shape_name)
        if not detector_obj:
            return frame, []

        found_contours = []

        for contour in contours:
            if cv2.contourArea(contour) < self.min_area:
                continue

            if detector_obj.detect(contour):
                found_contours.append(contour)
                self._draw_detection(frame, contour, target_shape_name)

        return frame, found_contours

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
