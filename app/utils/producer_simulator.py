#!/usr/bin/env python3
"""
Producer Simulator - Versão sem GPIO para desenvolvimento/testes
Monitora teclado ao invés de pinos GPIO
"""

import sys
import os
from datetime import datetime
import time

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import redis
from rq import Queue
from config import *

# Setup Redis
redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
download_queue = Queue(DOWNLOAD_QUEUE, connection=redis_conn)

CHANNEL_MAP = {
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
}


def trigger_event(channel):
    """Dispara evento de download"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n🔔 Evento detectado - Canal {channel}")
    print(f"   Timestamp: {timestamp}")
    
    # Enfileira a tarefa
    job = download_queue.enqueue("services.download_service.download_video", 
                                  timestamp=timestamp, 
                                  channel=channel)
    
    print(f"   Job enfileirado: {job.id}")
    print(f"   Aguardando worker processar...")


def keyboard_mode():
    """Modo de monitoramento de teclado"""
    print("="*70)
    print(" PRODUCER SIMULATOR - MODO TECLADO")
    print("="*70)
    print("\n⚠️  SIMULAÇÃO ATIVA - Sem GPIO real")
    print("\nPressione as teclas para simular botões:")
    print("  1 - Canal 1 (GPIO 17)")
    print("  2 - Canal 2 (GPIO 18)")
    print("  3 - Canal 3")
    print("  4 - Canal 4")
    print("  q - Sair")
    print("="*70)
    print("\n✅ Producer Simulator iniciado... aguardando eventos\n")
    
    try:
        while True:
            # Lê entrada do usuário
            key = input("Pressione tecla (1-4) ou 'q' para sair: ").strip()
            
            if key.lower() == 'q':
                print("\n👋 Encerrando producer simulator...")
                break
            
            elif key in CHANNEL_MAP:
                channel = CHANNEL_MAP[key]
                trigger_event(channel)
            
            elif key.isdigit() and 0 <= int(key) <= 63:
                trigger_event(int(key))
            
            else:
                print(f"⚠️  Tecla '{key}' ignorada (use 1-4 ou 'q')")
    
    except KeyboardInterrupt:
        print("\n\n👋 Producer simulator interrompido")


def auto_mode(interval=5):
    """Modo automático - dispara eventos periodicamente para testes"""
    print("="*70)
    print(" PRODUCER SIMULATOR - MODO AUTOMÁTICO")
    print("="*70)
    print(f"\n⚠️  MODO DE TESTE - Disparando eventos a cada {interval} segundos")
    print("\nPressione Ctrl+C para parar")
    print("="*70)
    
    channels = [1, 2]
    idx = 0
    
    try:
        while True:
            channel = channels[idx % len(channels)]
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Auto-disparando canal {channel}")
            trigger_event(channel)
            
            idx += 1
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n\n👋 Modo automático interrompido")


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Producer Simulator - Monitora teclado ao invés de GPIO',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-a', '--auto', action='store_true',
                        help='Modo automático - dispara eventos periodicamente')
    parser.add_argument('-i', '--interval', type=int, default=5,
                        help='Intervalo em segundos para modo automático (padrão: 5)')
    
    args = parser.parse_args()
    
    if args.auto:
        auto_mode(interval=args.interval)
    else:
        keyboard_mode()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
