import time
from threading import Thread, Event 
from dronekit import connect, VehicleMode

from vision_manager import run_vision_thread
from mission_control import MissionManager

def main():
    print("INICIANDO MISSÃO (Máquina de Estados + Thread de Visão)")
    Uno = None 
    
    # --- Inicia a Thread de Visão ---
    stop_vision_event = Event() # Sinal para parar a thread
    vision_thread = Thread(target=run_vision_thread, args=(stop_vision_event,), daemon=True)
    vision_thread.start()

    print("[SISTEMA] Aguardando 5s para a visão estabilizar...")
    time.sleep(5) 
    
    try:
        # --- Conecta ao Drone ---
        print("[SISTEMA] Conectando ao drone...")
        Uno = connect("udp:127.0.0.1:14550", wait_ready = True)
        print("[SISTEMA] Conexão com o drone estabelecida.")

        # --- Cria e Roda a Máquina de Estados ---
        mission_manager = MissionManager(vehicle=Uno, stop_event=stop_vision_event)
        mission_manager.run_state_machine()

    except Exception as e:
        print(f"\n!!! ERRO CRÍTICO NA CONEXÃO OU INICIALIZAÇÃO: {e} !!!")
        print("Não foi possível iniciar a máquina de estados. Encerrando...")
        
        # Tenta um RTL de emergência se a conexão foi estabelecida mas falhou antes da missão
        if Uno and Uno.armed:
             try:
                 print("Tentando RTL de emergência na inicialização...")
                 Uno.mode = VehicleMode("RTL")
                 while Uno.armed: time.sleep(1)
             except Exception as rtl_err:
                 print(f"Falha no RTL de emergência: {rtl_err}")
        
    finally:
        # Limpeza 
        print("\n--- MISSÃO FINALIZADA (MAIN) ---")

        print("[SISTEMA] Solicitando parada da thread de visão...")
        stop_vision_event.set() # Envia o sinal de parada
        vision_thread.join(timeout=3.0) # Espera a thread terminar
        
        if vision_thread.is_alive():
            print("[SISTEMA] WARN: Thread de visão não parou no tempo.")

        print("[SISTEMA] Thread de visão finalizada.")
        
        if Uno:
            Uno.close()
            print("[SISTEMA] Conexão com o drone fechada.")

        print("[SISTEMA] Script principal encerrado.")


if __name__ == "__main__": 
    main()