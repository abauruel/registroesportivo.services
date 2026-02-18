# ⚠️ GUIA DEFINITIVO: Como Executar o Worker Corretamente

## ❌ O Problema que Você Estava Enfrentando

Você estava executando o worker do diretório **ERRADO**:

```bash
# ❌ ERRADO - Do diretório RE/
cd /home/abauruel/www/onvif_learn/RE
rq worker download_queue
# Resultado: ValueError: Invalid attribute name: services.download_service.download_video
```

## ✅ A Solução Correta

Execute o worker do diretório `app/`:

```bash
# ✅ CORRETO - Do diretório RE/app/
cd /home/abauruel/www/onvif_learn/RE/app
./start_worker.sh download_queue
```

## 🔍 Por Que Precisa Ser no Diretório app/?

O RQ worker precisa importar: `services.download_service.download_video`

Estrutura de diretórios:
```
RE/
├── docker-compose.yaml
├── .venv/
└── app/                    ← EXECUTE DAQUI
    ├── config.py
    ├── simulator.py
    ├── start_worker.sh     ← USE ESTE SCRIPT
    └── services/
        ├── __init__.py
        ├── download_service.py  ← ESTE ARQUIVO
        └── jftecth_integration.py
```

Quando você executa do diretório `app/`, o Python adiciona `app/` ao PYTHONPATH automaticamente, permitindo que `import services.download_service` funcione.

## 📋 Passo a Passo Definitivo

### 1️⃣ Verificar Ambiente (sempre faça isso primeiro!)

```bash
cd /home/abauruel/www/onvif_learn/RE/app
../.venv/bin/python check_worker_env.py
```

Se aparecer `✅ TUDO OK!`, pode prosseguir.

### 2️⃣ Limpar Jobs Antigos (se houver erros anteriores)

```bash
cd /home/abauruel/www/onvif_learn/RE/app
../.venv/bin/python clear_failed_jobs.py
```

### 3️⃣ Executar Worker (Terminal 1)

```bash
cd /home/abauruel/www/onvif_learn/RE/app
./start_worker.sh download_queue
```

Você verá:
```
🚀 Iniciando RQ Worker...
📂 Diretório: /home/abauruel/www/onvif_learn/RE/app
📡 Fila: download_queue
=
🐍 Usando ambiente virtual
16:XX:XX Worker XXXXX: started with PID XXXXX, version 2.6.1
16:XX:XX *** Listening on download_queue...
```

### 4️⃣ Enfileirar Tarefas (Terminal 2)

```bash
cd /home/abauruel/www/onvif_learn/RE/app
../.venv/bin/python simulator.py --channel 1
```

### 5️⃣ Verificar Processamento

No Terminal 1 (worker), você verá:
```
16:XX:XX download_queue: services.download_service.download_video(...)
Iniciando download...
...
✅ Sucesso!
```

## 🎯 Comandos de Diagnóstico

### Ver jobs falhados:
```bash
cd /home/abauruel/www/onvif_learn/RE/app
../.venv/bin/python check_job.py
```

### Ver job específico:
```bash
cd /home/abauruel/www/onvif_learn/RE/app
../.venv/bin/python check_job.py <JOB_ID>
```

### Verificar fila no Redis:
```bash
podman exec -it redis_edge redis-cli LLEN download_queue
```

### Ver todas as chaves do RQ:
```bash
podman exec -it redis_edge redis-cli KEYS "rq:*"
```

## 🚨 Checklist de Segurança

Antes de executar o worker, sempre verifique:

- [ ] Estou no diretório `/home/abauruel/www/onvif_learn/RE/app`?
- [ ] Redis está rodando? (`podman ps | grep redis`)
- [ ] Dependências instaladas? (`check_worker_env.py` passou?)
- [ ] Jobs antigos limpos? (se necessário: `clear_failed_jobs.py`)

## 💡 Resumo Visual

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUXO CORRETO                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. cd /home/abauruel/www/onvif_learn/RE/app                │
│                                                             │
│  2. ../.venv/bin/python check_worker_env.py                 │
│     └─ Deve mostrar: ✅ TUDO OK!                            │
│                                                             │
│  3. ./start_worker.sh download_queue                        │
│     └─ Worker fica escutando...                             │
│                                                             │
│  4. [Outro terminal] ../.venv/bin/python simulator.py -q    │
│     └─ Job enfileirado                                      │
│                                                             │
│  5. Worker processa automaticamente                         │
│     └─ ✅ Sucesso!                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🎓 Explicação Técnica

**Erro:** `ValueError: Invalid attribute name: services.download_service.download_video`

**Causa:** O worker está tentando importar `services.download_service`, mas o diretório `services/` não está no PYTHONPATH.

**Solução:** Executar worker do diretório `app/`, que automaticamente adiciona `app/` ao PYTHONPATH, permitindo que `import services.download_service` funcione.

**Por que `start_worker.sh` funciona?**
```bash
#!/bin/bash
cd "$(dirname "$0")"  # ← Vai para o diretório do script (app/)
../.venv/bin/rq worker download_queue
```

O script automaticamente muda para o diretório `app/` antes de executar o worker!
