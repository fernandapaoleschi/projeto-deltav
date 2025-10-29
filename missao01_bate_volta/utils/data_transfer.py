from threading import Lock

DATA_FILE_PATH = "alvo_data.json"
_file_lock = Lock()

def escrever_dados_alvo(data: dict):
    """
    Escreve os dados do alvo em um arquivo JSON de forma segura (thread-safe).
    """
    with _file_lock:
        try:
            with open(DATA_FILE_PATH, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"[ERRO DataTransfer] Falha ao escrever no arquivo: {e}")
