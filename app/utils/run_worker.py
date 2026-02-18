#!/usr/bin/env python3
"""
Worker wrapper - Executa RQ worker com PYTHONPATH configurado
"""
import sys
import os

# Adiciona o diretório app ao PYTHONPATH
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)

# Agora importa e executa o worker
from rq import Worker, Queue, Connection
import redis
import config

# Conecta ao Redis
redis_conn = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)

def main():
    """Executa o worker"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RQ Worker para processamento de downloads')
    parser.add_argument('queue', nargs='?', default='download_queue',
                        help='Nome da fila (padrão: download_queue)')
    
    args = parser.parse_args()
    
    # Cria conexão e fila
    with Connection(redis_conn):
        queue = Queue(args.queue)
        worker = Worker([queue])
        
        print(f"🚀 Worker iniciado para fila: {args.queue}")
        print(f"📡 Redis: {config.REDIS_HOST}:{config.REDIS_PORT}")
        print(f"📂 PYTHONPATH: {app_dir}")
        print("="*60)
        
        worker.work()

if __name__ == '__main__':
    main()
