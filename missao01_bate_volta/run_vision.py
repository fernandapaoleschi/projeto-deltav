import cv2
import time
import json
from threading import Lock, Thread

# (Assumindo que run_vision.py está na raiz de missao01_bate_volta)
from utils.centralization import CentralizationController
from core.shape_manager import ShapeManager
from config import vision_config as settings
from utils.camera_sim import Camera
from utils.data_transfer import escrever_dados_alvo


CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
TARGET_SHAPE = "estrela"   # Nome da forma que você está procurando
#TARGET_REAL_WIDTH_CM = 80.0  # Largura real do seu alvo em CM

# --- SCRIPT PRINCIPAL (run_vision.py) ---

def main():
    print("Iniciando script de VISÃO...")

    # 1. Inicializa os componentes
    try:
        # (A) Câmera
        camera = Camera(resolution=(CAMERA_WIDTH, CAMERA_HEIGHT))
        camera.start()

        # (B) Processador de Formas
        shape_manager = ShapeManager() 
        
        # (C) Controlador de Centralização (a parte da Visão)
        controller = CentralizationController(shape_manager=shape_manager,camera_width=CAMERA_WIDTH,camera_height=CAMERA_HEIGHT)
        print("Componentes de visão inicializados.")
        
    except Exception as e:
        print(f"!!! ERRO CRÍTICO NA INICIALIZAÇÃO: {e} !!!")
        print("Script de visão não pode continuar.")
        return

    # 2. Loop Principal de Processamento
    try:
        while True:
            # Etapa 1: Captura um frame da câmera
            ret, frame = camera.read()
            if not ret:
                print("Aguardando frame da câmera...")
                time.sleep(0.1)
                continue
            
            # Etapa 2: Chama o controller para processar o frame
            # (Este é o método que retorna o objeto ShapeData)
            vision_data = controller.calculate_control_data(frame=frame,target_shape_name=TARGET_SHAPE,target_real_width_cm=settings.PLATFORM_WIDTH_CM
            )
            
            # Etapa 3: Verifica se o alvo foi encontrado
            if vision_data is not None:
                # Alvo ENCONTRADO!
                # Prepara o dicionário para salvar em JSON
                data_to_save = {
                    "found": True,
                    # O seu `def centralizacao` espera "dx" e "dy"
                    "dx": vision_data.error_x_px, 
                    "dy": vision_data.error_y_px,
                    "distance_m": vision_data.distance_z_m,
                    "timestamp": time.time()
                }
                
                # (Opcional) Mostrar na tela o que a visão está fazendo
                # print(f"Alvo: dx={data_to_save['dx']:.1f}, dy={data_to_save['dy']:.1f}, dist={data_to_save['distance_m']:.2f}m")

            else:
                # Alvo NÃO ENCONTRADO!
                # Envia um "heartbeat" (pulsação) dizendo que não encontrou
                data_to_save = {
                    "found": False,
                    "dx": 0.0,
                    "dy": 0.0,
                    "distance_m": 0.0,
                    "timestamp": time.time()
                }
                # print("Alvo não encontrado.")

            # Etapa 4: Escreve os dados no arquivo
            # (Esta é a função que o `ler_arquivo_alvo()` do seu controle irá ler)
            escrever_dados_alvo(data_to_save)

            # Controla a taxa de processamento (ex: 20 FPS)
            time.sleep(0.05) 

    except KeyboardInterrupt:
        print("\nEncerrando script de visão (Ctrl+C)...")
    except Exception as e:
        print(f"!!! ERRO INESPERADO NO LOOP PRINCIPAL: {e} !!!")
    finally:
        # 3. Limpeza
        # Garante que a câmera seja desligada corretamente
        camera.stop()
        # Escreve um último "not found" para o controle não ficar preso
        escrever_dados_alvo({"found": False, "dx": 0.0, "dy": 0.0, "distance_m": 0.0})
        print("Script de visão finalizado.")


if __name__ == "__main__":
    # Verifica se a constante FOCAL_LENGTH_PIXELS foi calibrada
    if settings.FOCAL_LENGTH_PIXELS == 0.0:
        print("="*50)
        print("!!! ATENÇÃO: FOCAL_LENGTH_PIXELS não foi calibrado! !!!")
        print("A 'distance_z_m' será sempre 0.")
        print("Execute o script 'calibrate_camera.py' primeiro.")
        print("="*50)
        time.sleep(3)
        
    main()