# Implementado máquina de estados E thread de visão paralela

import cv2 # Necessário para o imshow
import time
import json
from threading import Lock, Thread, Event # Necessário para as threads

# --- Imports da Missão ---
from control import funcoes_controle5
from utils.centralization import CentralizationController
from core.shape_manager import ShapeManager
from config import vision_config as settings
from utils.camera_sim import Camera
from utils.data_transfer import escrever_dados_alvo

# --- Constantes da Visão ---
TARGET_SHAPE = "pentagono" # Certifique-se que é o mesmo nome do detector

# --- Constantes da Missão ---
ALTITUDE_DE_BUSCA = 2.0
PASSO_DA_VARREDURA = 1.0   
VEL_LATERAL = 1.0          
VEL_FRENTE = 1.0           

# --- Definição dos Estados ---
ESTADO_INICIANDO = "INICIANDO"
ESTADO_ARMANDO = "ARMANDO"
ESTADO_DECOLANDO = "DECOLANDO"
ESTADO_BUSCANDO = "BUSCANDO"
ESTADO_CENTRALIZANDO = "CENTRALIZANDO"
ESTADO_POUSANDO_ALVO = "POUSANDO_ALVO"
ESTADO_RE_ARMANDO = "RE_ARMANDO"
ESTADO_RE_DECOLANDO = "RE_DECOLANDO"
ESTADO_RETORNANDO_RTL = "RETORNANDO_RTL"
ESTADO_FALHA_CRITICA = "FALHA_CRITICA"
ESTADO_FINALIZADO = "FINALIZADO"


# ---------------------------------------------------------------------
# --- TAREFA DE VISÃO (Roda em uma Thread separada) ---
# ---------------------------------------------------------------------
def run_vision_thread(stop_event: Event):
    print("[VISÃO] Iniciando script de VISÃO...")
    camera = None # Define fora do try para o finally
    try:
        # 1. Inicializa os componentes de visão
        camera = Camera(resolution=(CAMERA_WIDTH, CAMERA_HEIGHT))
        camera.start()
        shape_manager = ShapeManager() 
        controller = CentralizationController(shape_manager=shape_manager,camera_width=CAMERA_WIDTH,camera_height=CAMERA_HEIGHT)
        print("[VISÃO] Componentes de visão inicializados.")
        
    except Exception as e:
        print(f"!!! [VISÃO] ERRO CRÍTICO NA INICIALIZAÇÃO: {e} !!!")
        print("[VISÃO] Script de visão não pode continuar.")
        return # Encerra esta thread

    # 2. Loop Principal de Processamento
    try:
        while not stop_event.is_set():
            # Etapa 1: Captura um frame da câmera
            ret, frame = camera.read()
            if not ret:
                time.sleep(0.1)
                continue
            
            # (Opcional) Copia o frame para desenhar
            display_frame = frame.copy()
            
            # Etapa 2: Processa o frame
            vision_data = controller.calculate_control_data(frame=frame,target_shape_name=TARGET_SHAPE,target_real_width_cm=settings.PLATFORM_WIDTH_CM)
            
            # Etapa 3: Prepara os dados para salvar
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

            # Etapa 4: Escreve os dados no arquivo
            escrever_dados_alvo(data_to_save)

            # --- É AQUI QUE VOCÊ ADICIONA O CÓDIGO ---
            cv2.imshow("Stream da Visao", display_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("[VISÃO] Janela fechada pelo usuário ('q').")
                stop_event.set() # Sinaliza para a missão principal parar também

    except Exception as e:
        print(f"!!! [VISÃO] ERRO INESPERADO NO LOOP: {e} !!!")
    finally:
        # 3. Limpeza
        if camera:
            camera.stop()
        cv2.destroyAllWindows() # Fecha a janela do OpenCV
        escrever_dados_alvo({"found": False, "dx": 0.0, "dy": 0.0, "distance_m": 0.0})
        print("[VISÃO] Script de visão finalizado.")


# ---------------------------------------------------------------------
# --- TAREFA DE CONTROLE (Roda na Thread principal) ---
# ---------------------------------------------------------------------
def main():
    
    print("INICIANDO MISSÃO (Máquina de Estados + Thread de Visão)")
    
    Uno = None
    estado_atual = ESTADO_INICIANDO
    ultima_excecao = None   

    # --- Inicia a Thread de Visão ANTES de tudo ---
    stop_vision_event = Event() # Sinal para parar a thread
    vision_thread = Thread(target=run_vision_thread, args=(stop_vision_event,), daemon=True)
    vision_thread.start()

    print("[SISTEMA] Aguardando 5s para a visão estabilizar...")
    time.sleep(5) 

    # Loop principal da Máquina de Estados
    while estado_atual != ESTADO_FINALIZADO and not stop_vision_event.is_set(): 
        try:
            if estado_atual == ESTADO_INICIANDO:
                print(f"[ESTADO] {estado_atual}: Conectando ao drone...")
                Uno = funcoes_controle5.conectar_uno() 
                print("Conexão com o Uno estabelecida.")
                time.sleep(1)
                estado_atual = ESTADO_ARMANDO

            elif estado_atual == ESTADO_ARMANDO:
                print(f"[ESTADO] {estado_atual}: Armando o drone...")
                funcoes_controle5.armar_uno(Uno)
                print("Uno armado pronto para decolagem.")
                time.sleep(1)
                estado_atual = ESTADO_DECOLANDO
            
            elif estado_atual == ESTADO_DECOLANDO:
                print(f"[ESTADO] {estado_atual}: Subindo para {ALTITUDE_DE_BUSCA}m...")
                funcoes_controle5.decolar_uno(Uno, ALTITUDE_DE_BUSCA)
                print("Altitude de busca atingida.")
                estado_atual = ESTADO_BUSCANDO

            # ... (Restante dos seus estados: BUSCANDO, CENTRALIZANDO, etc.) ...
            elif estado_atual == ESTADO_BUSCANDO:
                print(f"[ESTADO] {estado_atual}: Iniciando varredura da arena...")
                sucesso_busca = funcoes_controle5.varredura_arena(Uno, 
                                                                 passo_frente=PASSO_DA_VARREDURA, 
                                                                 velocidade_lateral=VEL_LATERAL, 
                                                                 velocidade_frente=VEL_FRENTE)
                if sucesso_busca:
                    print("Alvo identificado! Próximo estado: CENTRALIZANDO.")
                    estado_atual = ESTADO_CENTRALIZANDO
                else:
                    print("Alvo não encontrado. Próximo estado: RETORNANDO_RTL.")
                    estado_atual = ESTADO_RETORNANDO_RTL

            elif estado_atual == ESTADO_CENTRALIZANDO:
                print(f"[ESTADO] {estado_atual}: Iniciando centralização...")
                time.sleep(1)
                sucesso_centralizacao = funcoes_controle5.centralizacao(Uno)
                if sucesso_centralizacao:
                    print("Centralização concluída. Próximo estado: POUSANDO_ALVO.")
                    estado_atual = ESTADO_POUSANDO_ALVO
                else:
                    print("Falha ao centralizar. Próximo estado: RETORNANDO_RTL.")
                    estado_atual = ESTADO_RETORNANDO_RTL

            elif estado_atual == ESTADO_POUSANDO_ALVO:
                print(f"[ESTADO] {estado_atual}: Iniciando pouso sobre o alvo.")
                funcoes_controle5.pousar_no_alvo_e_desarmar(Uno)
                print("Pouso sobre alvo concluído.")
                estado_atual = ESTADO_RE_ARMANDO
                
            elif estado_atual == ESTADO_RE_ARMANDO:
                print(f"[ESTADO] {estado_atual}: Re-armando o drone para subida...")
                funcoes_controle5.armar_uno(Uno)
                print("Re-armado.")
                estado_atual = ESTADO_RE_DECOLANDO

            elif estado_atual == ESTADO_RE_DECOLANDO:
                print(f"[ESTADO] {estado_atual}: Subindo de volta para {ALTITUDE_DE_BUSCA}m...")
                funcoes_controle5.decolar_uno(Uno, ALTITUDE_DE_BUSCA)
                print("Altitude de segurança para RTL atingida.")
                estado_atual = ESTADO_RETORNANDO_RTL
                
            elif estado_atual == ESTADO_RETORNANDO_RTL:
                print(f"[ESTADO] {estado_atual}: Fase final.")
                if Uno and Uno.armed:
                    print("[MISSÃO] Ativando RTL...")
                    funcoes_controle5.return_to_launch(Uno, altitude_retorno_m=0)
                    print("[MISSÃO] Pouso e desarme na base concluídos.")
                elif Uno and not Uno.armed:
                    print("[MISSÃO] Drone já está no chão. Missão concluída sem RTL.")
                else:
                    print("[MISSÃO] Estado inesperado ou sem conexão. Não é possível RTL.")
                estado_atual = ESTADO_FINALIZADO
                
            elif estado_atual == ESTADO_FALHA_CRITICA:
                print(f"[ESTADO] {estado_atual}: Tratando erro: {ultima_excecao}")
                if Uno:
                    print("Tentando RTL de emergência...")
                    try:
                        if Uno.armed: funcoes_controle5.return_to_launch(Uno, altitude_retorno_m=0)
                        else: print("Drone estava desarmado.")
                    except Exception as rtl_err: print(f"Falha ao tentar RTL de emergência: {rtl_err}")
                else: print("Sem conexão com o drone. Impossível executar RTL.")
                estado_atual = ESTADO_FINALIZADO

        except Exception as e:
            print(f"\n!!! ERRO CRÍTICO NA MISSÃO (Estado: {estado_atual}): {e} !!!")
            ultima_excecao = e
            estado_atual = ESTADO_FALHA_CRITICA

    # --- Limpeza Pós-Loop ---
    print("\n--- MISSÃO FINALIZADA ---")

    print("[SISTEMA] Solicitando parada da thread de visão...")
    stop_vision_event.set() # Envia o sinal de parada
    vision_thread.join(timeout=3.0) # Espera a thread terminar
    print("[SISTEMA] Thread de visão finalizada.")

if __name__ == "__main__":
    main()
