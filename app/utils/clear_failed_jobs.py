#!/usr/bin/env python3
"""
Limpa jobs falhados do Redis
"""
import redis
from rq import Queue
from rq.registry import FailedJobRegistry
import config

# Conecta ao Redis
redis_conn = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
queue = Queue('download_queue', connection=redis_conn)
registry = FailedJobRegistry(queue=queue, connection=redis_conn)

print("\n" + "="*70)
print("🧹 Limpando Jobs Falhados")
print("="*70)

failed_job_ids = registry.get_job_ids()
print(f"Total de jobs falhados: {len(failed_job_ids)}")

if failed_job_ids:
    print("\nRemovendo jobs falhados...")
    for job_id in failed_job_ids:
        registry.remove(job_id, delete_job=True)
        print(f"  ✓ Removido: {job_id}")
    
    print(f"\n✅ {len(failed_job_ids)} jobs removidos com sucesso!")
else:
    print("\n✅ Nenhum job falhado encontrado")

print("="*70)
