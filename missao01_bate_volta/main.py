import sys
from core import camera
from core import view_camera 
from config import vision_config as vc

class Application:
    """
    A classe principal que orquestra a captura e visualização.
    """
    def __init__(self):
       
        try:
            # 1. Cria um objeto da sua classe Camera, usando a config
            self.camera = camera.Camera(vc.CAMERA_INDEX)
            
            # 2. Cria um objeto da sua classe Visualizer
            self.view = view_camera.ViewCamera("Captura")

        except IOError as e: # ver se isso tá redundante pq ja tinha uma função de erro na classe camera
            print(f"[ERRO FATAL] Falha ao inicializar a câmera: {e}")
            sys.exit(1)
    
    def clean(self):
        """Libera a câmera e fecha as janelas do OpenCV."""
        print("Encerrando aplicação...")
        self.camera.release_cap()
        self.view.close_windows()

    def run_window(self):
       
        print("Aplicação iniciada. Pressione 'q' na janela para sair.")
        
        try:
            while self.camera.is_open():
                
                sucess, frame = self.camera.read_frame()
                if not sucess:
                    print("Fim do vídeo ou erro na captura.")
                    break
                
                self.view.show_frame(frame)

                # pressionou 'q' para fechar a aplicação
                if self.view.check_exit():
                    break
                    
        finally:
            self.clean()

   

if __name__ == "__main__":

    app = Application()
    app.run_window()
