# missao_principal5
# Implementado máquina de estados

import funcoes_controle5
import time

ALTITUDE_DE_BUSCA = 3.0
PASSO_DA_VARREDURA = 1.0   
VEL_LATERAL = 1.0          
VEL_FRENTE = 1.0           

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


def main():
    
    print("INICIANDO MISSÃO")
    
    Uno = None
    estado_atual = ESTADO_INICIANDO
    ultima_excecao = None            

    while estado_atual != ESTADO_FINALIZADO: 

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

            elif estado_atual == ESTADO_BUSCANDO:
                print(f"[ESTADO] {estado_atual}: Iniciando varredura da arena...")
                sucesso_busca = funcoes_controle5.varredura_arena(Uno, 
                                                                 passo_frente=PASSO_DA_VARREDURA, 
                                                                 velocidade_lateral=VEL_LATERAL, 
                                                                 velocidade_frente=VEL_FRENTE)
                
                # Transição condicional
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
                
                # Transição condicional
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
                # Transição
                estado_atual = ESTADO_RE_ARMANDO
                
            elif estado_atual == ESTADO_RE_ARMANDO:
                print(f"[ESTADO] {estado_atual}: Re-armando o drone para subida...")
                funcoes_controle5.armar_uno(Uno)
                print("Re-armado.")
                # Transição
                estado_atual = ESTADO_RE_DECOLANDO

            elif estado_atual == ESTADO_RE_DECOLANDO:
                print(f"[ESTADO] {estado_atual}: Subindo de volta para {ALTITUDE_DE_BUSCA}m...")
                funcoes_controle5.decolar_uno(Uno, ALTITUDE_DE_BUSCA)
                print("Altitude de segurança para RTL atingida.")
                # Transição
                estado_atual = ESTADO_RETORNANDO_RTL
                
            elif estado_atual == ESTADO_RETORNANDO_RTL:
                # Estado terminal "seguro"
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
                        if Uno.armed:
                            funcoes_controle5.return_to_launch(Uno, altitude_retorno_m=0)
                            print("Pouso de emergência (RTL) concluído.")
                        else:
                            print("Drone estava desarmado no momento da falha. Não é possível RTL.")
                    except Exception as rtl_err:
                        print(f"Falha ao tentar RTL de emergência: {rtl_err}")
                else:
                    print("Sem conexão com o drone. Impossível executar RTL.")
                
        
                estado_atual = ESTADO_FINALIZADO

        except Exception as e:
            print(f"\n!!! ERRO CRÍTICO NA MISSÃO (Estado: {estado_atual}): {e} !!!")
            ultima_excecao = e
    
            estado_atual = ESTADO_FALHA_CRITICA

    print("\n--- MISSÃO FINALIZADA ---")

if __name__ == "__main__":
    main()
    
