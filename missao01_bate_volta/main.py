# test_detecction.py (Agora como o controlador principal do Webots)

# --- APIs do Webots ---
from controller import Robot
# (Nota: O Webots pode ter classes específicas de Drone,
#  mas vamos usar a 'Robot' genérica por agora)
import numpy as np
import cv2
import time

# --- Seus Módulos de Visão ---
# (Estes SÃO compatíveis e podem ser usados!)
from core.shape_manager import ShapeManager
from utils.centralization import CentralizationController
from config import vision_config as settings

# --- Seus Módulos de Controlo ---
# !!! ATENÇÃO: ISTO NÃO VAI FUNCIONAR NO WEBOTS !!!
# from control import funcoes_controle5 
# (Vamos focar-nos na visão primeiro)

# --- Constantes da Missão ---
ALTITUDE_DE_BUSCA = 3.0
TARGET_SHAPE = "estrela"
CAMERA_WIDTH = 640  # Valor padrão, será atualizado
CAMERA_HEIGHT = 480 # Valor padrão, será atualizado

def main():
    
    # 1. INICIALIZAÇÃO DO WEBOTS
    print("Iniciando controlador do Webots...")
    robot = Robot()
    timestep = int(robot.getBasicTimeStep()) # Obtém o passo de simulação

    # 2. INICIALIZAÇÃO DA CÂMARA (O MODO CORRETO)
    try:
        # 'camera' deve ser o nome que deu ao nó da câmara no Webots
        camera_node = robot.getCamera("camera") 
        camera_node.enable(timestep) # Liga a câmara
        
        # Obtém a largura e altura reais da câmara no simulador
        CAMERA_WIDTH = camera_node.getWidth()
        CAMERA_HEIGHT = camera_node.getHeight()
        print(f"Câmara do Webots '{camera_node.getName()}' inicializada ({CAMERA_WIDTH}x{CAMERA_HEIGHT}).")
        
    except Exception as e:
        print(f"!!! ERRO: Falha ao encontrar/ligar a câmara no Webots: {e} !!!")
        print("Verifique o 'name' do nó da câmara no seu robô (ex: 'camera').")
        return

    # 3. INICIALIZAÇÃO DOS COMPONENTES DE VISÃO
    # (Isto é o que o run_vision.py fazia)
    shape_manager = ShapeManager() 
    vision_controller = CentralizationController(
        shape_manager=shape_manager,
        camera_width=CAMERA_WIDTH,
        camera_height=CAMERA_HEIGHT
    )
    print("Componentes de visão (ShapeManager, CentralizationController) inicializados.")

    # 4. INICIALIZAÇÃO DO CONTROLO DO DRONE (API DO WEBOTS)
    # Aqui você precisaria de inicializar os motores, GPS, Gyro, etc., do Webots
    # Ex: gps = robot.getDevice("gps")
    # Ex: motor1 = robot.getDevice("motor1")
    # ...
    # O 'funcoes_controle5' (DroneKit) NÃO funcionará aqui.
    print("A inicializar dispositivos do drone (GPS, motores... - API Webots)")
    
    
    # 5. EXECUÇÃO DA MISSÃO (O LOOP PRINCIPAL)
    print("INICIANDO MISSÃO)")
    
    # --- Aqui entraria a sua lógica de decolagem ---
    # (Usando a API do Webots para controlar os motores e atingir 3.0m)
    print(f"Decolando para {ALTITUDE_DE_BUSCA}m...")
    # ... (código de decolagem do Webots) ...
    
    
    # O loop principal da simulação. Substitui todos os 'time.sleep()'
    while robot.step(timestep) != -1:
        
        # --- ETAPA DE VISÃO (O que o run_vision.py faria) ---
        
        # 1. Obtém a imagem da câmara do Webots
        img_data = camera_node.getImage()
        if img_data is None:
            continue

        # 2. Converte a imagem para o formato OpenCV (BGR)
        # O Webots fornece BGRA num buffer 1D, o OpenCV usa BGR num array 3D
        frame = np.frombuffer(img_data, np.uint8).reshape((CAMERA_HEIGHT, CAMERA_WIDTH, 4))
        frame_bgr = frame[:, :, :3] # Remove o canal Alpha (transparência)
        
        # (Opcional) Mostrar a imagem que o OpenCV está a ver
        # cv2.imshow("Visao", frame_bgr)
        # cv2.waitKey(1)
        
        # 3. Processa o frame
        vision_data = vision_controller.calculate_control_data(
            frame=frame_bgr,
            target_shape_name=TARGET_SHAPE,
            target_real_width_cm=settings.PLATFORM_WIDTH_CM
        )

        # 4. Agora, 'vision_data' está disponível DIRETAMENTE
        #    Não precisamos de ficheiros JSON!
        
        
        # --- ETAPA DE CONTROLO (O que o test_detecction.py faria) ---
        
        # Agora, use 'vision_data' para tomar decisões
        if vision_data is not None:
            # Alvo encontrado!
            print(f"Alvo encontrado: dx={vision_data.error_x_px:.1f}, dy={vision_data.error_y_px:.1f}")
            
            # --- Aqui entraria a sua lógica de centralização ---
            # (Usando os erros vision_data.error_x_px e .error_y_px
            # para calcular a velocidade dos motores do Webots)
            
        else:
            # Alvo não encontrado
            print("Procurando alvo...")
            
            # --- Aqui entraria a sua lógica de varredura ---
            # (Movendo o drone com a API do Webots)

        # ... (Resto da sua lógica de missão: pousar, etc.) ...


if __name__ == "__main__":
    main()