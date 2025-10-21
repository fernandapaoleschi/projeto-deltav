import sys
from core import camera
from core import view_camera 
from config import vision_config as vc

class Aplicacao:
    """
    A classe principal que orquestra a captura e visualização.
    """
    def __init__(self):
       
        try:
            # 1. Cria um objeto da sua classe Camera, usando a config
            self.camera = camera.Camera(vc.CAMERA_INDEX)
            
            # 2. Cria um objeto da sua classe Visualizer
            self.visualizador = view_camera.Visualizer("Captura")

        except IOError as e: # ver se isso tá redundante pq ja tinha uma função de erro na classe camera
            print(f"[ERRO FATAL] Falha ao inicializar a câmera: {e}")
            sys.exit(1)

    def rodar(self):
       
        print("Aplicação iniciada. Pressione 'q' na janela para sair.")
        
        try:
            while self.camera.is_open():
                
                sucesso, frame = self.camera.read_frame()
                if not sucesso:
                    print("Fim do vídeo ou erro na captura.")
                    break
                
                self.visualizador.show_frame(frame)

                # pressionou 'q' para fechar a aplicação
                if self.visualizador.check_exit():
                    break
                    
        finally:
            self.limpar()

    def limpar(self):
        """Libera a câmera e fecha as janelas do OpenCV."""
        print("Encerrando aplicação...")
        self.camera.release_cap()
        self.visualizador.close_windows()

if __name__ == "__main__":

    app = Aplicacao()
    app.rodar()
