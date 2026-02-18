import requests
import os
from config import *

def upload_video(file_path):
    print("Iniciando upload externo...")

    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(API_UPLOAD_URL, files=files, timeout=60)

        if response.status_code in [200, 201]:
            print("Upload concluído com sucesso.")
            
            # Remove arquivo após sucesso
            os.remove(file_path)
            print("Arquivo removido:", file_path)
        else:
            print("Erro no upload:", response.status_code)
            raise Exception("Upload falhou")

    except Exception as e:
        print("Falha no upload:", e)
        raise  # permite retry automático do RQ
