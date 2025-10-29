#funcoes_controle5

from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
import time
import json


CONNECTION_STRING = "udp:127.0.0.1:14550"   # Conexão ArduPilot SITL
PIXEL_TO_METER = 0.002                      # Pixel para metro
CENTER_THRESHOLD_M = 0.15                   # Tolerância centralização
VELOCITY_SEND_FREQ = 10                     # Frequência de envio de comandos de velocidade
TARGET_JSON_PATH = "target.json"            # Arquivo de Visão


def conectar_uno(connection_string = CONNECTION_STRING, wait_ready=True):

    print("Conectando ao Uno", connection_string)
    Uno = connect(connection_string, wait_ready=wait_ready)
    print("Conectado. Firmware:", Uno.version)
    return Uno


def armar_uno(Uno, timeout=20):

    print("Armando Uno...")
    Uno.mode = VehicleMode("GUIDED")
    
    # Espera ficar armável
    inicio = time.time()
    while not Uno.is_armable:
        if time.time() - inicio > timeout:
            raise RuntimeError("Uno não armou dentro do tempo")
        print("Aguardando Uno ficar armável...")
        time.sleep(1)
        
    Uno.armed = True

    inicio = time.time()
    while not Uno.armed:
         Uno.armed = True
        if time.time() - inicio > timeout:
            raise RuntimeError("Falha ao armar o Uno")
        print("Aguardando armar...")
        time.sleep(0.5)
    print("Uno armado.")


def decolar_uno(Uno, altitude_m=3.0):

    print(f"Uno decolando até {altitude_m} m...")
    Uno.simple_takeoff(altitude_m)
    
    while True:
        altitude_atual = Uno.location.global_relative_frame.alt
        print(f"Altitude atual: {altitude_atual:.2f} m")
        if altitude_atual >= altitude_m * 0.95:
            print("Altitude desejada atingida.")
            break
        time.sleep(0.5)


def movimentacao_velocidade(Uno, vx, vy, vz, duration):

    
    print(f"Movimentação_Velocidade vx={vx:.2f}, vy={vy:.2f}, vz={vz:.2f}, dur={duration}s")
    
    type_mask = 0b0000010111000111
    rate = VELOCITY_SEND_FREQ
    interval = 1.0 / rate
    count = int(duration * rate)

   
    for _ in range(count):
        msg = Uno.message_factory.set_position_target_local_ned_encode(
            0,       # time_boot_ms (ignored)
            0, 0,    # target system, component (ignored)
            mavutil.mavlink.MAV_FRAME_BODY_NED, # Frame de referência
            type_mask, # Ignorar pos/accel/yaw
            0, 0, 0, # Posições x, y, z (ignored)
            vx, vy, vz, # Velocidades vx, vy, vz (m/s)
            0, 0, 0, # Acelerações ax, ay, az (ignored)
            0, 0     # yaw, yaw_rate (ignored)
        )
        Uno.send_mavlink(msg)
        Uno.flush()
        time.sleep(interval)
        

def varredura_arena(Uno, passo_frente=1.0, velocidade_lateral=1.0, velocidade_frente=1.0, intervalo_chegagem=0.2):
    
    arena_largura = 10.0
    arena_profundidade = 10.0
    print(f"Iniciando busca do alvo (Checagem a cada {intervalo_chegagem}s).")

    tempo_varredura_lateral = arena_largura / velocidade_lateral
    tempo_passo_frente = passo_frente / velocidade_frente
    num_passos = int(arena_profundidade / passo_frente)
    num_chegagens_lateral = int(tempo_varredura_lateral / intervalo_chegagem)
    num_chegagens_frente = int(tempo_passo_frente / intervalo_chegagem)

    print(f"Passo 0: Movendo {arena_largura}m para a esquerda...")
    for _ in range(num_chegagens_lateral):
        movimentacao_velocidade(Uno, 0, -velocidade_lateral, 0, intervalo_chegagem)
        if ler_arquivo_alvo()["found"]:
            print("Alvo encontrado! Parando varredura.")
            movimentacao_velocidade(Uno, 0, 0, 0, 0.1)
            return True

   
    for i in range(num_passos):
        print(f"Varredura: Passo {i+1}/{num_passos}")

        print(f"...avançando {passo_frente}m para frente.")
        for _ in range(num_chegagens_frente):
            movimentacao_velocidade(Uno, velocidade_frente, 0, 0, intervalo_chegagem)
            if ler_arquivo_alvo()["found"]:
                print("Alvo encontrado! Parando varredura.")
                movimentacao_velocidade(Uno, 0, 0, 0, 0.1)
                return True

        
        vy_atual = velocidade_lateral if (i % 2 == 0) else -velocidade_lateral
        direcao_str = "Direita" if (vy_atual > 0) else "Esquerda"
        
        print(f"...varrendo {arena_largura}m para a {direcao_str}.")
        for _ in range(num_chegagens_lateral):
            movimentacao_velocidade(Uno, 0, vy_atual, 0, intervalo_chegagem)
            if ler_arquivo_alvo()["found"]:
                print("Alvo encontrado! Parando varredura.")
                movimentacao_velocidade(Uno, 0, 0, 0, 0.1)
                return True

    print(f"Varredura completa da arena. Alvo não encontrado.")
    return False


def ler_arquivo_alvo(path=TARGET_JSON_PATH):
    try:
        with open(path, "r") as f:
            data = json.load(f)
            found = bool(data.get("found", False))
            dx = float(data.get("dx", 0.0))
            dy = float(data.get("dy", 0.0))
            return {"found": found, "dx": dx, "dy": dy}
    except FileNotFoundError:
        # Se o arquivo não existir, retorna como se não tivesse encontrado
        return {"found": False, "dx": 0.0, "dy": 0.0}
    except Exception as e:
        # Se houver outro erro (JSON mal formatado, etc.), avisa e retorna não encontrado
        print(f"[ler_arquivo_alvo] Erro ao ler o arquivo: {e}")
        return {"found": False, "dx": 0.0, "dy": 0.0}


def centralizacao(Uno, tentativas_max=10, px_to_m=PIXEL_TO_METER, threshold_m=CENTER_THRESHOLD_M, step_speed=0.4, step_time=1.0):

    print("Tentando centralizar sobre o alvo...")
    tentativas = 0
    while tentativas < tentativas_max :
        # Lê a posição do alvo no arquivo
        t = ler_arquivo_alvo()
        if not t["found"]:
            print("Alvo não encontrado durante a centralização.")
            return False
        
        dx_px = t["dx"]; dy_px = t["dy"]
        dx_m = dx_px * px_to_m; dy_m = dy_px * px_to_m
        print(f"Leitura Visão: dx_px={dx_px:.1f}, dy_px={dy_px:.1f} -> dx_m={dx_m:.3f}, dy_m={dy_m:.3f}")
        
        need_right = abs(dx_m) > threshold_m
        need_forward = abs(dy_m) > threshold_m
        if not need_right and not need_forward:
            print("Centralizado dentro do threshold.")
            return True
        
        vx = 0.0; vy = 0.0
        if need_forward: vx = step_speed if dy_m > 0 else -step_speed
        if need_right:   vy = step_speed if dx_m > 0 else -step_speed

        print(f"Enviando correção: vx={vx:.2f}, vy={vy:.2f} por {step_time}s")
        movimentacao_velocidade(Uno, vx, vy, 0, step_time)
        tentativas += 1

    print("Falhou em centralizar após tentativas.")
    return False


def pousar_no_alvo_e_desarmar(Uno, timeout=60):
    
    print("Iniciando pouso no local atual (Modo LAND)...")
    Uno.mode = VehicleMode("LAND")
    
    inicio = time.time()
    while Uno.armed: # O ArduPilot desarma automaticamente ao pousar no modo LAND
        if time.time() - inicio > timeout:
            raise RuntimeError("Timeout! Drone não pousou ou desarmou no modo LAND.")
        
        alt_atual = Uno.location.global_relative_frame.alt
        print(f"Aguardando pouso e desarme... Altitude atual: {alt_atual:.2f}m")
        time.sleep(1)
    
    print("Pouso concluído. Motores desarmados.")


def return_to_launch(Uno, altitude_retorno_m=0):
    
    altitude_retorno_cm = int(altitude_retorno_m * 100)
    
    print(f"Definindo parâmetro RTL_ALT para {altitude_retorno_cm} cm...")
    try:
        Uno.parameters['RTL_ALT'] = altitude_retorno_cm
        print("Parâmetro RTL_ALT atualizado.")
        time.sleep(0.5) # Pausa para garantir envio
    except Exception as e:
        print(f"Aviso: Não foi possível definir RTL_ALT: {e}. Usando o padrão do drone.")

    print("Ativando modo RTL...")
    Uno.mode = VehicleMode("RTL")
    print("Aguardando drone pousar e desarmar...")
    time.sleep(2) 

    while Uno.armed:
        alt_atual = Uno.location.global_relative_frame.alt
        print(f"Retornando... Altitude atual: {alt_atual:.1f} m")
        time.sleep(1)

    print("RTL concluído. Drone pousou e desarmou.")


def desarmar_uno(Uno, timeout=10):
    
    print("Desarmando Uno...")
    Uno.armed = False
    inicio = time.time()
    while Uno.armed:
        if time.time() - inicio > timeout:
            print("[desarmar_uno] Timeout ao desarmar.")
            return False
        time.sleep(0.5)
    print("Uno desarmado.")
    return True
