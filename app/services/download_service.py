import requests
import os
import sys
from datetime import datetime
from config import *
import redis
from rq import Queue
from video_processor import process_video
from .jftecth_integration import main as jftech_main

redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
upload_queue = Queue(UPLOAD_QUEUE, connection=redis_conn)

def download_video(timestamp=None, channel=0):
    """
    Faz download de vídeo do NVR usando JFTech SDK.
    
    Args:
        timestamp (str): Data e hora no formato "YYYY-MM-DD HH:MM:SS"
                        Se None, usa a hora atual
        channel (int): Número do canal (0-63, padrão=0)
    """
    print("Iniciando download...")
    
    # Se timestamp não foi fornecido, usa hora atual
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Valida formato do timestamp
    try:
        datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print(f"Erro: Formato de timestamp inválido: '{timestamp}'")
        print("Formato esperado: YYYY-MM-DD HH:MM:SS")
        print("Exemplo: '2026-02-18 14:30:00'")
        return
    
    # Salva sys.argv original
    original_argv = sys.argv.copy()
    
    filename = None
    
    try:
        # Modifica sys.argv para passar parâmetros para jftech_main
        sys.argv = ['jftech_integration.py', str(channel), timestamp]
        
        # Executa a função main do jftech_integration e recebe o caminho do arquivo
        filename = jftech_main()
        
    finally:
        # Restaura sys.argv original
        sys.argv = original_argv
    
    # Verifica se o download foi bem-sucedido
    if filename and os.path.exists(filename):
        print(f"\n{'='*60}")
        print(f"✅ Download concluído com sucesso!")
        print(f"{'='*60}")
        print(f"   Arquivo: {filename}")
        print(f"   Tamanho: {os.path.getsize(filename)} bytes")
        print(f"{'='*60}\n")
        
        # Processamento opcional
        process_video(filename)
        
        # Enfileira upload
        print(f"\n{'='*60}")
        print(f"📤 Enfileirando upload do arquivo: {filename}")
        upload_job = upload_queue.enqueue("services.upload_service.upload_video", filename)
        print(f"   Upload Job ID: {upload_job.id}")
        print(f"   Status inicial: {upload_job.get_status()}")
        print(f"   Fila: {UPLOAD_QUEUE}")
        print(f"{'='*60}\n")
        
        return filename
    else:
        print(f"\n{'='*60}")
        print(f"❌ Download falhou!")
        print(f"{'='*60}")
        if filename:
            print(f"   Arquivo esperado: {filename}")
            print(f"   Arquivo existe? {os.path.exists(filename)}")
            print(f"   Motivo: Arquivo não foi criado pelo SDK")
        else:
            print(f"   Motivo: SDK retornou None (erro no download)")
        print(f"   ⚠️  Upload NÃO foi enfileirado")
        print(f"{'='*60}\n")
        return None
