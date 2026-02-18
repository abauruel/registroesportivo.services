# 🔧 Como Executar os Workers RQ

## ❌ Problema Identificado

Quando você executa `rq worker download_queue` de qualquer diretório, o RQ não consegue encontrar o módulo `services.download_service.download_video` porque o PYTHONPATH não está configurado corretamente.

**Erro:**
```
ValueError: Invalid attribute name: services.download_service.download_video
```

## ✅ Soluções

### Opção 1: Script Pronto (Recomendado)

Use o script que já configura tudo automaticamente:

```bash
# Do diretório RE/app, execute:
./start_worker.sh

# Ou para fila de upload:
./start_worker.sh upload_queue
```

### Opção 2: Executar do Diretório Correto

Execute o worker **do diretório app/**:

```bash
cd /home/abauruel/www/onvif_learn/RE/app
/home/abauruel/www/onvif_learn/RE/.venv/bin/python -m rq worker download_queue
```

Ou sem ambiente virtual:

```bash
cd /home/abauruel/www/onvif_learn/RE/app
python3 -m rq worker download_queue
```

### Opção 3: Configurar PYTHONPATH

```bash
export PYTHONPATH=/home/abauruel/www/onvif_learn/RE/app:$PYTHONPATH
rq worker download_queue
```

## 📋 Fluxo Completo de Teste

### Terminal 1: Redis (se ainda não estiver rodando)
```bash
cd /home/abauruel/www/onvif_learn/RE
podman compose up -d redis
```

### Terminal 2: Worker de Download
```bash
cd /home/abauruel/www/onvif_learn/RE/app
./start_worker.sh download_queue
```

### Terminal 3: Worker de Upload (opcional)
```bash
cd /home/abauruel/www/onvif_learn/RE/app
./start_worker.sh upload_queue
```

### Terminal 4: Simulador
```bash
cd /home/abauruel/www/onvif_learn/RE/app
/home/abauruel/www/onvif_learn/RE/.venv/bin/python simulator.py --quick
```

## 🔍 Verificar Jobs na Fila

```bash
# Ver quantos jobs na fila
podman exec -it redis_edge redis-cli LLEN download_queue

# Ver todas as chaves
podman exec -it redis_edge redis-cli KEYS "*"

# Limpar fila (se necessário)
podman exec -it redis_edge redis-cli DEL rq:queue:download_queue
```

## 📊 Estrutura Esperada

```
RE/
├── app/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── download_service.py
│   │   └── jftecth_integration.py
│   ├── simulator.py
│   ├── start_worker.sh  ← Script para executar worker
│   └── config.py
└── .venv/
```

## 💡 Por que precisa executar do diretório app/?

O RQ precisa importar `services.download_service.download_video`. Para isso funcionar:

1. O diretório `app/` precisa estar no PYTHONPATH
2. `services/` precisa ser um módulo Python (tem `__init__.py` ✓)
3. O worker precisa ser executado do contexto correto

Quando você executa do diretório `app/`, o Python automaticamente adiciona esse diretório ao PYTHONPATH, permitindo que `import services.download_service` funcione.
