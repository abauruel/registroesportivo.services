#!/usr/bin/env python3
"""
Verifica se o worker pode ser executado do diretório atual
"""
import sys
import os

current_dir = os.getcwd()
expected_dir = "/home/abauruel/www/onvif_learn/RE/app"

print("\n" + "="*70)
print("🔍 VERIFICAÇÃO DE AMBIENTE PARA RQ WORKER")
print("="*70)

print(f"\n📂 Diretório atual: {current_dir}")
print(f"📂 Diretório esperado: {expected_dir}")

if current_dir == expected_dir:
    print("\n✅ Você está no diretório correto!")
else:
    print(f"\n❌ ERRO: Você está no diretório errado!")
    print(f"\n💡 Solução: Execute os seguintes comandos:")
    print(f"   cd {expected_dir}")
    print(f"   ./start_worker.sh download_queue")
    print("="*70)
    sys.exit(1)

# Testa importação
print("\n🔬 Testando importação do módulo...")

sys.path.insert(0, current_dir)

try:
    import services.download_service
    print("✅ Módulo 'services.download_service' importado com sucesso!")
    
    # Testa função
    if hasattr(services.download_service, 'download_video'):
        print("✅ Função 'download_video' encontrada!")
    else:
        print("❌ ERRO: Função 'download_video' não encontrada!")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ ERRO ao importar módulo: {e}")
    print("\n💡 Certifique-se que:")
    print("   1. Você está no diretório /home/abauruel/www/onvif_learn/RE/app")
    print("   2. A pasta services/ existe e tem __init__.py")
    print("   3. O arquivo services/download_service.py existe")
    print("="*70)
    sys.exit(1)

# Verifica Redis
print("\n📡 Testando conexão com Redis...")
try:
    import redis
    import config
    
    r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    r.ping()
    print(f"✅ Redis conectado! ({config.REDIS_HOST}:{config.REDIS_PORT})")
    
except ImportError:
    print("❌ Módulo 'redis' não instalado")
    print("   pip install redis rq")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro ao conectar no Redis: {e}")
    print("   Certifique-se que o Redis está rodando:")
    print("   podman compose up -d redis")
    sys.exit(1)

print("\n" + "="*70)
print("✅ TUDO OK! PODE EXECUTAR O WORKER COM SEGURANÇA")
print("="*70)
print("\n🚀 Execute:")
print("   ./start_worker.sh download_queue")
print("\nOu manualmente:")
print(f"   ../.venv/bin/rq worker download_queue")
print("="*70 + "\n")
