# Guia de Simulação - Testando sem Hardware GPIO

Este guia explica como testar o sistema sem ter GPIO/Raspberry Pi disponível.

## 🎯 Ferramentas de Simulação

### 1. `simulator.py` - Simulador de Eventos
Dispara eventos manualmente sem precisar de GPIO.

**Uso:**
```bash
# Modo interativo (recomendado para testes manuais)
python3 simulator.py

# Teste rápido - dispara evento canal 1
python3 simulator.py --quick

# Disparar evento específico
python3 simulator.py --channel 1
python3 simulator.py --channel 2 --timestamp "2026-02-18 14:30:00"
```

**Modo Interativo:**
```
Comandos:
  1 - Simular botão canal 1
  2 - Simular botão canal 2
  c - Escolher canal personalizado
  t - Escolher timestamp personalizado
  q - Sair
```

### 2. `producer_simulator.py` - Producer sem GPIO
Versão do producer que monitora teclado ao invés de GPIO.

**Uso:**
```bash
# Modo teclado (padrão)
python3 producer_simulator.py

# Modo automático - dispara eventos a cada 5 segundos
python3 producer_simulator.py --auto

# Modo automático com intervalo customizado
python3 producer_simulator.py --auto --interval 10
```

**Modo Teclado:**
```
Pressione as teclas:
  1 - Canal 1 (simula GPIO 17)
  2 - Canal 2 (simula GPIO 18)
  3 - Canal 3
  4 - Canal 4
  q - Sair
```

### 3. `tests/test_e2e_simulation.py` - Teste End-to-End
Valida fluxo completo sem nenhuma dependência externa.

**Uso:**
```bash
python3 tests/test_e2e_simulation.py
```

## 📋 Cenários de Teste

### Cenário 1: Teste Rápido (Sem Redis)
Valida lógica sem infraestrutura:

```bash
python3 tests/test_e2e_simulation.py
```

**O que testa:**
- ✓ Trigger de eventos
- ✓ Download service (mockado)
- ✓ Upload service (mockado)
- ✓ Fluxo completo

### Cenário 2: Teste com Redis (Sem GPIO)
Testa com fila real, mas sem GPIO:

```bash
# Terminal 1: Inicie Redis
redis-server

# Terminal 2: Inicie worker de download
rq worker download_queue

# Terminal 3: Inicie worker de upload
rq worker upload_queue

# Terminal 4: Execute simulador
python3 simulator.py
```

**No simulador:**
1. Pressione `1` para disparar evento canal 1
2. Observe workers processando nos outros terminais

### Cenário 3: Producer Simulado + Workers
Simula producer rodando continuamente:

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Worker download
rq worker download_queue

# Terminal 3: Worker upload
rq worker upload_queue

# Terminal 4: Producer simulado
python3 producer_simulator.py

# Ou modo automático (dispara eventos sozinho)
python3 producer_simulator.py --auto --interval 10
```

### Cenário 4: Teste Completo com NVR Real
Testa download real do NVR:

```bash
# 1. Configure .env com credenciais do NVR
cat > .env << EOF
NVR_IP=192.168.0.168
NVR_PORT=34567
NVR_USERNAME=service
NVR_PASSWORD=sua_senha
EOF

# 2. Inicie infraestrutura
redis-server &
rq worker download_queue &
rq worker upload_queue &

# 3. Dispare evento com simulator
python3 simulator.py --channel 1

# 4. Verifique logs do worker para ver download real
```

## 🔍 Monitoramento

### Ver status das filas:
```bash
rq info
```

### Ver jobs na fila:
```python
import redis
from rq import Queue

r = redis.Redis()
dq = Queue('download_queue', connection=r)
uq = Queue('upload_queue', connection=r)

print(f"Downloads pendentes: {len(dq)}")
print(f"Uploads pendentes: {len(uq)}")

# Ver jobs
for job in dq.jobs:
    print(f"Job {job.id}: {job.func_name} - {job.get_status()}")
```

### Limpar filas:
```python
import redis
from rq import Queue

r = redis.Redis()
Queue('download_queue', connection=r).empty()
Queue('upload_queue', connection=r).empty()
```

## 🧪 Exemplos Práticos

### Exemplo 1: Disparar eventos sequenciais
```bash
# Dispara 3 eventos com intervalo
python3 simulator.py --channel 1
sleep 5
python3 simulator.py --channel 2
sleep 5
python3 simulator.py --channel 1
```

### Exemplo 2: Teste com timestamp específico
```bash
# Baixar gravação de ontem às 14:30
python3 simulator.py --channel 1 --timestamp "2026-02-17 14:30:00"
```

### Exemplo 3: Teste automatizado
```python
# script: auto_test.py
from simulator import trigger_download
import time

# Dispara eventos em sequência
for i in range(5):
    print(f"\n--- Teste {i+1} ---")
    trigger_download(channel=1)
    time.sleep(10)  # Aguarda 10s entre eventos
```

### Exemplo 4: Validar download real (sem upload)
```bash
# Dispara apenas download, sem upload
python3 -c "
from services.download_service import download_video
result = download_video(channel=1)
print(f'Arquivo baixado: {result}')
"
```

## 📊 Comparação: Real vs Simulado

| Componente | Real | Simulado |
|------------|------|----------|
| GPIO | Raspberry Pi + botões físicos | Teclado / Script |
| Producer | `producer_service.py` | `producer_simulator.py` |
| Redis/RQ | Redis server + workers | Mesmo (ou mock) |
| Download | SDK JFTech + NVR real | SDK real (ou mock) |
| Upload | API externa real | API real (ou mock) |

## 🎓 Workflow de Desenvolvimento

```
1. Desenvolvimento Local (Sem hardware)
   ↓
   • Use test_e2e_simulation.py
   • Valide lógica com mocks
   
2. Testes com Infraestrutura (Sem GPIO)
   ↓
   • Redis + Workers
   • Use simulator.py
   • Teste filas e processamento
   
3. Testes com NVR (Sem GPIO)
   ↓
   • Configure .env
   • Use simulator.py
   • Valide downloads reais
   
4. Produção (Com GPIO)
   ↓
   • Raspberry Pi
   • Use producer_service.py
   • Botões físicos
```

## 🐛 Troubleshooting

### Eventos não processam
```bash
# Verifique se Redis está rodando
redis-cli ping

# Verifique workers
rq info

# Inicie worker se necessário
rq worker download_queue -v
```

### Erro ao importar módulos
```bash
# Execute do diretório app/
cd /home/abauruel/www/onvif_learn/RE/app
python3 simulator.py
```

### Downloads falham
```bash
# Verifique configuração NVR
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print(f\"NVR_IP: {os.getenv('NVR_IP')}\")
print(f\"NVR_PORT: {os.getenv('NVR_PORT')}\")
"

# Teste diretamente o SDK
cd app
python3 -c "from services.jftecth_integration import main; main()" 1 "2026-02-18 14:30:00"
```

## 📝 Checklist de Testes

- [ ] Teste de validação passa: `python3 tests/test_validation.py`
- [ ] Teste E2E passa: `python3 tests/test_e2e_simulation.py`
- [ ] Simulator dispara eventos: `python3 simulator.py --quick`
- [ ] Workers processam filas: `rq worker download_queue`
- [ ] Download real funciona (com NVR configurado)
- [ ] Upload funciona (com API configurada)

## 🚀 Quick Start para Testes

```bash
# 1. Teste básico (sem infraestrutura)
python3 tests/test_e2e_simulation.py

# 2. Teste com Redis
redis-server &
rq worker download_queue &
python3 simulator.py --quick

# 3. Teste completo
# Configure .env primeiro!
redis-server &
rq worker download_queue &
rq worker upload_queue &
python3 simulator.py
```

---

**💡 Dica:** Use `producer_simulator.py --auto` para gerar tráfego de teste contínuo enquanto desenvolve!
