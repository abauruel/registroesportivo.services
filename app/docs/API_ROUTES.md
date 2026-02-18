# API REST - Producer Service

## Visão Geral
O Producer Service agora aceita eventos de trigger tanto via GPIO (hardware) quanto via API REST.

## Endpoints Disponíveis

### 1. Health Check
Verifica o status do serviço.

**Request:**
```http
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "service": "producer_service",
  "redis_connected": true
}
```

---

### 2. Trigger com JSON
Dispara um evento de download fornecendo todos os parâmetros via JSON.

**Request:**
```http
POST /trigger
Content-Type: application/json

{
  "channel": 1,
  "timestamp": "2026-02-18 16:00:00"
}
```

**Parâmetros:**
- `channel` (obrigatório): Número do canal (0-63)
- `timestamp` (opcional): Data/hora no formato "YYYY-MM-DD HH:MM:SS". Se omitido, usa timestamp atual.

**Response (sucesso):**
```json
{
  "status": "success",
  "message": "Evento enfileirado para canal 1",
  "channel": 1,
  "timestamp": "2026-02-18 16:00:00",
  "job_id": "abc123-def456-..."
}
```

**Response (erro):**
```json
{
  "error": "Campo 'channel' é obrigatório"
}
```

---

### 3. Trigger com URL Parameter
Dispara um evento especificando o canal diretamente na URL.

**Request:**
```http
POST /trigger/1
```

ou com timestamp via query string:

```http
POST /trigger/1?timestamp=2026-02-18 16:00:00
```

**Parâmetros:**
- `channel` (na URL): Número do canal (0-63)
- `timestamp` (query string opcional): Data/hora no formato "YYYY-MM-DD HH:MM:SS"

**Response:**
Mesmo formato do endpoint `/trigger`

---

### 4. Consultar Status do Job
Verifica o status de um job enfileirado.

**Request:**
```http
GET /status/<job_id>
```

**Response:**
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

**Status possíveis:**
- `queued` - Na fila aguardando processamento
- `started` - Em execução
- `finished` - Concluído com sucesso
- `failed` - Falhou

---

## Exemplos de Uso

### Usando curl

#### 1. Health Check
```bash
curl http://localhost:5000/health
```

#### 2. Trigger simples (canal 1, timestamp atual)
```bash
curl -X POST http://localhost:5000/trigger/1
```

#### 3. Trigger com timestamp específico
```bash
curl -X POST "http://localhost:5000/trigger/2?timestamp=2026-02-18%2016:00:00"
```

#### 4. Trigger com JSON completo
```bash
curl -X POST http://localhost:5000/trigger \
  -H "Content-Type: application/json" \
  -d '{"channel": 3, "timestamp": "2026-02-18 16:30:00"}'
```

#### 5. Consultar status de um job
```bash
curl http://localhost:5000/status/abc123-def456-...
```

### Usando Python requests

```python
import requests

# Health check
response = requests.get('http://localhost:5000/health')
print(response.json())

# Trigger evento
response = requests.post('http://localhost:5000/trigger', json={
    'channel': 1,
    'timestamp': '2026-02-18 16:00:00'
})
result = response.json()
print(f"Job ID: {result['job_id']}")

# Verificar status
job_id = result['job_id']
response = requests.get(f'http://localhost:5000/status/{job_id}')
print(response.json())
```

### Usando JavaScript fetch

```javascript
// Trigger evento
fetch('http://localhost:5000/trigger', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    channel: 1,
    timestamp: '2026-02-18 16:00:00'
  })
})
.then(response => response.json())
.then(data => console.log('Job ID:', data.job_id));
```

---

## Executando o Serviço

### Modo Híbrido (GPIO + API)
Inicia tanto o monitoramento GPIO quanto a API REST:

```bash
cd /home/abauruel/www/onvif_learn/RE/app
python services/producer_service.py
```

### Modo Somente API (sem GPIO)
Se você quiser executar apenas a API REST sem GPIO:

```bash
cd /home/abauruel/www/onvif_learn/RE/app
python services/producer_routes.py
```

---

## Validações

### Canal
- Deve ser um número inteiro
- Deve estar entre 0 e 63
- É obrigatório

### Timestamp
- Formato: `YYYY-MM-DD HH:MM:SS`
- Exemplo válido: `2026-02-18 16:00:00`
- Se omitido, usa timestamp atual
- É opcional

---

## Códigos de Resposta HTTP

- `200 OK` - Requisição bem-sucedida
- `400 Bad Request` - Parâmetros inválidos ou faltando
- `404 Not Found` - Job não encontrado (endpoint /status)
- `500 Internal Server Error` - Erro interno do servidor
