# Troubleshooting - Download Falhou

## ❌ Problema: "Download não completado ou falhou"

### Causas Possíveis

#### 1. **Timeout do RQ Worker** ✅ CORRIGIDO
**Sintoma:** 
```
rq.timeouts.JobTimeoutException: Task exceeded maximum timeout value (180 seconds)
```

**Causa:** O RQ worker tem um timeout padrão de 180 segundos. Se o download demorar exatamente 180s, o worker mata o job antes dele completar.

**Solução Aplicada:**
```python
# Timeout do job aumentado para 5 minutos (300s)
job = download_queue.enqueue(
    "services.download_service.download_video",
    timestamp=timestamp,
    channel=channel,
    job_timeout=300  # 5 minutos (era padrão 180s)
)
```

**Configuração Atual:**
- Timeout do download no SDK: 180 segundos (3 minutos)
- Timeout do job no RQ: 300 segundos (5 minutos)
- Margem de segurança: 2 minutos

**Fluxo temporal:**
```
0s ──────────────────────> 180s ────────────> 300s
│                           │                  │
Início                 Max download      Max job RQ
                       (SDK timeout)     (Worker timeout)
                                         
                       [───── 2 min de margem ─────]
```

---

#### 2. **Timeout do download muito curto** ✅ CORRIGIDO
**Sintoma:** Download não completa em 30 segundos

**Solução:** Aumentado de 30s para 180s (3 minutos)

O timeout estava configurado incorretamente como 30 segundos quando deveria ser 180 segundos.

---

#### 2. **Timeout do download muito curto** ✅ CORRIGIDO
**Sintoma:** Download não completa em 30 segundos

**Solução:** Aumentado de 30s para 180s (3 minutos)

O timeout estava configurado incorretamente como 30 segundos quando deveria ser 180 segundos.

---

#### 3. **Canal sem gravações**
**Sintoma:** 
```
! Nenhuma gravação encontrada
  Código: -70119 - Sem gravações no período ou canal inativo
```

**Causas:**
- Canal sem câmera conectada
- Canal desabilitado no NVR
- Sem gravações no período especificado (últimos 15 segundos)
- Canal fora do range (seu NVR tem canais 0-15)

**Soluções:**
1. Verifique se o canal tem câmera conectada no NVR
2. Verifique se o canal está habilitado
3. Verifique se há gravações recentes (últimos 15 segundos)
4. Tente outro canal (0-15)

**Teste:**
```bash
# Tente diferentes canais
curl -X POST http://localhost:5000/trigger/0  # Canal 0
curl -X POST http://localhost:5000/trigger/1  # Canal 1
curl -X POST http://localhost:5000/trigger/2  # Canal 2
```

---

#### 4. **Credenciais incorretas**
**Sintoma:**
```
✗ Login falhou
```

**Solução:**
Verifique o arquivo `.env`:
```bash
NVR_IP="192.168.x.x"
NVR_PORT=34567
NVR_USERNAME="admin"
NVR_PASSWORD="sua_senha"
```

---

#### 5. **NVR offline ou inacessível**
**Sintoma:**
```
✗ Falha ao conectar
```

**Teste de conectividade:**
```bash
# Ping no NVR
ping 192.168.x.x

# Verifica se a porta está aberta
nc -zv 192.168.x.x 34567
```

---

#### 6. **Diretório de downloads não existe**
**Sintoma:** Arquivo não é criado

**Solução:**
```bash
cd /home/abauruel/www/onvif_learn/RE/app
mkdir -p videos
chmod 755 videos
```

---

## 🔍 Como Verificar se a Linha 62 foi Executada

### Método 1: Logs Claros (RECOMENDADO)

Agora os logs são bem claros:

**✅ Sucesso (linha 62 executada):**
```
============================================================
✅ Download concluído com sucesso!
============================================================
   Arquivo: videos/nvr01_stream0_20260218_193050.mp4
   Tamanho: 245680 bytes
============================================================

============================================================
📤 Enfileirando upload do arquivo: videos/nvr01_stream0_...
   Upload Job ID: abc123-def456-...
   Status inicial: queued
   Fila: upload_queue
============================================================
```

**❌ Falha (linha 62 NÃO executada):**
```
============================================================
❌ Download falhou!
============================================================
   Arquivo esperado: videos/nvr01_stream0_20260218_193050.mp4
   Arquivo existe? False
   Motivo: Arquivo não foi criado pelo SDK
   ⚠️  Upload NÃO foi enfileirado
============================================================
```

### Método 2: Script de Verificação

```bash
cd /home/abauruel/www/onvif_learn/RE/app
../.venv/bin/python check_upload_queue.py
```

**Se linha 62 foi executada:**
```
📊 STATUS DA FILA DE UPLOAD: upload_queue
...
📋 Informações gerais:
   Jobs na fila (aguardando): 1  ← DEVE SER > 0
```

**Se linha 62 NÃO foi executada:**
```
📋 Informações gerais:
   Jobs na fila (aguardando): 0  ← Será 0
```

### Método 3: Verificar Arquivos Baixados

```bash
# Lista arquivos baixados
ls -lh /home/abauruel/www/onvif_learn/RE/app/videos/

# Se vazio, o download falhou
```

---

## 🧪 Teste Completo do Sistema

### Passo a Passo

#### 1. Inicie Redis
```bash
podman start redis_edge
podman ps | grep redis
```

#### 2. Inicie Worker de Download
```bash
cd /home/abauruel/www/onvif_learn/RE/app
rq worker download_queue
```

#### 3. Inicie Producer API
```bash
# Em outro terminal
cd /home/abauruel/www/onvif_learn/RE/app
../.venv/bin/python services/producer_service.py
```

#### 4. Dispare Evento
```bash
# Em outro terminal
curl -X POST http://localhost:5000/trigger/0
```

#### 5. Monitore os Logs

No terminal do worker, você deve ver:

**Progresso do download:**
```
⏳ Aguardando conclusão do download...
   5s - 32768 bytes baixados...
   10s - 98304 bytes baixados...
   15s - 163840 bytes baixados...
   20s - 229376 bytes baixados...

✓ Download/Reprodução concluído com sucesso
  Total de 245680 bytes baixados
```

**Se der certo:**
```
============================================================
✅ Download concluído com sucesso!
============================================================
   Arquivo: videos/nvr01_stream0_20260218_193050.mp4
   Tamanho: 245680 bytes
============================================================

============================================================
📤 Enfileirando upload do arquivo: ...
   Upload Job ID: ...
============================================================
```

#### 6. Verifique a Fila de Upload
```bash
cd /home/abauruel/www/onvif_learn/RE/app
../.venv/bin/python check_upload_queue.py
```

---

## 🔧 Correções Aplicadas

### 1. Timeout aumentado
```python
# ANTES (incorreto):
timeout = 30  # 3 minutos

# DEPOIS (correto):
timeout = 180  # 3 minutos (180 segundos)
```

### 2. Progresso do download
Agora mostra progresso a cada 5 segundos:
```
⏳ Aguardando conclusão do download...
   5s - 32768 bytes baixados...
   10s - 98304 bytes baixados...
```

### 3. Logs melhorados
- ✅ Indica claramente quando o upload foi enfileirado
- ❌ Indica claramente quando o upload NÃO foi enfileirado
- 📊 Mostra tamanho do arquivo baixado
- 🔍 Mostra motivo da falha

---

## 📋 Checklist de Verificação

Antes de disparar um evento, verifique:

- [ ] Redis está rodando (`podman ps | grep redis`)
- [ ] Worker de download está rodando (`rq worker download_queue`)
- [ ] Producer API está rodando (na porta 5000)
- [ ] Arquivo `.env` está configurado com credenciais corretas
- [ ] NVR está acessível na rede
- [ ] Canal especificado tem câmera conectada e ativa
- [ ] Diretório `videos/` existe
- [ ] Há gravações disponíveis no período (últimos 15 segundos)

---

## 💡 Dicas

### Testar com canal conhecido
Se você sabe que o canal 1 tem câmera ativa:
```bash
curl -X POST http://localhost:5000/trigger/1
```

### Aumentar período de busca de gravações
No arquivo `jftecth_integration.py`, linha ~607:
```python
# ATUAL: 15 segundos antes
start_time = end_time - timedelta(seconds=15)

# TESTE: 60 segundos antes (para ter mais chance de encontrar gravação)
start_time = end_time - timedelta(seconds=60)
```

### Ver todos os arquivos baixados
```bash
ls -lht /home/abauruel/www/onvif_learn/RE/app/videos/ | head -10
```

### Limpar fila de upload
```bash
cd /home/abauruel/www/onvif_learn/RE/app
../.venv/bin/python -c "from rq import Queue; from redis import Redis; Queue('upload_queue', connection=Redis()).empty()"
```

---

**Última atualização:** 18 de Fevereiro de 2026
