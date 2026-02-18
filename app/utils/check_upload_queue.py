#!/usr/bin/env python
"""
Script para verificar a fila de upload no Redis
"""
import redis
from rq import Queue
from rq.job import Job
from config import REDIS_HOST, REDIS_PORT, UPLOAD_QUEUE

# Conecta ao Redis
redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
upload_queue = Queue(UPLOAD_QUEUE, connection=redis_conn)

print("="*70)
print(f"📊 STATUS DA FILA DE UPLOAD: {UPLOAD_QUEUE}")
print("="*70)

# Informações da fila
print(f"\n📋 Informações gerais:")
print(f"   Jobs na fila (aguardando): {len(upload_queue)}")
print(f"   Jobs em execução: {len(upload_queue.started_job_registry)}")
print(f"   Jobs finalizados: {len(upload_queue.finished_job_registry)}")
print(f"   Jobs com falha: {len(upload_queue.failed_job_registry)}")

# Lista jobs na fila (aguardando processamento)
if len(upload_queue) > 0:
    print(f"\n⏳ Jobs aguardando na fila:")
    for job in upload_queue.jobs:
        print(f"   • Job ID: {job.id}")
        print(f"     Função: {job.func_name}")
        print(f"     Args: {job.args}")
        print(f"     Status: {job.get_status()}")
        print(f"     Criado em: {job.created_at}")
        print()

# Lista jobs em execução
started_jobs = upload_queue.started_job_registry.get_job_ids()
if started_jobs:
    print(f"\n⚙️  Jobs em execução:")
    for job_id in started_jobs:
        try:
            job = Job.fetch(job_id, connection=redis_conn)
            print(f"   • Job ID: {job.id}")
            print(f"     Função: {job.func_name}")
            print(f"     Args: {job.args}")
            print(f"     Iniciado em: {job.started_at}")
            print()
        except:
            pass

# Lista últimos jobs finalizados (máximo 5)
finished_jobs = upload_queue.finished_job_registry.get_job_ids(0, 4)
if finished_jobs:
    print(f"\n✅ Últimos jobs finalizados:")
    for job_id in finished_jobs:
        try:
            job = Job.fetch(job_id, connection=redis_conn)
            print(f"   • Job ID: {job.id}")
            print(f"     Função: {job.func_name}")
            print(f"     Args: {job.args}")
            print(f"     Resultado: {job.result}")
            print(f"     Concluído em: {job.ended_at}")
            print()
        except:
            pass

# Lista jobs com falha
failed_jobs = upload_queue.failed_job_registry.get_job_ids()
if failed_jobs:
    print(f"\n❌ Jobs com falha:")
    for job_id in failed_jobs:
        try:
            job = Job.fetch(job_id, connection=redis_conn)
            print(f"   • Job ID: {job.id}")
            print(f"     Função: {job.func_name}")
            print(f"     Args: {job.args}")
            print(f"     Erro: {job.exc_info}")
            print()
        except:
            pass

print("="*70)
