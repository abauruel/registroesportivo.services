import os
from datetime import datetime
from zoneinfo import ZoneInfo

API_UPLOAD_URL = "https://api.externa.com/upload"

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

DOWNLOAD_QUEUE = "download_queue"
UPLOAD_QUEUE = "upload_queue"

VIDEO_STORAGE_PATH = "/home/pi/videos/"

APP_TIMEZONE = os.getenv("APP_TIMEZONE", os.getenv("TZ", "America/Sao_Paulo"))


def now_local():
	"""Retorna datetime atual no fuso configurado (fallback para horário local do sistema)."""
	try:
		return datetime.now(ZoneInfo(APP_TIMEZONE))
	except Exception:
		return datetime.now()


def now_timestamp():
	"""Retorna timestamp no formato padrão do projeto."""
	return now_local().strftime("%Y-%m-%d %H:%M:%S")


NVR_IP="192.168.1.66"
NVR_PORT=34567
NVR_USERNAME="service"
NVR_PASSWORD=""