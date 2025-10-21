import cv2
from config import vision_config as vc

class Camera:
    '''Encapsula a lógica de captura de vídeo do OpenCV (câmera ou arquivo). '''
    def __init__(self, camera_id):
       
        self.camera_source = camera_id
        self.cap = cv2.VideoCapture(self.camera_source)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, vc.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, vc.CAMERA_HEIGHT)
        
        if not self.cap.isOpened():
            '''Erro se não conseguir abrir a camera'''
            raise IOError(f"Não foi possível abrir a fonte de vídeo: {self.camera_source}")

    def read_frame(self):
        '''Lê o próximo frame da fonte.'''
        sucess, frame = self.cap.read()
        return sucess, frame

    def is_open(self):
        """Verifica se a captura ainda está ativa."""
        return self.cap.isOpened()

    def release_cap(self):
        """Libera os recursos da captura de vídeo."""
        if self.cap.isOpened():
            self.cap.release()
            print("Fonte de vídeo liberada.")

