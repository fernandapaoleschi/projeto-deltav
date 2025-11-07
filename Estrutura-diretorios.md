missao01_bate_volta/
├── config/
│   ├── __init__.py         # Inicialização do módulo de configuração
│   ├── control_config.py   # Parâmetros de controle e PID
│   ├── mission_config.py   # Estados da missão 
│   └── vision_config.py    # Configurações da câmera e visão computacional
│
├── control/
│   └── funcoes_controle.py # Funções de controle de voo
│
├── core/
│   ├── shape_data.py       # Estrutura de dados de forma detectada
│   └── shape_manager.py    # Coordenação entre detecção e classificação
│
├── detectors/
│   ├── base_detector.py    # Classe base para detectores
│   ├── casa_detector.py    # Detector da figura "Casa"
│   ├── circle_detector.py  # Detector de Círculo (circularidade)
│   ├── cruz_detector.py      # Detector de Cruz (solidez e vértices)
│   ├── estrela_detector.py # Detector de Estrela (ângulos e pontas agudas)
│   ├── hexagono_detector.py# Detector de Hexágono (6 vértices)
│   ├── pentagono_detector.py# Detector de Pentágono (5 vértices, assinatura não-casa)
│   └── triangle_detector.py# Detector de Triângulo (3 vértices)
│
├── utils/
│   ├── __init__.py
│   ├── camera_sim.py       # Simulação de câmera RTSP
│   ├── centralization.py   # Cálculo de centralização do alvo (dx, dy)
│   ├── conversions.py      # Conversões de unidades
│   ├── data_transfer.py    # Comunicação JSON entre visão e controle
│   ├── distance_calculate.py# Estimativa de distância ao alvo
│   ├── geometry.py         # Funções geométricas auxiliares
│
├── main.py                 # Ponto de entrada da aplicação
├── mission_control.py      # Máquina de estados e lógica da missão
└── vision_manager.py       # Thread de visão (captura, detecção e saída JSON)
