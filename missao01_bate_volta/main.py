import cv2
import time
import json
from threading import Lock, Thread, Event

# --- Imports do run_vision.py ---
from utils.centralization import CentralizationController
from core.shape_manager import ShapeManager
from config import vision_config as settings
from utils.camera_sim import Camera # A câmera que usa RTSP
from utils.data_transfer import escrever_dados_alvo # Corrigido

# --- Imports do test_detecction.py ---
from control import funcoes_controle5

# --- Constantes do run_vision.py ---
# CAMERA_WIDTH = 640
# CAMERA_HEIGHT = 480
TARGET_SHAPE = "estrela"   # Nome da forma que você está procurando

# --- Constantes do test_detecction.py ---
ALTITUDE_DE_BUSCA = 3.0
PASSO_DA_VARREDURA = 1.0   # Distância (m) entre as "pernas" da varredura em S
VEL_LATERAL = 1.0          
VEL_FRENTE = 1.0           

# --- LÓGICA DE VISÃO (Original de run_vision.py) ---
# Esta função rodará em uma Thread separada

def run_vision_thread(stop_event: Event):
    print("[VISÃO] Iniciando script de VISÃO...")

    # 1. Inicializa os componentes
    try:
        # (A) Câmera
        camera = Camera(resolution=(settings.CAMERA_WIDTH, settings.CAMERA_HEIGHT))
        camera.start()

        # (B) Processador de Formas
        shape_manager = ShapeManager() 
        
        # (C) Controlador de Centralização (a parte da Visão)
        controller = CentralizationController(shape_manager=shape_manager,camera_width=settings.CAMERA_WIDTH,camera_height=settings.CAMERA_HEIGHT)
        print("[VISÃO] Componentes de visão inicializados.")
        
    except Exception as e:
        print(f"!!! [VISÃO] ERRO CRÍTICO NA INICIALIZAÇÃO: {e} !!!")
        print("[VISÃO] Script de visão não pode continuar.")
        return # Encerra esta thread

    # 2. Loop Principal de Processamento
    try:
        # O loop agora também verifica o evento de parada
        while not stop_event.is_set():
            # Etapa 1: Captura um frame da câmera
            ret, frame = camera.read()
            if not ret:
                # print("Aguardando frame da câmera...") # Evita spam
                time.sleep(0.1)
                continue
            
            # Etapa 2: Chama o controller para processar o frame
            vision_data = controller.calculate_control_data(frame=frame,target_shape_name=TARGET_SHAPE,target_real_width_cm=settings.PLATFORM_WIDTH_CM
            )
            
            # Etapa 3: Verifica se o alvo foi encontrado
            if vision_data is not None:
                # Alvo ENCONTRADO!
                data_to_save = {
                    "found": True,
                    "dx": vision_data.error_x_px, 
                    "dy": vision_data.error_y_px,
                    "distance_m": vision_data.distance_z_m,
                    "timestamp": time.time()
                }
            else:
                # Alvo NÃO ENCONTRADO!
                data_to_save = {
                    "found": False,
                    "dx": 0.0,
                    "dy": 0.0,
                    "distance_m": 0.0,
                    "timestamp": time.time()
                }

            # Etapa 4: Escreve os dados no arquivo
            escrever_dados_alvo(data_to_save)

            # Controla a taxa de processamento (ex: 20 FPS)
            # time.sleep(0.05) # O read() da câmera já pode ser bloqueante
            pass # Deixa a câmera ditar o ritmo

    except KeyboardInterrupt:
        print("\n[VISÃO] Encerrando (recebeu Ctrl+C)...")
    except Exception as e:
        print(f"!!! [VISÃO] ERRO INESPERADO NO LOOP: {e} !!!")
    finally:
        # 3. Limpeza
        camera.stop()
        escrever_dados_alvo({"found": False, "dx": 0.0, "dy": 0.0, "distance_m": 0.0})
        print("[VISÃO] Script de visão finalizado.")


# --- LÓGICA DE MISSÃO (Original de test_detecction.py) ---
# Esta será a função principal do script

def main_mission():
    
    print("[MISSÃO] INICIANDO MISSÃO)")
    
    Uno = None
    stop_vision_event = Event() # Cria o "sinal de parada"

    # --- Inicia a thread de visão ANTES de tudo ---
    print("[SISTEMA] Iniciando thread de visão em background...")
    vision_thread = Thread(target=run_vision_thread, args=(stop_vision_event,), daemon=True)
    vision_thread.start()
    
    # Dá um tempo para a câmera RTSP e a visão inicializarem
    print("[SISTEMA] Aguardando 5s para a visão estabilizar...")
    time.sleep(5) 

    try:
        
        Uno = funcoes_controle5.conectar_uno()
        print("[MISSÃO] Conexão com o Uno estabelecida.")
        time.sleep(1) 

        funcoes_controle5.armar_uno(Uno)
        print("[MISSÃO] Uno armado pronto para decolagem.")
        time.sleep(1)

        print(f"[MISSÃO] Decolando para {ALTITUDE_DE_BUSCA}m...")
        funcoes_controle5.decolar_uno(Uno, ALTITUDE_DE_BUSCA)
        print("[MISSÃO] Altitude de busca atingida.")
        
        
        print(f"[MISSÃO] Iniciando varredura da arena...")
      
        sucesso_busca = funcoes_controle5.varredura_arena(Uno, 
                                                         passo_frente=PASSO_DA_VARREDURA, 
                                                         velocidade_lateral=VEL_LATERAL, 
                                                         velocidade_frente=VEL_FRENTE)
        
        
        if sucesso_busca:
            print("[MISSÃO] Alvo identificado! Iniciando centralização.")
            time.sleep(1)
            
            sucesso_centralizacao = funcoes_controle5.centralizacao(Uno)
            
            if sucesso_centralizacao:
                print("[MISSÃO] Centralização concluída. Iniciando pouso sobre o alvo.")
            
                funcoes_controle5.pousar_no_alvo_e_desarmar(Uno)
                print(f"[MISSÃO] Pouso sobre alvo concluído.")
                
                print(f"[MISSÃO] Re-armando o drone para decolagem...")
                funcoes_controle5.armar_uno(Uno)
            
                print(f"[MISSÃO] Subindo de volta para {ALTITUDE_DE_BUSCA}m para o RTL...")
                funcoes_controle5.decolar_uno(Uno, ALTITUDE_DE_BUSCA)
                print("[MISSÃO] Altitude de segurança para RTL atingida.")
                
                
            else:
                print("[MISSÃO] Falha ao centralizar no alvo. Abortando pouso.")
        
        else:
            print("[MISSÃO] Alvo não encontrado após varredura completa.")

    except Exception as e:
        print(f"\n!!! [MISSÃO] ERRO CRÍTICO NA MISSÃO: {e} !!!")
        print("[MISSÃO] Uma exceção ocorreu. Tentando ativar RTL por segurança...")

    finally:
        # --- FASE 4: FINALIZAÇÃO (SEMPRE EXECUTA) ---
        
        print("\n[MISSÃO] Fase final: Retornando para base.")
        
        if Uno:
            if Uno.armed:
                print("[MISSÃO] Ativando RTL...")
                funcoes_controle5.return_to_launch(Uno, altitude_retorno_m=0)
                print("[MISSÃO] Pouso e desarme na base concluídos.")
            elif not Uno.armed and Uno.location.global_relative_frame.alt < 0.1:
                 print("[MISSÃO] Drone já está no chão após pouso no alvo. Missão concluída sem RTL.")
            else:
                 try:
                     print("[MISSÃO] Estado inesperado (desarmado, mas não no chão?). Tentando armar e RTL...")
                     funcoes_controle5.armar_uno(Uno)
                     print("[MISSÃO] Ativando RTL de emergência...")
                     funcoes_controle5.return_to_launch(Uno, altitude_retorno_m=0)
                     print("[MISSÃO] Pouso e desarme na base concluídos.")
                 except Exception as rtl_err:
                     print(f"[MISSÃO] Falha ao tentar RTL de emergência: {rtl_err}")
        else:
            print("[MISSÃO] Conexão com o drone nunca foi estabelecida. Finalizando script.")
            
        print("--- [MISSÃO] MISSÃO FINALIZADA ---")

        # --- Sinaliza para a thread de visão parar ---
        print("[SISTEMA] Solicitando parada da thread de visão...")
        stop_vision_event.set() # Envia o sinal de parada
        vision_thread.join(timeout=3.0) # Espera a thread terminar (por até 3s)
        print("[SISTEMA] Thread de visão finalizada.")


# Ponto de entrada do script: Chama a função main() quando o arquivo é executado
if __name__ == "__main__":
    
    # Verificação de segurança da visão (do run_vision.py)
    # Corrigido para usar o nome correto da constante
    if settings.DISTANCE_F_PX == 0.0:
        print("="*50)
        print(f"!!! ATENÇÃO: settings.DISTANCE_F_PX não foi calibrado (valor: {settings.DISTANCE_F_PX})! !!!")
        print("A 'distance_z_m' será incorreta ou sempre 0.")
        print("Por favor, ajuste o 'config/vision_config.py' com o valor calibrado.")
        print("="*50)
        time.sleep(3)
        
    main_mission() # Inicia a missão