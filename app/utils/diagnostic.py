#!/usr/bin/env python
"""
Script de diagnóstico completo do sistema
"""
import os
import sys
import redis
from rq import Queue

# Cores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_redis():
    """Verifica se Redis está rodando"""
    from config import REDIS_HOST, REDIS_PORT
    
    print(f"\n{BLUE}1. Redis{RESET}")
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        r.ping()
        print(f"   {GREEN}✅ Redis conectado{RESET} ({REDIS_HOST}:{REDIS_PORT})")
        return True
    except Exception as e:
        print(f"   {RED}❌ Redis não conectado{RESET}")
        print(f"      Erro: {e}")
        print(f"      Solução: podman start redis_edge")
        return False

def check_directories():
    """Verifica diretórios necessários"""
    print(f"\n{BLUE}2. Diretórios{RESET}")
    
    dirs = ['videos', 'downloads']
    all_ok = True
    
    for d in dirs:
        if os.path.exists(d):
            print(f"   {GREEN}✅ {d}/{RESET} existe")
        else:
            print(f"   {YELLOW}⚠️  {d}/{RESET} não existe")
            print(f"      Solução: mkdir -p {d}")
            all_ok = False
    
    return all_ok

def check_env_file():
    """Verifica arquivo .env"""
    print(f"\n{BLUE}3. Configuração (.env){RESET}")
    
    from config import NVR_IP, NVR_USERNAME, NVR_PASSWORD
    
    if NVR_IP and NVR_USERNAME and NVR_PASSWORD:
        print(f"   {GREEN}✅ Credenciais configuradas{RESET}")
        print(f"      NVR IP: {NVR_IP}")
        print(f"      Usuário: {NVR_USERNAME}")
        print(f"      Senha: {'*' * len(NVR_PASSWORD)}")
        return True
    else:
        print(f"   {RED}❌ Credenciais incompletas{RESET}")
        print(f"      Verifique arquivo .env")
        return False

def check_queues():
    """Verifica filas Redis"""
    print(f"\n{BLUE}4. Filas{RESET}")
    
    from config import REDIS_HOST, REDIS_PORT, DOWNLOAD_QUEUE, UPLOAD_QUEUE
    
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        
        download_q = Queue(DOWNLOAD_QUEUE, connection=r)
        upload_q = Queue(UPLOAD_QUEUE, connection=r)
        
        print(f"   {GREEN}download_queue:{RESET}")
        print(f"      Aguardando: {len(download_q)}")
        print(f"      Em execução: {len(download_q.started_job_registry)}")
        print(f"      Concluídos: {len(download_q.finished_job_registry)}")
        print(f"      Falhas: {len(download_q.failed_job_registry)}")
        
        print(f"\n   {GREEN}upload_queue:{RESET}")
        print(f"      Aguardando: {len(upload_q)}")
        print(f"      Em execução: {len(upload_q.started_job_registry)}")
        print(f"      Concluídos: {len(upload_q.finished_job_registry)}")
        print(f"      Falhas: {len(upload_q.failed_job_registry)}")
        
        return True
    except Exception as e:
        print(f"   {RED}❌ Erro ao consultar filas{RESET}")
        print(f"      Erro: {e}")
        return False

def check_api():
    """Verifica se API está rodando"""
    print(f"\n{BLUE}5. Producer API{RESET}")
    
    try:
        import requests
        response = requests.get('http://localhost:5000/health', timeout=2)
        if response.status_code == 200:
            print(f"   {GREEN}✅ API rodando{RESET} (http://localhost:5000)")
            data = response.json()
            print(f"      Status: {data.get('status')}")
            return True
        else:
            print(f"   {YELLOW}⚠️  API retornou status {response.status_code}{RESET}")
            return False
    except Exception as e:
        print(f"   {RED}❌ API não está rodando{RESET}")
        print(f"      Solução: ../.venv/bin/python services/producer_service.py")
        return False

def check_recent_downloads():
    """Verifica downloads recentes"""
    print(f"\n{BLUE}6. Arquivos Baixados (últimos 5){RESET}")
    
    videos_dir = 'videos'
    if os.path.exists(videos_dir):
        files = sorted(
            [f for f in os.listdir(videos_dir) if f.endswith('.mp4')],
            key=lambda x: os.path.getmtime(os.path.join(videos_dir, x)),
            reverse=True
        )[:5]
        
        if files:
            for f in files:
                path = os.path.join(videos_dir, f)
                size = os.path.getsize(path)
                print(f"   {GREEN}•{RESET} {f} ({size} bytes)")
            return True
        else:
            print(f"   {YELLOW}⚠️  Nenhum arquivo .mp4 no diretório videos/{RESET}")
            return False
    else:
        print(f"   {YELLOW}⚠️  Diretório videos/ não existe{RESET}")
        return False

def main():
    print("="*70)
    print("🔍 DIAGNÓSTICO DO SISTEMA DE DOWNLOAD")
    print("="*70)
    
    checks = [
        check_redis(),
        check_directories(),
        check_env_file(),
        check_queues(),
        check_api(),
        check_recent_downloads()
    ]
    
    print("\n" + "="*70)
    print("📊 RESUMO")
    print("="*70)
    
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"{GREEN}✅ Todos os checks passaram ({passed}/{total}){RESET}")
        print(f"\n{GREEN}Sistema pronto para uso!{RESET}")
        print(f"\nPara disparar um evento:")
        print(f"   curl -X POST http://localhost:5000/trigger/0")
    else:
        print(f"{YELLOW}⚠️  {passed}/{total} checks passaram{RESET}")
        print(f"\n{YELLOW}Verifique os itens marcados com ❌ acima{RESET}")
    
    print("="*70)

if __name__ == "__main__":
    main()
