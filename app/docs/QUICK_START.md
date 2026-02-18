# 🚀 Início Rápido - Teste Sem Hardware

Este guia mostra como testar o sistema **sem precisar de GPIO**.

## 📋 O que você precisa

- Python 3.x
- Redis rodando (para testes com worker) - ou nenhuma dependência para simulação simples!

## ⚡ Início Ultra-Rápido (0 instalação)

### Simulador Simples - Sem Redis, Sem Dependências

```bash
# Executar simulação de evento no canal 1
python3 simulator_simple.py --channel 1

# Modo interativo
python3 simulator_simple.py
```

## 🔧 Teste Completo com Redis e Workers

### 1. Iniciar Redis (Podman/Docker)

```bash
cd /home/abauruel/www/onvif_learn/RE
podman compose up -d redis
```

### 2. Instalar Dependências Python (se necessário)

```bash
cd /home/abauruel/www/onvif_learn/RE
pip install redis rq python-dotenv requests
# ou usando ambiente virtual
.venv/bin/pip install redis rq python-dotenv requests
```

### 3. Limpar Jobs Antigos (se houver problemas)

```bash
cd /home/abauruel/www/onvif_learn/RE/app
python3 clear_failed_jobs.py
```

### 4. Executar Worker (Terminal 1)

**IMPORTANTE:** O worker DEVE ser executado do diretório `app/`

```bash
cd /home/abauruel/www/onvif_learn/RE/app
./start_worker.sh download_queue
```

Ou manualmente:
```bash
cd /home/abauruel/www/onvif_learn/RE/app
../.venv/bin/rq worker download_queue
```

### 5. Enfileirar Tarefas (Terminal 2)

```bash
cd /home/abauruel/www/onvif_learn/RE/app
../.venv/bin/python simulator.py --quick

# Ou canal específico
../.venv/bin/python simulator.py --channel 2 --timestamp "2026-02-18 16:00:00"
```

### 6. Verificar Processamento

**Ver fila:**
```bash
podman exec -it redis_edge redis-cli LLEN download_queue
```

**Ver jobs falhados:**
```bash
cd /home/abauruel/www/onvif_learn/RE/app
../.venv/bin/python check_job.py
```

**Ver job específico:**
```bash
../.venv/bin/python check_job.py <JOB_ID>
```

### Exemplo de saída:

```
======================================================================
🔘 SIMULANDO EVENTO GPIO - Canal 1
======================================================================
  Timestamp: 2026-02-18 16:02:50
  Canal: 1

📥 [1/3] Producer captura evento GPIO...
   ├─ Evento detectado no pino GPIO (simulado)
   ├─ Timestamp capturado: 2026-02-18 16:02:50
   └─ Parâmetros: channel=1, timestamp='2026-02-18 16:02:50'

⬇️  [2/3] Download Service processa requisição...
   ├─ Conectando ao NVR (simulado)...
   ├─ Canal: 1
   ├─ Timestamp: 2026-02-18 16:02:50
   ├─ Baixando 15 segundos antes do timestamp...
   ├─ Arquivo gerado: videos/channel_1_2026-02-18_16-02-50.mp4
   └─ ✅ Download concluído com sucesso (mock)

⬆️  [3/3] Upload Service enviaria arquivo...
   ├─ Arquivo: videos/channel_1_2026-02-18_16-02-50.mp4
   ├─ Destino: API de upload (mock)
   └─ Upload concluído (simulado)

======================================================================
✅ SIMULAÇÃO COMPLETA
======================================================================
```

## 🐛 Problemas Comuns

### ❌ "ValueError: Invalid attribute name: services.download_service.download_video"

**Causa:** Worker não está executando do diretório correto (`app/`)

**Solução:**
```bash
cd /home/abauruel/www/onvif_learn/RE/app
./start_worker.sh download_queue
```

### ❌ Fila vazia mas jobs não processam

**Causa:** Jobs falharam rapidamente (0.004s) por erro de importação

**Solução:**
```bash
# Ver jobs falhados
cd /home/abauruel/www/onvif_learn/RE/app
../.venv/bin/python check_job.py

# Limpar jobs falhados
../.venv/bin/python clear_failed_jobs.py

# Enfileirar novamente
../.venv/bin/python simulator.py --quick
```

### ❌ "No module named 'redis'"

**Solução:**
```bash
cd /home/abauruel/www/onvif_learn/RE
.venv/bin/pip install redis rq
```

## 📊 Scripts Úteis

| Script | Função |
|--------|--------|
| `simulator_simple.py` | Simulação visual sem infraestrutura |
| `simulator.py` | Enfileiramento real no Redis |
| `start_worker.sh` | Inicia worker com PATH correto |
| `check_job.py` | Verifica status de jobs |
| `clear_failed_jobs.py` | Limpa jobs falhados |
| `test_e2e.py` | Teste end-to-end completo |

## ✅ Opção 1: Simulador Simples (Recomendado para começar)

O simulador simples mostra todo o fluxo sem precisar de infraestrutura:

```bash
# Executar simulação de evento no canal 1
python3 simulator_simple.py --channel 1

# Executar simulação de evento no canal 2
python3 simulator_simple.py --channel 2

# Modo interativo (menu)
python3 simulator_simple.py
```

Execute testes sem necessidade de infraestrutura:

```bash
# Teste de validação (verifica estrutura do projeto)
cd tests
python3 test_validation.py

# Teste end-to-end completo com mocks
python3 test_e2e_simulation.py

# Teste simples com mocks
python3 test_mock_simple.py
```

### Exemplo de execução:

```bash
cd tests
python3 test_validation.py
```

Saída esperada:
```
test_01_files_exist (__main__.ProjectValidationTest.test_01_files_exist) ... ok
test_02_config_has_required_values (__main__.ProjectValidationTest.test_02_config_has_required_values) ... ok
test_03_video_processor_exists (__main__.ProjectValidationTest.test_03_video_processor_exists) ... ok
test_04_upload_service_exists (__main__.ProjectValidationTest.test_04_upload_service_exists) ... ok
test_05_download_service_function (__main__.ProjectValidationTest.test_05_download_service_function) ... ok
test_06_producer_service_exists (__main__.ProjectValidationTest.test_06_producer_service_exists) ... ok
test_07_jftech_integration_exists (__main__.ProjectValidationTest.test_07_jftech_integration_exists) ... ok
test_08_timestamp_format_validation (__main__.ProjectValidationTest.test_08_timestamp_format_validation) ... ok
test_09_flow_logic (__main__.ProjectValidationTest.test_09_flow_logic) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.003s

OK
```

## 📦 Quando quiser infraestrutura completa

Para testes mais avançados com Redis e workers, instale as dependências:

```bash
# Instalar dependências
pip3 install redis rq python-dotenv requests

# Iniciar Redis (em terminal separado)
redis-server

# Executar worker (em terminal separado)
rq worker download_queue

# Usar simulador com Redis
python3 simulator.py --channel 1
```

## 📚 Mais informações

- [SIMULACAO.md](docs/SIMULACAO.md) - Guia completo de simulação
- [TESTES_README.md](docs/TESTES_README.md) - Documentação dos testes
- [README.md](docs/README.md) - Documentação completa do projeto

## 🎯 Resumo Rápido

| Ferramenta | Requer Redis? | Uso |
|------------|---------------|-----|
| `simulator_simple.py` | ❌ | Demonstração visual do fluxo |
| `test_validation.py` | ❌ | Validar estrutura do projeto |
| `test_e2e_simulation.py` | ❌ | Teste completo com mocks |
| `simulator.py` | ✅ | Enfileiramento real |
| `start_worker.sh` | ✅ | Worker para processar jobs |
| `check_job.py` | ✅ | Inspecionar jobs no Redis |
| `clear_failed_jobs.py` | ✅ | Limpar jobs falhados |
| `test_e2e.py` | ✅ | Teste end-to-end real |

## 💡 Dica

1. **Comece com** `simulator_simple.py` para entender o fluxo
2. **Depois use** `simulator.py + start_worker.sh` para testar com Redis
3. **Se algo falhar**, use `check_job.py` para diagnosticar
4. **Limpe erros** com `clear_failed_jobs.py`
