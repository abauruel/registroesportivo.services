#!/usr/bin/env python3
"""
Simulador de eventos GPIO - Para testes sem hardware
Permite simular pressionar botões e disparar eventos de download
"""

import sys
import os
from datetime import datetime

# Adiciona o diretório do app ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import redis
    from rq import Queue
    import config
    REDIS_AVAILABLE = True
    REDIS_HOST = config.REDIS_HOST
    REDIS_PORT = config.REDIS_PORT
    DOWNLOAD_QUEUE = config.DOWNLOAD_QUEUE
except ImportError as e:
    REDIS_AVAILABLE = False
    print(f"⚠️  Redis/RQ não disponível - modo demonstração ({e})")
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    DOWNLOAD_QUEUE = "download_queue"

# Setup Redis (se disponível)
if REDIS_AVAILABLE:
    redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    download_queue = Queue(DOWNLOAD_QUEUE, connection=redis_conn)
else:
    redis_conn = None
    download_queue = None


def trigger_download(channel, timestamp=None):
    """
    Simula um evento GPIO e enfileira download
    
    Args:
        channel (int): Número do canal (0-63)
        timestamp (str): Timestamp no formato "YYYY-MM-DD HH:MM:SS" (opcional)
    """
    # Se timestamp não fornecido, usa hora atual
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("\n" + "="*60)
    print(f"🔘 SIMULANDO EVENTO GPIO - Botão Canal {channel}")
    print("="*60)
    print(f"  Timestamp: {timestamp}")
    print(f"  Canal: {channel}")
    
    if not REDIS_AVAILABLE:
        print("  ⚠️  Redis não disponível - apenas demonstração")
        print("  💡 Instale: pip install redis rq")
        print("="*60)
        return None
    
    # Enfileira a tarefa
    try:
        job = download_queue.enqueue("services.download_service.download_video", 
                                      timestamp=timestamp, 
                                      channel=channel)
        
        print(f"  Job ID: {job.id}")
        print(f"  Status: {job.get_status()}")
        print("="*60)
        print("\n✅ Evento enfileirado com sucesso!")
        print(f"   Execute o worker para processar: rq worker {DOWNLOAD_QUEUE}")
        
        return job
    except Exception as e:
        print(f"  ✗ Erro ao enfileirar: {e}")
        print("  💡 Redis está rodando? Execute: redis-server")
        print("="*60)
        return None


def interactive_mode():
    """Modo interativo - permite disparar eventos via teclado"""
    print("\n" + "="*70)
    print(" SIMULADOR DE EVENTOS GPIO - MODO INTERATIVO")
    print("="*70)
    print("\nEste simulador permite testar o sistema sem hardware GPIO")
    print("\nComandos:")
    print("  1 - Simular botão canal 1")
    print("  2 - Simular botão canal 2")
    print("  c - Escolher canal personalizado")
    print("  t - Escolher timestamp personalizado")
    print("  q - Sair")
    print("="*70)
    
    while True:
        print()
        cmd = input("Digite um comando (1/2/c/t/q): ").strip().lower()
        
        if cmd == 'q':
            print("\n👋 Saindo...")
            break
        
        elif cmd == '1':
            trigger_download(channel=1)
        
        elif cmd == '2':
            trigger_download(channel=2)
        
        elif cmd == 'c':
            try:
                channel = int(input("Digite o número do canal (0-63): "))
                if 0 <= channel <= 63:
                    trigger_download(channel=channel)
                else:
                    print("❌ Canal deve estar entre 0 e 63")
            except ValueError:
                print("❌ Valor inválido")
        
        elif cmd == 't':
            try:
                channel = int(input("Digite o canal (0-63): "))
                timestamp = input("Digite o timestamp (YYYY-MM-DD HH:MM:SS): ")
                
                # Valida formato
                datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                
                trigger_download(channel=channel, timestamp=timestamp)
            except ValueError as e:
                print(f"❌ Erro: {e}")
        
        else:
            print("❌ Comando inválido")


def quick_test():
    """Teste rápido - dispara evento para canal 1"""
    print("\n🚀 TESTE RÁPIDO - Disparando evento para canal 1\n")
    trigger_download(channel=1)


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Simulador de eventos GPIO para testes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  
  # Modo interativo
  python3 simulator.py
  
  # Teste rápido - dispara evento canal 1
  python3 simulator.py --quick
  
  # Disparar evento específico
  python3 simulator.py --channel 1
  python3 simulator.py --channel 2 --timestamp "2026-02-18 14:30:00"
        """
    )
    
    parser.add_argument('-q', '--quick', action='store_true',
                        help='Teste rápido - dispara evento canal 1')
    parser.add_argument('-c', '--channel', type=int,
                        help='Canal para disparar evento (0-63)')
    parser.add_argument('-t', '--timestamp', type=str,
                        help='Timestamp no formato "YYYY-MM-DD HH:MM:SS"')
    
    args = parser.parse_args()
    
    # Teste rápido
    if args.quick:
        quick_test()
    
    # Comando direto
    elif args.channel is not None:
        if 0 <= args.channel <= 63:
            trigger_download(channel=args.channel, timestamp=args.timestamp)
        else:
            print("❌ Erro: Canal deve estar entre 0 e 63")
            sys.exit(1)
    
    # Modo interativo (padrão)
    else:
        interactive_mode()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
