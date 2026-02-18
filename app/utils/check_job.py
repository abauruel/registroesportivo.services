#!/usr/bin/env python3
"""
Verifica status e erro de jobs no Redis
"""
import sys
import redis
from rq import Queue
from rq.job import Job
import config

# Conecta ao Redis
redis_conn = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)

def check_job(job_id):
    """Verifica detalhes de um job específico"""
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        
        print("\n" + "="*70)
        print(f"📋 Job Details: {job_id}")
        print("="*70)
        print(f"Status: {job.get_status()}")
        print(f"Description: {job.description}")
        print(f"Created: {job.created_at}")
        print(f"Started: {job.started_at}")
        print(f"Ended: {job.ended_at}")
        print(f"Queue: {job.origin}")
        
        if job.is_failed:
            print("\n❌ JOB FAILED")
            print("-"*70)
            if job.exc_info:
                print(job.exc_info)
            else:
                print("No exception info available")
                
        elif job.is_finished:
            print("\n✅ JOB COMPLETED")
            print(f"Result: {job.result}")
            
        print("="*70)
        
    except Exception as e:
        print(f"❌ Erro ao buscar job: {e}")

def list_failed_jobs():
    """Lista jobs que falharam"""
    queue = Queue('download_queue', connection=redis_conn)
    
    print("\n" + "="*70)
    print("📋 Failed Jobs Registry")
    print("="*70)
    
    from rq.registry import FailedJobRegistry
    registry = FailedJobRegistry(queue=queue, connection=redis_conn)
    
    failed_job_ids = registry.get_job_ids()
    print(f"Total: {len(failed_job_ids)} jobs failed")
    print()
    
    for job_id in failed_job_ids[:10]:  # Mostra primeiros 10
        job = Job.fetch(job_id, connection=redis_conn)
        print(f"  ID: {job_id}")
        print(f"  Description: {job.description}")
        print(f"  Failed at: {job.ended_at}")
        
        if job.exc_info:
            print(f"  Error (first 200 chars):\n    {job.exc_info[:200]}...")
        print()
    
    print("="*70)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Verifica job específico
        job_id = sys.argv[1]
        check_job(job_id)
    else:
        # Lista jobs falhados
        list_failed_jobs()
