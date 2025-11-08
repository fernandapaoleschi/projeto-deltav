# --- Em um novo arquivo: vision_manager.py ---

import cv2 
import time
from threading import Event 
# --- Imports da Missão ---
from utils.centralization import CentralizationController
from core.shape_manager import ShapeManager
from utils.camera_sim import Camera
from utils.data_transfer import escrever_dados_alvo
from config import vision_config as settings
from config import mission_config as m_settings

def run_vision_thread(stop_event: Event):

    """
    Executa o loop principal de processamento de visão em uma thread separada.

    Inicializa a câmera e os controladores de visão, e então entra
    em um loop contínuo (enquanto `stop_event` não for acionado) para:

    1.  Capturar o frame: Lê o quadro mais recente da câmera.
    2.  Processar a imagem: Utiliza o `CentralizationController` para analisar
        o frame.
    3.  Detectar a figura: Tenta encontrar a forma alvo (`TARGET_SHAPE`)
        definida nas configurações da missão.
    4.  Gerar saída (JSON): Escreve os resultados em um arquivo 
        indicando se o alvo foi (encontrado e suas características
        (erro `dx`, `dy`, `distance_m`).

    A thread também exibe o vídeo processado em uma janela do OpenCV e
    pode ser interrompida pressionando 'q'.

    Args:
        stop_event (Event): Objeto de threading.Event() usado para sinalizar
                            a esta thread que ela deve parar.
    """
    
    print("[VISÃO] Iniciando script de VISÃO...")
    camera = None # Define fora do try para o finally
    try:
        # 1. Inicializa os componentes de visão
        camera = Camera()
        camera.start()
        shape_manager = ShapeManager() 
        controller = CentralizationController(shape_manager=shape_manager,camera_width=settings.CAMERA_WIDTH,camera_height=settings.CAMERA_HEIGHT)
        print("[VISÃO] Componentes de visão inicializados.")
        
    except Exception as e:
        print(f"!!! [VISÃO] ERRO CRÍTICO NA INICIALIZAÇÃO: {e} !!!")
        print("[VISÃO] Script de visão não pode continuar.")
        return # Encerra esta thread

    # Loop Principal de Processamento
    try:
        while not stop_event.is_set():
            
            ret, frame = camera.read()

            if not ret:
                time.sleep(0.1)
                continue
            
            display_frame = frame.copy()

            # Processa o frame
            vision_data = controller.calculate_control_data(frame=frame,target_shape_name=m_settings.TARGET_SHAPE,target_real_width_cm=settings.PLATFORM_WIDTH_CM)
            
            # Prepara os dados para salvar
            if vision_data is not None:
                # Alvo ENCONTRADO!
                data_to_save = {"found": True, "dx": vision_data.error_x_px, "dy": vision_data.error_y_px, "distance_m": vision_data.distance_z_m, "timestamp": time.time()}
                # (Opcional) Desenha no frame de display
                center = (int(vision_data.robust_center[0]), int(vision_data.robust_center[1]))
                cv2.drawContours(display_frame, [vision_data.contour], -1, (0, 255, 0), 2)
                cv2.circle(display_frame, center, 5, (0, 0, 255), -1)
            else:
                # Alvo NÃO ENCONTRADO!
                data_to_save = {"found": False, "dx": 0.0, "dy": 0.0, "distance_m": 0.0, "timestamp": time.time()}

            # Escreve os dados no arquivo
            escrever_dados_alvo(data_to_save)

            cv2.imshow("Stream da Visao", display_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("[VISÃO] Janela fechada pelo usuário ('q').")
                stop_event.set() # Sinaliza para a missão principal parar também

    except Exception as e:
        print(f"!!! [VISÃO] ERRO INESPERADO NO LOOP: {e} !!!")
    finally:
        # Limpeza
        if camera:
            camera.stop()
        cv2.destroyAllWindows() 
        escrever_dados_alvo({"found": False, "dx": 0.0, "dy": 0.0, "distance_m": 0.0})
        print("[VISÃO] Script de visão finalizado.")