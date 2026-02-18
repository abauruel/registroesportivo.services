#!/usr/bin/env python3
"""
Teste End-to-End completo
Enfileira job, executa worker, e verifica resultado
"""
import sys
import os
import time
import signal
import redis
from rq import Queue
from rq.job import Job
import config

# Conecta ao Redis
redis_conn = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
queue = Queue('download_queue', connection=redis_conn)

def test_complete_flow():
    print("\n" + "="*70)
    print("🧪 TESTE END-TO-END COMPLETO")
    print("="*70)
    
    # Passo 1: Enfileira job
    print("\n📤 [1/4] Enfileirando job de teste...")
    timestamp = "2026-02-18 16:00:00"
    channel = 1
    
    job = queue.enqueue(
        'services.download_service.download_video',
        timestamp=timestamp,
        channel=channel,
        timeout=180
    )
    
    print(f"  ✓ Job ID: {job.id}")
    print(f"  ✓ Status: {job.get_status()}")
    print(f"  ✓ Description: {job.description}")
    
    # Passo 2: Avisa sobre worker
    print("\n⚙️  [2/4] Iniciar worker em outro terminal:")
    print(f"  cd /home/abauruel/www/onvif_learn/RE/app")
    print(f"  ./start_worker.sh download_queue")
    
    # Passo 3: Aguarda processamento
    print("\n⏳ [3/4] Aguardando processamento (máx 30s)...")
    
    for i in range(30):
        job.refresh()
        status = job.get_status()
        
        if status in ['finished', 'failed']:
            break
        
        if i % 5 == 0:
            print(f"  ... {i}s - Status: {status}")
        
        time.sleep(1)
    
    # Passo 4: Verifica resultado
    print("\n📊 [4/4] Resultado:")
    print("-"*70)
    
    job.refresh()
    final_status = job.get_status()
    
    print(f"  Status Final: {final_status}")
    print(f"  Criado: {job.created_at}")
    print(f"  Iniciado: {job.started_at}")
    print(f"  Finalizado: {job.ended_at}")
    
    if job.is_finished:
        print(f"\n  ✅ JOB COMPLETADO COM SUCESSO!")
        print(f"  Resultado: {job.result}")
        
    elif job.is_failed:
        print(f"\n  ❌ JOB FALHOU")
        if job.exc_info:
            print(f"\n  Erro:\n{job.exc_info}")
        
    else:
        print(f"\n  ⚠️  Job ainda não processado - Status: {final_status}")
        print(f"  Certifique-se que o worker está rodando!")
    
    print("="*70)
    
    return job.is_finished

if __name__ == "__main__":
    try:
        success = test_complete_flow()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Teste interrompido")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
