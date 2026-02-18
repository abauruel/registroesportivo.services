"""
Producer Service - Modo Híbrido (GPIO + API REST)
Aceita eventos de trigger tanto de hardware GPIO quanto de requisições HTTP
"""
import time
import redis
import threading
import sys
import os
from rq import Queue
from datetime import datetime

# Adiciona diretório pai ao path para importar config
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config import *

# Tenta importar GPIO, se falhar usa modo somente API
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    print("⚠️  RPi.GPIO não disponível - rodando em modo somente API")

# Setup Redis
redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
download_queue = Queue(DOWNLOAD_QUEUE, connection=redis_conn)

# Configurações
BUTTON_PIN_1 = 17
BUTTON_PIN_2 = 18
API_PORT = 5000


def trigger_event(channel):
    """Dispara evento de download (usado pelo GPIO)"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n{'='*60}")
    print(f"📥 Evento GPIO detectado - Canal {channel}")
    print(f"{'='*60}")
    print(f"  Timestamp: {timestamp}")
    print(f"  Canal: {channel}")
    
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


def setup_gpio():
    """Configura GPIO para monitorar botões"""
    if not GPIO_AVAILABLE:
        print("⚠️  GPIO não disponível - pulando configuração GPIO")
        return False
    
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUTTON_PIN_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(BUTTON_PIN_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Callbacks para detecção de eventos
        GPIO.add_event_detect(
            BUTTON_PIN_1,
            GPIO.FALLING,
            callback=lambda x: trigger_event(channel=1),
            bouncetime=300
        )
        GPIO.add_event_detect(
            BUTTON_PIN_2,
            GPIO.FALLING,
            callback=lambda x: trigger_event(channel=2),
            bouncetime=300
        )
        
        print("✅ GPIO configurado com sucesso")
        print(f"   Pin {BUTTON_PIN_1} → Canal 1")
        print(f"   Pin {BUTTON_PIN_2} → Canal 2")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar GPIO: {e}")
        return False


def start_api_server():
    """Inicia servidor Flask em thread separada"""
    from services.producer_routes import app
    
    print(f"\n🌐 Iniciando API REST em 0.0.0.0:{API_PORT}")
    print(f"   Endpoints disponíveis:")
    print(f"   GET  /health")
    print(f"   POST /trigger")
    print(f"   POST /trigger/<channel>")
    print(f"   GET  /status/<job_id>")
    print()
    
    # Desabilita logs do Flask para não poluir o terminal
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.WARNING)
    
    app.run(host='0.0.0.0', port=API_PORT, debug=False, use_reloader=False)


def main():
    """Função principal que inicia o producer em modo híbrido (GPIO + API)"""
    print("\n" + "="*70)
    print("🚀 PRODUCER SERVICE - Modo Híbrido (GPIO + API REST)")
    print("="*70)
    
    # Configura GPIO se disponível
    gpio_ok = setup_gpio()
    
    # Inicia servidor API em thread separada
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    print("\n" + "="*70)
    print("✅ Producer iniciado com sucesso!")
    print("="*70)
    
    if gpio_ok:
        print(f"📍 GPIO: Monitorando eventos nos pinos {BUTTON_PIN_1} e {BUTTON_PIN_2}")
    else:
        print("📍 GPIO: Não disponível (somente API ativa)")
    
    print(f"🌐 API: Escutando em http://0.0.0.0:{API_PORT}")
    print("\n💡 Exemplos de uso da API:")
    print(f"   curl http://localhost:{API_PORT}/health")
    print(f"   curl -X POST http://localhost:{API_PORT}/trigger/1")
    print(f"   curl -X POST http://localhost:{API_PORT}/trigger -H 'Content-Type: application/json' -d '{{\"channel\": 2}}'")
    print("\n" + "="*70)
    print("\nPressione Ctrl+C para parar\n")
    
    # Loop principal - mantém o programa rodando
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Encerrando producer...")
        if gpio_ok:
            GPIO.cleanup()
        sys.exit(0)


if __name__ == '__main__':
    main()

