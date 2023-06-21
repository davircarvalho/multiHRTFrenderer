# multiHRTFrenderer

## Setup

```
pip install -r requirements.txt

```

Baixe o app para Android **OSC_btn**. Nele você pode carregar o template HRTFdatasetOSCsender.xml
Com template permite que você se comunique com a máquina de auralização e alterar entre os perfis de HRTF .sofa carregados.

- NOTE: para o OSC_btn funcionar, tanto o dispositivo android quanto o computador precisam estar conectados na mesma rede de internet


# Uso

Rode o arquivo ```renderer.py```, que funciona de forma interativa.


Na celula *Global configs* edite o caminho para os arquivos .sofa e para o audio a ser reproduzido.


# Hotkeys

Como alternativa para utilizar o app, os comandos de troca de dataset e salvar posicao atual do headtracker pode ser ativadas por meio de comandos no teclado:

- **Espaco**: salvar posicao atual
- **AltGr** + **0**: selecionar dataset 0 
- **AltGr** + **1**: selecionar dataset 1
- **AltGr** + **2**: selecionar dataset 2 
- **AltGr** + **3**: selecionar dataset 3 
- **AltGr** + **4**: selecionar dataset 4 


