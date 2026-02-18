# Documentação do Sistema de Gravação NVR

Sistema automatizado para captura e upload de gravações de NVR JFTech.

## Estrutura do Projeto

```
app/
├── config.py                 # Configurações (Redis, NVR, APIs)
├── producer_service.py       # Serviço que detecta eventos GPIO
├── download_service.py       # Serviço que baixa vídeos do NVR
├── upload_service.py         # Serviço que faz upload para API externa
├── video_processor.py        # Processamento de vídeo (opcional)
├── services/                 # Serviços auxiliares
│   └── jftecth_integration.py   # Integração com SDK JFTech
├── lib/                      # Bibliotecas externas
│   └── XCloudSDK-v1.0.0-Linux-x86_64/  # SDK JFTech
├── tests/                    # Testes automatizados
│   ├── test_validation.py       # Validação de estrutura
│   ├── test_mock_simple.py      # Testes simples com mocks
│   └── test_services.py         # Testes unitários completos
└── docs/                     # Documentação
    ├── README.md                # Este arquivo
    └── TESTES_README.md         # Guia de testes
```

## Componentes Principais

### 1. Producer Service (producer_service.py)
- Monitora botões GPIO no Raspberry Pi
- Detecta eventos de pressionamento
- Captura timestamp e canal
- Enfileira tarefa de download no Redis

**Configuração:**
- `BUTTON_PIN_1`: GPIO 17 → Canal 1
- `BUTTON_PIN_2`: GPIO 18 → Canal 2

### 2. Download Service (download_service.py)
- Processa fila de downloads
- Recebe timestamp e canal
- Executa integração com SDK JFTech
- Baixa vídeo do NVR
- Enfileira para upload

**Parâmetros:**
- `timestamp`: Data/hora formato "YYYY-MM-DD HH:MM:SS"
- `channel`: Número do canal (0-63)

### 3. JFTech Integration (services/jftecth_integration.py)
- Wrapper Python para XCloudSDK
- Login no NVR via IP
- Busca de gravações
- Download de vídeo
- Retorna caminho do arquivo baixado

**Funcionalidades:**
- Busca gravações 15 segundos antes do timestamp
- Salva em formato MP4
- Nomenclatura: `nvr01_stream{CHANNEL}_{TIMESTAMP}.mp4`

### 4. Upload Service (upload_service.py)
- Processa fila de uploads
- Envia vídeo para API externa
- Remove arquivo local após sucesso

### 5. Video Processor (video_processor.py)
- Processamento opcional de vídeo
- Placeholder para futuras funcionalidades
- Ex: compressão, conversão, análise

## Fluxo de Trabalho

```
1. GPIO Trigger
   ↓
2. Producer Service
   • Captura timestamp
   • Enfileira download
   ↓
3. Worker processa fila
   ↓
4. Download Service
   • Chama JFTech Integration
   • Baixa vídeo do NVR
   ↓
5. Video Processor
   • Processamento opcional
   ↓
6. Enfileira upload
   ↓
7. Worker processa upload
   ↓
8. Upload Service
   • Envia para API
   • Remove arquivo local
```

## Configuração

### Variáveis de Ambiente (.env)

```bash
# NVR JFTech
NVR_IP=192.168.0.168
NVR_PORT=34567
NVR_USERNAME=service
NVR_PASSWORD=sua_senha

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# APIs
API_UPLOAD_URL=https://api.externa.com/upload
```

### Configuração (config.py)

```python
REDIS_HOST = "localhost"
REDIS_PORT = 6379
DOWNLOAD_QUEUE = "download_queue"
UPLOAD_QUEUE = "upload_queue"
VIDEO_STORAGE_PATH = "/home/pi/videos/"
```

## Execução

### Iniciar Producer (Raspberry Pi)

```bash
python3 producer_service.py
```

### Iniciar Workers (RQ)

```bash
# Worker para downloads
rq worker download_queue

# Worker para uploads
rq worker upload_queue
```

### Teste Manual

```python
from download_service import download_video

# Download com timestamp específico
download_video(timestamp='2026-02-18 14:30:00', channel=1)

# Download com hora atual
download_video(channel=1)
```

## Testes

Veja [TESTES_README.md](TESTES_README.md) para guia completo de testes.

Quick start:

```bash
cd /home/abauruel/www/onvif_learn/RE/app

# Validação completa
python3 tests/test_validation.py

# Testes com mocks
python3 tests/test_mock_simple.py
```

## Dependências

```bash
pip3 install -r requirements.txt
```

**Principais:**
- redis
- rq (Redis Queue)
- requests
- python-dotenv
- RPi.GPIO (apenas Raspberry Pi)

## Troubleshooting

### Erro: No module named 'redis'
```bash
pip3 install redis rq
```

### Erro: No module named 'RPi'
Normal em ambiente de desenvolvimento. Use mocks para testes.

### NVR não conecta
- Verifique IP e porta do NVR
- Confirme credenciais (username/password)
- Teste ping: `ping {NVR_IP}`

### Vídeo não baixa
- Verifique se há gravação no período (15s antes do timestamp)
- Confirme que o canal está ativo
- Verifique logs do SDK em `logs/`

## Logs

SDK JFTech salva logs em:
- `logs/XCloudSDK.log` - Log principal
- Console - Saída de debug

## Diretórios

- **videos/**: Vídeos baixados (temporários)
- **logs/**: Logs do SDK e aplicação
- **tests/**: Testes automatizados
- **docs/**: Documentação

## Segurança

- Não commite o arquivo `.env` com credenciais
- Use variáveis de ambiente para senhas
- Configure permissões adequadas em `/home/pi/videos/`

## Monitoramento

### Redis Queue Dashboard

```bash
rq info
```

### Verificar filas

```python
import redis
from rq import Queue

r = redis.Redis()
download_q = Queue('download_queue', connection=r)
upload_q = Queue('upload_queue', connection=r)

print(f"Downloads pendentes: {len(download_q)}")
print(f"Uploads pendentes: {len(upload_q)}")
```

## Manutenção

### Limpar vídeos antigos

```bash
find videos/ -name "*.mp4" -mtime +7 -delete
```

### Limpar logs antigos

```bash
find logs/ -name "*.log" -mtime +30 -delete
```

## Desenvolvido com

- Python 3.x
- XCloudSDK JFTech v1.0.0
- Redis Queue (RQ)
- Raspberry Pi GPIO

## Licença

Uso interno.
