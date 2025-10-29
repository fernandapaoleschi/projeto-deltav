#test_detecction.py

from control import funcoes_controle5
import time

ALTITUDE_DE_BUSCA = 3.0
PASSO_DA_VARREDURA = 1.0   # Distância (m) entre as "pernas" da varredura em S
VEL_LATERAL = 1.0          
VEL_FRENTE = 1.0           

def main():
    
    print("INICIANDO MISSÃO)")
    
    Uno = None
    
    try:
        
        Uno = funcoes_controle5.conectar_uno()
        print("Conexão com o Uno estabelecida.")
        time.sleep(1) 

        funcoes_controle5.armar_uno(Uno)
        print("Uno armado pronto para decolagem.")
        time.sleep(1)

        print(f"Decolando para {ALTITUDE_DE_BUSCA}m...")
        funcoes_controle5.decolar_uno(Uno, ALTITUDE_DE_BUSCA)
        print(f"Altitude de busca atingida.")
        
        
        print(f"Iniciando varredura da arena...")
      
        sucesso_busca = funcoes_controle5.varredura_arena(Uno, 
                                                         passo_frente=PASSO_DA_VARREDURA, 
                                                         velocidade_lateral=VEL_LATERAL, 
                                                         velocidade_frente=VEL_FRENTE)
        
        
        if sucesso_busca:
            print("Alvo identificado! Iniciando centralização.")
            time.sleep(1)
            
            sucesso_centralizacao = funcoes_controle5.centralizacao(Uno)
            
            if sucesso_centralizacao:
                print("Centralização concluída. Iniciando pouso sobre o alvo.")
            
                funcoes_controle5.pousar_no_alvo_e_desarmar(Uno)
                print(f"Pouso sobre alvo concluído.")
                
                print(f"Re-armando o drone para decolagem...")
                funcoes_controle5.armar_uno(Uno)
            
                print(f"[MISSÃO] Subindo de volta para {ALTITUDE_DE_BUSCA}m para o RTL...")
                funcoes_controle5.decolar_uno(Uno, ALTITUDE_DE_BUSCA)
                print("Altitude de segurança para RTL atingida.")
                
                
            else:
                print("[MISSÃO] Falha ao centralizar no alvo. Abortando pouso.")
        
        else:
            print("[MISSÃO] Alvo não encontrado após varredura completa.")

    except Exception as e:
        print(f"\n!!! ERRO CRÍTICO NA MISSÃO: {e} !!!")
        print("Uma exceção ocorreu. Tentando ativar RTL por segurança...")

    finally:
        # --- FASE 4: FINALIZAÇÃO (SEMPRE EXECUTA) ---
        
        print("\n[MISSÃO] Fase final: Retornando para base.")
        
        # Verifica se a conexão foi estabelecida
        if Uno:
            # Verifica se o drone ainda está no ar (armado)
            if Uno.armed:
                print("[MISSÃO] Ativando RTL...")
                # Chama o RTL com altitude_retorno_m=0 (retorna na altitude atual, que deve ser 3m)
                funcoes_controle5.return_to_launch(Uno, altitude_retorno_m=0)
                print("[MISSÃO] Pouso e desarme na base concluídos.")
            # Se ele já pousou no alvo e não conseguiu rearmar/redecolar
            elif not Uno.armed and Uno.location.global_relative_frame.alt < 0.1:
                 print("[MISSÃO] Drone já está no chão após pouso no alvo. Missão concluída sem RTL.")
            # Situação inesperada: desarmado mas ainda no ar? Tenta RTL mesmo assim.
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
            # Se a conexão inicial falhou
            print("[MISSÃO] Conexão com o drone nunca foi estabelecida. Finalizando script.")
            
        print("--- MISSÃO FINALIZADA ---")

# Ponto de entrada do script: Chama a função main() quando o arquivo é executado
if __name__ == "__main__":
    main()
