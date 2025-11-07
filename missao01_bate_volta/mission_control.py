import time
from dronekit import Vehicle
from threading import Event
from control import funcoes_controle
from config import control_config as c_settings

class MissionManager:
    """
    Gerencia a execução da máquina de estados da missão do drone.
    """
    def __init__(self, vehicle: Vehicle, stop_event: Event):
        self.Uno = vehicle
        self.stop_vision_event = stop_event
        self.estado_atual = c_settings.ESTADO_INICIANDO
        self.ultima_excecao = None
        print("[SISTEMA] MissionManager inicializado.")

    def run_state_machine(self):
        """
        Inicia o loop principal da máquina de estados.
        """
        print("[SISTEMA] Iniciando Máquina de Estados de Controle.")
        
        while self.estado_atual != c_settings.ESTADO_FINALIZADO and not self.stop_vision_event.is_set():
            try:
                self._process_current_state()
            except Exception as e:
                print(f"\n!!! ERRO CRÍTICO NA MISSÃO (Estado: {self.estado_atual}): {e} !!!")
                self.ultima_excecao = e
                self.estado_atual = c_settings.ESTADO_FALHA_CRITICA
        
        print("[SISTEMA] Máquina de Estados de Controle finalizada.")

    def _process_current_state(self):
        """
       lógica de transição de estados.
        """
        
        if self.estado_atual == c_settings.ESTADO_INICIANDO:
            print(f"[ESTADO] {self.estado_atual}: Conexão com o drone já estabelecida.")
            # A conexão agora é feita no main.py, antes de chamar esta classe.
            time.sleep(1)
            self.estado_atual = c_settings.ESTADO_ARMANDO

        elif self.estado_atual == c_settings.ESTADO_ARMANDO:
            print(f"[ESTADO] {self.estado_atual}: Armando o drone...")
            funcoes_controle.armar_uno(self.Uno)
            print("Uno armado pronto para decolagem.")
            time.sleep(1)
            self.estado_atual = c_settings.ESTADO_DECOLANDO
        
        elif self.estado_atual == c_settings.ESTADO_DECOLANDO:
            print(f"[ESTADO] {self.estado_atual}: Subindo para {c_settings.ALTITUDE_DE_BUSCA}m...")
            funcoes_controle.decolar_uno(self.Uno, c_settings.ALTITUDE_DE_BUSCA)
            print("Altitude de busca atingida.")
            self.estado_atual = c_settings.ESTADO_BUSCANDO

        elif self.estado_atual == c_settings.ESTADO_BUSCANDO:
            print(f"[ESTADO] {self.estado_atual}: Iniciando varredura da arena...")
            sucesso_busca = funcoes_controle.varredura_arena(self.Uno,  passo_frente=c_settings.PASSO_DA_VARREDURA, velocidade_lateral=c_settings.VEL_LATERAL,  velocidade_frente=c_settings.VEL_FRENTE)
            if sucesso_busca:
                print("Alvo identificado! Próximo estado: CENTRALIZANDO.")
                self.estado_atual = c_settings.ESTADO_CENTRALIZANDO
            #else
                #print("Alvo não encontrado. Próximo estado: RETORNANDO_RTL.")
                #self.estado_atual = c_settings.ESTADO_RETORNANDO_RTL

        elif self.estado_atual == c_settings.ESTADO_CENTRALIZANDO:
            print(f"[ESTADO] {self.estado_atual}: Iniciando centralização...")
            time.sleep(1)
            sucesso_centralizacao = funcoes_controle.centralizacao(self.Uno)
            print("AQUI")
            if sucesso_centralizacao:
                print("Centralização concluída. Próximo estado: POUSANDO_ALVO.")
                self.estado_atual = c_settings.ESTADO_POUSANDO_ALVO
            #else:
                #print("Falha ao centralizar. Próximo estado: RETORNANDO_RTL.")
                # self.estado_atual = c_settings.ESTADO_RETORNANDO_RTL

        elif self.estado_atual == c_settings.ESTADO_POUSANDO_ALVO:
            print(f"[ESTADO] {self.estado_atual}: Iniciando pouso sobre o alvo.")
            funcoes_controle.pousar_no_alvo_e_desarmar(self.Uno)
            print("Pouso sobre alvo concluído.")
            self.estado_atual = c_settings.ESTADO_RE_ARMANDO
            
        elif self.estado_atual == c_settings.ESTADO_RE_ARMANDO:
            print(f"[ESTADO] {self.estado_atual}: Re-armando o drone para subida...")
            funcoes_controle.armar_uno(self.Uno)
            print("Re-armado.")
            self.estado_atual = c_settings.ESTADO_RE_DECOLANDO

        elif self.estado_atual == c_settings.ESTADO_RE_DECOLANDO:
            print(f"[ESTADO] {self.estado_atual}: Subindo de volta para {c_settings.ALTITUDE_DE_BUSCA}m...")
            funcoes_controle.decolar_uno(self.Uno, c_settings.ALTITUDE_DE_BUSCA)
            print("Altitude de segurança para RTL atingida.")
            self.estado_atual = c_settings.ESTADO_RETORNANDO_RTL
            
        elif self.estado_atual == c_settings.ESTADO_RETORNANDO_RTL:
            print(f"[ESTADO] {self.estado_atual}: Fase final.")
            if self.Uno and self.Uno.armed:
                print("[MISSÃO] Ativando RTL...")
                funcoes_controle.return_to_launch(self.Uno, altitude_retorno_m=0)
                print("[MISSÃO] Pouso e desarme na base concluídos.")
            elif self.Uno and not self.Uno.armed:
                print("[MISSÃO] Drone já está no chão. Missão concluída sem RTL.")
            else:
                print("[MISSÃO] Estado inesperado ou sem conexão. Não é possível RTL.")
            self.estado_atual = c_settings.ESTADO_FINALIZADO
            
        elif self.estado_atual == c_settings.ESTADO_FALHA_CRITICA:
            print(f"[ESTADO] {self.estado_atual}: Tratando erro: {self.ultima_excecao}")
            if self.Uno:
                print("Tentando RTL de emergência...")
                try:
                    if self.Uno.armed: funcoes_controle.return_to_launch(self.Uno, altitude_retorno_m=0)
                    else: print("Drone estava desarmado.")
                except Exception as rtl_err: print(f"Falha ao tentar RTL de emergência: {rtl_err}")
            else: print("Sem conexão com o drone. Impossível executar RTL.")
            self.estado_atual = c_settings.ESTADO_FINALIZADO