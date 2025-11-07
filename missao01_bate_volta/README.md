# Competição Microquad Delta V - Missão 01: Bate-Volta

Este repositório contém o código-fonte para a "Missão 01: Bate-Volta" do Projeto Delta V. O projeto implementa um sistema de voo autônomo para um drone, utilizando visão computacional e uma máquina de estados para executar uma sequência completa de tarefas.

## 🎯 Visão Geral da Missão

A missão simula uma tarefa de reconhecimento por um VANT (Veículo Aéreo Não Tripulado). O drone deve demonstrar capacidade de navegação autônoma, processamento de imagem para identificação de alvos e precisão na manobra sobre um local específico.

**O Cenário:**
A arena de competição consiste em uma área plana de 10 x 10 metros. Nela, estão dispostas diversas plataformas brancas, quadradas (80 cm de largura), cada uma contendo uma figura geométrica distinta (cruz, estrela, pentágono, etc.). O drone iniciará a missão a partir de uma base circular azul (80 cm de diâmetro), localizada no canto da arena. A figura-alvo específica é informada pela organização com 24 horas de antecedência.

**Objetivos do Desafio:**
O fluxo da missão consiste em:
1.  **Decolar** autonomamente da base azul.
2.  **Navegar** pela arena para localizar a plataforma que contém a figura-alvo pré-determinada.
3.  **Identificar** corretamente a figura-alvo usando visão computacional.
4.  **Executar a Entrega:** Sobrevoar a plataforma-alvo e realizar um **pouso de precisão sobre o alvo, seguido de um rearme**.
5.  **Retornar** à base de decolagem original.
6.  **Pousar** com segurança dentro dos limites da base circular azul.

## 🧭 Principais Características

* **Multithreading:** A lógica de controle do drone (Máquina de Estados) roda na *thread* principal, enquanto o processamento de visão computacional (OpenCV) roda em uma *thread* paralela, garantindo que a detecção de imagens não bloqueie o controle de voo.
* **Máquina de Estados (FSM):** A lógica da missão é gerenciada por uma Máquina de Estados finita, tornando o código robusto, fácil de depurar e de escalar para novas etapas.
* **Visão Computacional:** Utiliza OpenCV para detectar, rastrear e calcular a posição relativa do drone em relação ao alvo (erros `dx`, `dy` e distância `z`).
* **Arquitetura Limpa:** O código é dividido em três camadas principais:
    1.  `main.py` (Orquestração e Gerenciamento de Falhas)
    2.  `mission_control.py` (Lógica de Estados da Missão)
    3.  `vision_manager.py` (Lógica da Thread de Visão)
* **Configurável:** Parâmetros de voo, missão e câmera são facilmente ajustáveis através de arquivos de configuração.

## 🛠️ Setup do Ambiente (Linux/WSL)

Este projeto requer um ambiente de simulação específico (SITL + Webots) rodando em Linux ou WSL.

**1. Versão do Python (Crítico)**
Este projeto **requer Python 3.8, 3.9 ou 3.10**. Versões mais recentes (3.11+) podem ter problemas de compatibilidade com as bibliotecas de simulação (Webots, OpenCV ou ArduPilot).

**2. Instalação de Software (Sistema)**
Você precisará instalar as seguintes ferramentas no seu sistema Linux/WSL:

* **Webots:** Faça o download e instale o simulador Webots para Linux a partir do [site oficial](https://cyberbotics.com/).
* **mediamtx:** Este é um servidor de streaming. Siga as instruções de instalação do [repositório do mediamtx](https://github.com/bluenviron/mediamtx).
* **ArduPilot (Fonte):** Você precisará ter o código-fonte do ArduPilot, pois ele será usado para iniciar o SITL. Siga o [guia de setup do ArduPilot](https://ardupilot.org/dev/docs/building-setup-linux.html) se ainda não o tiver.

**3. Ambiente Virtual e Dependências Python**
É **altamente recomendado** usar um ambiente virtual.

```bash
# Crie o ambiente virtual (ex: venv-ardupilot)
# Use o python da versão correta (ex: python3.10)
python3.10 -m venv $HOME/venv/venv-ardupilot

# Ative o ambiente
source $HOME/venv/venv-ardupilot/bin/activate

# Clone o repositório (se ainda não o fez)
git clone [https://github.com/fernandapaoleschi/projeto-deltav.git](https://github.com/fernandapaoleschi/projeto-deltav.git)
cd projeto-deltav/missao01_bate_volta

# Instale as dependências do Python
pip install -r requirements.txt
```
---

## 🚀 Executando a Simulação (Sequência de Lançamento)

Para executar a missão, você precisará iniciar 4 processos em ordem, **em terminais separados**.



**Terminal 1: Iniciar o `mediamtx`**

Abra um **novo** terminal e inicie o servidor de streaming `mediamtx`.
```bash
# O comando exato pode variar dependendo de como foi instalado
mediamtx
```
**Terminal 2: Iniciar o ArduPilot SITL (Software-in-the-Loop)**

Abra um segundo terminal. Navegue até o diretório do ArduPilot e inicie o SITL, apontando para o Webots e os parâmetros da simulação.
```bash
# Navegue até a pasta do ArduPilot
cd /caminho/para/seu/ardupilot

# Execute o sim_vehicle.py
# SUBSTITUA o caminho do --add-param-file pelo seu caminho absoluto
./Tools/autotest/sim_vehicle.py -v ArduCopter --model webots-python --add-param-file=/home/pasta/ardupilot/Webots-PS/params/drone.parm -w --out="127.0.0.1:14550"
```
**Terminal 3: Iniciar o Webots**
Abra um terceiro terminal e inicie a interface gráfica do Webots.
```bash
webots
```
**Terminal 4: Executar o Script da Missão**
```bash
# Navegue até a pasta do projeto
cd /caminho/para/projeto-deltav/missao01_bate_volta

# Ative o ambiente virtual
source $HOME/venv/venv-ardupilot/bin/activate

# Execute o script principal da missão
python main.py
```

