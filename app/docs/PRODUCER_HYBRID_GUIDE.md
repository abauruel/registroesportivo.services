# Producer Service - Modo Híbrido (GPIO + API REST)

## 📋 Visão Geral

O Producer Service agora funciona em **modo híbrido**, aceitando eventos de trigger através de:
1. **Hardware GPIO** - Botões físicos conectados aos pinos GPIO 17 e 18
2. **API REST** - Endpoints HTTP para disparar eventos remotamente

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────┐
│      PRODUCER SERVICE (Híbrido)         │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────┐          ┌─────────┐     │
│  │   GPIO   │          │   API   │     │
│  │ Pino 17  │          │  Flask  │     │
│  │ Pino 18  │          │ :5000   │     │
│  └────┬─────┘          └────┬────┘     │
│       │                     │          │
│       └──────┬──────────────┘          │
│              │                         │
│      ┌───────▼────────┐                │
│      │  trigger_event │                │
│      └───────┬────────┘                │
│              │                         │
│       ┌──────▼───────┐                 │
│       │ Redis Queue  │                 │
│       └──────────────┘                 │
└─────────────────────────────────────────┘
              │
              ▼
       [Download Worker]
```

## 📁 Arquivos Criados

### 1. `services/producer_routes.py`
Arquivo com todas as rotas da API REST:
- `/health` - Health check
- `/trigger` - Trigger via JSON
- `/trigger/<channel>` - Trigger via URL
- `/status/<job_id>` - Consultar status do job

### 2. `services/producer_service.py` (modificado)
Arquivo principal que roda em modo híbrido:
- Thread 1: Monitoramento GPIO (pinos 17 e 18)
- Thread 2: Servidor Flask (porta 5000)

### 3. `docs/API_ROUTES.md`
Documentação completa da API REST

### 4. `test_api_producer.py`
Script de testes automatizados da API

## 🚀 Como Usar

### Instalação
```bash
# Instalar dependências (Flask foi adicionado)
cd /home/abauruel/www/onvif_learn/RE
.venv/bin/pip install -r requirements.txt
```

### Opção 1: Modo Híbrido (GPIO + API)
Executa ambos os modos simultaneamente:

```bash
cd /home/abauruel/www/onvif_learn/RE/app
python services/producer_service.py
```

**Terminal mostrará:**
```
======================================================================
🚀 PRODUCER SERVICE - Modo Híbrido (GPIO + API REST)
======================================================================
✅ GPIO configurado com sucesso
   Pin 17 → Canal 1
   Pin 18 → Canal 2

🌐 Iniciando API REST em 0.0.0.0:5000
   Endpoints disponíveis:
   GET  /health
   POST /trigger
   POST /trigger/<channel>
   GET  /status/<job_id>

======================================================================
✅ Producer iniciado com sucesso!
======================================================================
📍 GPIO: Monitorando eventos nos pinos 17 e 18
🌐 API: Escutando em http://0.0.0.0:5000

💡 Exemplos de uso da API:
   curl http://localhost:5000/health
   curl -X POST http://localhost:5000/trigger/1
   curl -X POST http://localhost:5000/trigger -H 'Content-Type: application/json' -d '{"channel": 2}'

Pressione Ctrl+C para parar
```

### Opção 2: Somente API (sem GPIO)
Se você não tem hardware GPIO ou quer rodar apenas a API:

```bash
cd /home/abauruel/www/onvif_learn/RE/app
python services/producer_routes.py
```

## 🌐 Usando a API REST

### Health Check
```bash
curl http://localhost:5000/health
```

**Resposta:**
```json
{
  "status": "ok",
  "service": "producer_service",
  "redis_connected": true
}
```

### Trigger Simples (canal via URL)
```bash
# Dispara evento no canal 1 com timestamp atual
curl -X POST http://localhost:5000/trigger/1
```

**Resposta:**
```json
{
  "status": "success",
  "message": "Evento enfileirado para canal 1",
  "channel": 1,
  "timestamp": "2026-02-18 16:30:45",
  "job_id": "abc123-def456-..."
}
```

### Trigger com Timestamp Específico (via JSON)
```bash
curl -X POST http://localhost:5000/trigger \
  -H "Content-Type: application/json" \
  -d '{
    "channel": 2,
    "timestamp": "2026-02-18 16:00:00"
  }'
```

### Trigger com Query String
```bash
curl -X POST "http://localhost:5000/trigger/3?timestamp=2026-02-18%2017:30:00"
```

### Consultar Status do Job
```bash
curl http://localhost:5000/status/abc123-def456-...
```

**Resposta:**
```json
{
  "job_id": "abc123-def456-...",
  "status": "finished",
  "created_at": "2026-02-18T16:00:00",
  "started_at": "2026-02-18T16:00:01",
  "ended_at": "2026-02-18T16:00:30",
  "result": null
}
```

## 🧪 Testando a API

### Teste Automatizado
Execute o script de testes:

```bash
# Em um terminal, inicie o producer
cd /home/abauruel/www/onvif_learn/RE/app
python services/producer_service.py

# Em outro terminal, execute os testes
cd /home/abauruel/www/onvif_learn/RE/app
../.venv/bin/python test_api_producer.py
```

O script testará:
- ✅ Health check
- ✅ Trigger simples
- ✅ Trigger com timestamp
- ✅ Trigger com query string
- ✅ Consulta de status do job
- ✅ Validações de erro

### Teste Manual com Python
```python
import requests

# Trigger evento
response = requests.post('http://localhost:5000/trigger', json={
    'channel': 1,
    'timestamp': '2026-02-18 16:00:00'
})

result = response.json()
print(f"Job ID: {result['job_id']}")

# Verificar status
job_id = result['job_id']
status = requests.get(f'http://localhost:5000/status/{job_id}')
print(status.json())
```

## 🔧 GPIO (Hardware)

### Conexões
- **GPIO 17** → Botão para Canal 1
- **GPIO 18** → Botão para Canal 2

### Comportamento
Quando um botão é pressionado:
1. GPIO detecta evento (FALLING edge)
2. Timestamp atual é capturado
3. Evento é enfileirado no Redis
4. Mensagem é exibida no console

**Exemplo de saída:**
```
============================================================
📥 Evento GPIO detectado - Canal 1
============================================================
  Timestamp: 2026-02-18 16:30:45
  Canal: 1
  Job ID: abc123-def456-...
  Status: queued
============================================================
```

## 📊 Validações

### Canal
- ✅ Deve ser inteiro entre 0 e 63
- ❌ Valores inválidos retornam erro 400

### Timestamp
- ✅ Formato: `YYYY-MM-DD HH:MM:SS`
- ✅ Opcional (usa timestamp atual se omitido)
- ❌ Formato inválido retorna erro 400

## 🔄 Fluxo Completo

### Via GPIO:
```
Botão pressionado → GPIO detecta → trigger_event() → Redis Queue → Worker processa
```

### Via API:
```
HTTP POST → Flask endpoint → trigger_event_api() → Redis Queue → Worker processa
```

## 🛠️ Troubleshooting

### GPIO não disponível
Se você vir: `⚠️  RPi.GPIO não disponível - rodando em modo somente API`

**Solução:** Normal! O sistema automaticamente desabilita GPIO e roda apenas API. Use a API REST para disparar eventos.

### Flask não instalado
```bash
cd /home/abauruel/www/onvif_learn/RE
.venv/bin/pip install Flask
```

### Redis não conecta
```bash
# Verificar se Redis está rodando
podman ps | grep redis

# Se não estiver, iniciar:
podman start redis
```

## 📝 Próximos Passos

Para usar o sistema completo:

1. **Iniciar Redis** (se não estiver rodando)
   ```bash
   podman start redis
   ```

2. **Iniciar Worker** (processa downloads)
   ```bash
   cd /home/abauruel/www/onvif_learn/RE/app
   rq worker download_queue
   ```

3. **Iniciar Producer** (este serviço)
   ```bash
   cd /home/abauruel/www/onvif_learn/RE/app
   python services/producer_service.py
   ```

4. **Disparar Eventos**
   - Via GPIO: Pressione os botões nos pinos 17 ou 18
   - Via API: Use curl ou qualquer cliente HTTP

## 📚 Documentação Adicional

- `docs/API_ROUTES.md` - Documentação completa da API REST
- `test_api_producer.py` - Exemplos de uso da API em Python

---

**Desenvolvido com ❤️ para o sistema de NVR**
