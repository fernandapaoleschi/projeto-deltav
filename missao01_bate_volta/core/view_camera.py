# visualizador.py
import cv2 as cv

class Visualizer:
    ''' Gerencia a exibição de janelas e a verificação de entrada do usuário. '''
    
    def __init__(self, window_name="Missão 01"):
        self.window_name = window_name
        cv.namedWindow(self.window_name, cv.WINDOW_AUTOSIZE)

    def show_frame(self, frame, window_title=None):
        ''' Exibe um frame em uma janela.'''

        name = window_title if window_title else self.window_name
        cv.imshow(name, frame)

    def check_exit(self, delay_ms=1):
        ''' Verifica se a tecla 'q' foi pressionada para sair.'''
        
        # 0xFF == ord('q') é a máscara para garantir compatibilidade 64-bit
        if cv.waitKey(delay_ms) & 0xFF == ord('q'):
            return True
        return False

    def close_windows(self):
        '''Fecha todas as janelas abertas pelo OpenCV.'''
        print("Closing OpenCV windows.")
        cv.destroyAllWindows()