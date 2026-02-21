"""
Producer API Routes - Rotas REST para acionar eventos de trigger
"""
from flask import Flask, request, jsonify
from datetime import datetime
import redis
from rq import Queue
import sys
import os

# Adiciona diretório pai ao path para importar config
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config import REDIS_HOST, REDIS_PORT, DOWNLOAD_QUEUE, now_timestamp

# Setup Flask
app = Flask(__name__)

# Setup Redis
redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
download_queue = Queue(DOWNLOAD_QUEUE, connection=redis_conn)


def trigger_event_api(channel, timestamp=None, source="API"):
    """
    Dispara evento de download via API
    
    Args:
        channel (int): Número do canal (0-63)
        timestamp (str): Timestamp no formato "YYYY-MM-DD HH:MM:SS" (opcional)
        source (str): Origem do evento (padrão: "API")
    
    Returns:
        dict: Resultado da operação com job_id
    """
    # Se timestamp não fornecido, usa hora atual
    if timestamp is None:
        timestamp = now_timestamp()
    
    # Valida formato do timestamp
    try:
        datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return {"error": f"Timestamp inválido. Use formato: YYYY-MM-DD HH:MM:SS"}, 400
    
    # Valida canal
    if not isinstance(channel, int) or not (0 <= channel <= 63):
        return {"error": "Canal deve ser um número inteiro entre 0 e 63"}, 400
    
    print(f"\n{'='*60}")
    print(f"📥 Evento {source} detectado - Canal {channel}")
    print(f"{'='*60}")
    print(f"  Timestamp: {timestamp}")
    print(f"  Canal: {channel}")
    print(f"  Origem: {source}")
    
    # Enfileira a tarefa com timeout de 5 minutos
    # (download tem timeout de 3min, precisa de margem para processar)
    job = download_queue.enqueue(
        "services.download_service.download_video",
        timestamp=timestamp,
        channel=channel,
        job_timeout=300  # 5 minutos
    )
    
    print(f"  Job ID: {job.id}")
    print(f"  Status: {job.get_status()}")
    print(f"{'='*60}\n")
    
    return {
        "status": "success",
        "message": f"Evento enfileirado para canal {channel}",
        "channel": channel,
        "timestamp": timestamp,
        "job_id": job.id
    }, 200


# ==================== ROTAS API ====================

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    GET /health
    """
    try:
        redis_ok = redis_conn.ping()
    except:
        redis_ok = False
    
    return jsonify({
        "status": "ok",
        "service": "producer_service",
        "redis_connected": redis_ok
    }), 200


@app.route('/trigger', methods=['POST'])
def trigger_json():
    """
    Dispara evento via JSON payload
    
    POST /trigger
    Body: {
        "channel": 1,              # Obrigatório: 0-63
        "timestamp": "2026-02-18 16:00:00"  # Opcional: YYYY-MM-DD HH:MM:SS
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            "error": "JSON payload obrigatório",
            "exemplo": {
                "channel": 1,
                "timestamp": "2026-02-18 16:00:00"
            }
        }), 400
    
    # Valida canal
    channel = data.get('channel')
    if channel is None:
        return jsonify({"error": "Campo 'channel' é obrigatório"}), 400
    
    try:
        channel = int(channel)
    except ValueError:
        return jsonify({"error": "Canal deve ser um número inteiro"}), 400
    
    # Timestamp opcional
    timestamp = data.get('timestamp')
    
    # Dispara evento
    result, status_code = trigger_event_api(channel, timestamp=timestamp, source="API")
    return jsonify(result), status_code


@app.route('/trigger/<int:channel>', methods=['POST', 'GET'])
def trigger_channel(channel):
    """
    Dispara evento via URL parameter
    
    GET/POST /trigger/1
    GET/POST /trigger/2?timestamp=2026-02-18 16:00:00
    
    Query params:
        timestamp (str): Opcional - formato YYYY-MM-DD HH:MM:SS
    """
    # Timestamp pode vir na query string ou no JSON
    timestamp = request.args.get('timestamp')
    
    if not timestamp and request.is_json:
        json_data = request.get_json(silent=True)
        if json_data:
            timestamp = json_data.get('timestamp')
    
    # Dispara evento
    result, status_code = trigger_event_api(channel, timestamp=timestamp, source="API")
    return jsonify(result), status_code


@app.route('/status/<job_id>', methods=['GET'])
def check_job_status(job_id):
    """
    Consulta status de um job
    
    GET /status/<job_id>
    """
    from rq.job import Job
    
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        
        return jsonify({
            "job_id": job.id,
            "status": job.get_status(),
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "ended_at": job.ended_at.isoformat() if job.ended_at else None,
            "result": job.result
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Job não encontrado: {str(e)}"
        }), 404


if __name__ == '__main__':
    # Executa apenas API (sem GPIO)
    print("🌐 Iniciando Producer API (somente modo API)")
    print("   Endpoints:")
    print("   GET  /health")
    print("   POST /trigger")
    print("   POST /trigger/<channel>")
    print("   GET  /status/<job_id>")
    app.run(host='0.0.0.0', port=5000, debug=False)
