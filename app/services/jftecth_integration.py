#!/usr/bin/env python3
"""
JFTech XCloudSDK Python Wrapper - v1.1
Exemplo de uso do SDK nativo da JFTech para acessar gravações do NVR

Funcionalidades:
- Login em dispositivos JFTech/XMEye NVR
- Busca de gravações por canal e período de tempo (últimos 15 segundos)
- Download de gravações em formato H.264 raw

Uso:
    python3 jftech_sdk_example.py [canal] [data_hora]
    
Argumentos:
    canal: Número do canal (0-63, padrão=0)
    data_hora: Data e hora no formato "YYYY-MM-DD HH:MM:SS" (padrão=agora)
    
Exemplo:
    python3 jftech_sdk_example.py 1 "2026-01-08 14:30:00"
    python3 jftech_sdk_example.py 1  # Usa hora atual
"""

import ctypes
import json
import os
import time
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Caminho para a biblioteca
SDK_PATH = "./lib/libXCloudSDK.so"

# Tipos de callback
PXSDK_MessageCallBack = ctypes.CFUNCTYPE(
    ctypes.c_int,  # return type
    ctypes.c_void_p,  # hObject
    ctypes.c_int,  # nMsgId
    ctypes.c_int,  # nParam1
    ctypes.c_int,  # nParam2
    ctypes.c_int,  # nParam3
    ctypes.c_char_p,  # szString
    ctypes.c_void_p,  # pObject
    ctypes.c_int64,  # lParam
    ctypes.c_int,  # nSeq
    ctypes.c_void_p,  # pUserData
    ctypes.c_void_p,  # pMsg
)

# Message IDs do SDK
ESXSDK_DEV_LOGIN = 12001
ESXSDK_ON_DEV_STATE = 12020
ESXSDK_DEV_FIND_FILE = 12011  # ID antigo
ESXSDK_DEV_FIND_FILE_RESULT = 12105  # ID real do resultado
ESXSDK_MEDIA_START_RECORD_PLAY = 12003
ESXSDK_MEDIA_DOWN_RECORD_FILE = 12004
EXSDK_DATA_MEDIA_ON_PLAY_STATE = 1010
EXCMD_DOWNLOAD_DATA = 1020  # Não usado neste SDK
EMSG_DOWNLOAD_DATA_CHUNK = 1426  # REAL message ID para chunks de download! (0x0592)
                                 # Cada chunk tem ~32KB (32768 bytes)
                                 # Descoberto através de logging de todos os callbacks
ESXSDK_DEV_SET_SYS_CONFIG = 12102  # Sincronização de tempo e configuração do sistema
# Estado de mídia
EState_Media_DataEnd = 0
EState_Media_NetDisConnect = 1

# Códigos de erro conhecidos
ERROR_CODES = {
    -70119: "Sem gravações no período ou canal inativo",
    -70136: "Comando não suportado",
    -10: "Arquivo não encontrado",
    100: "Sucesso",
    119: "Sem gravações no período"
}


class XCloudSDK:
    """Wrapper Python para o XCloudSDK da JFTech"""

    def __init__(self, sdk_path: str = SDK_PATH):
        """Inicializa o SDK"""
        self.sdk = ctypes.CDLL(sdk_path)
        self.h_user = 0
        self.login_handle = 0
        self.is_logged_in = False
        self.recordings = []
        self.callback_func = None
        self.download_file = None
        self.download_bytes = 0
        self.download_progress = 0  # Progresso 0-100 quando usar SaveFileName
        self.download_completed = False  # Flag de conclusão
        
        # Define as assinaturas das funções
        self._setup_function_signatures()
        
    def _setup_function_signatures(self):
        """Define os tipos de retorno e argumentos das funções do SDK"""
        
        # XCloudSDK_Init
        self.sdk.XCloudSDK_Init.argtypes = [ctypes.c_char_p]
        self.sdk.XCloudSDK_Init.restype = ctypes.c_int
        
        # XCloudSDK_UnInit
        self.sdk.XCloudSDK_UnInit.argtypes = []
        self.sdk.XCloudSDK_UnInit.restype = None
        
        # XCloudSDK_SetLogTypeAndLevel
        self.sdk.XCloudSDK_SetLogTypeAndLevel.argtypes = [ctypes.c_int, ctypes.c_int]
        self.sdk.XCloudSDK_SetLogTypeAndLevel.restype = None
        
        # XCloudSDK_RegisterCallback
        self.sdk.XCloudSDK_RegisterCallback.argtypes = [PXSDK_MessageCallBack, ctypes.c_void_p]
        self.sdk.XCloudSDK_RegisterCallback.restype = ctypes.c_int
        
        # XCloudSDK_UnRegister
        self.sdk.XCloudSDK_UnRegister.argtypes = [ctypes.c_int]
        self.sdk.XCloudSDK_UnRegister.restype = None
        
        # XCloudSDK_Device_SetLocalUserNameAndPwd
        self.sdk.XCloudSDK_Device_SetLocalUserNameAndPwd.argtypes = [
            ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p
        ]
        self.sdk.XCloudSDK_Device_SetLocalUserNameAndPwd.restype = ctypes.c_int
        
        # XCloudSDK_Device_DevLogin
        self.sdk.XCloudSDK_Device_DevLogin.argtypes = [
            ctypes.c_int, ctypes.c_char_p, ctypes.c_int
        ]
        self.sdk.XCloudSDK_Device_DevLogin.restype = ctypes.c_int
        
        # XCloudSDK_Device_DevLogout
        self.sdk.XCloudSDK_Device_DevLogout.argtypes = [ctypes.c_char_p]
        self.sdk.XCloudSDK_Device_DevLogout.restype = ctypes.c_int
        
        # XCloudSDK_Device_FindRecordFile
        self.sdk.XCloudSDK_Device_FindRecordFile.argtypes = [
            ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int
        ]
        self.sdk.XCloudSDK_Device_FindRecordFile.restype = ctypes.c_int
        
        # XCloudSDK_Device_MediaRecordPlayByTime
        self.sdk.XCloudSDK_Device_MediaRecordPlayByTime.argtypes = [
            ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_int
        ]
        self.sdk.XCloudSDK_Device_MediaRecordPlayByTime.restype = ctypes.c_int
        
        # XCloudSDK_Device_MediaRecordDownloadByTime
        self.sdk.XCloudSDK_Device_MediaRecordDownloadByTime.argtypes = [
            ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int
        ]
        self.sdk.XCloudSDK_Device_MediaRecordDownloadByTime.restype = ctypes.c_int
        
        # XCloudSDK_Device_StopMediaPlay
        self.sdk.XCloudSDK_Device_StopMediaPlay.argtypes = [ctypes.c_int]
        self.sdk.XCloudSDK_Device_StopMediaPlay.restype = ctypes.c_int
        
        # XCloudSDK_Device_DevSynTime
        self.sdk.XCloudSDK_Device_DevSynTime.argtypes = [
            ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int
        ]
        self.sdk.XCloudSDK_Device_DevSynTime.restype = ctypes.c_int
    
    def _message_callback(self, hObject, nMsgId, nParam1, nParam2, nParam3,
                          szString, pObject, lParam, nSeq, pUserData, pMsg):
        """Callback para mensagens do SDK"""
        
        # Log apenas para debug de download (remover depois)
        # if nMsgId == EMSG_DOWNLOAD_DATA_CHUNK:
        #     print(f"🔔 CHUNK: {nParam1} bytes")
        
        if nMsgId == ESXSDK_DEV_LOGIN:
            if nParam1 >= 0:
                print(f"✓ Login bem-sucedido")
                self.is_logged_in = True
            else:
                print(f"✗ Login falhou: erro {nParam1}")
                self.is_logged_in = False
                
        elif nMsgId == ESXSDK_DEV_FIND_FILE or nMsgId == ESXSDK_DEV_FIND_FILE_RESULT:
            if nParam1 >= 0 and pObject:
                # Parse JSON com informações das gravações
                json_str = ctypes.string_at(pObject).decode('utf-8')
                try:
                    data = json.loads(json_str)
                    if "OPFileQuery" in data:
                        recordings = data["OPFileQuery"]
                        if isinstance(recordings, list):
                            self.recordings = recordings
                            print(f"✓ Encontradas {len(recordings)} gravações")
                            for i, rec in enumerate(recordings, 1):
                                filename = rec.get("FileName", "")
                                start_time = rec.get("StartTime", "")
                                end_time = rec.get("EndTime", "")
                                size = rec.get("Length", 0)
                                print(f"  [{i}] {filename}")
                                print(f"      Início: {start_time}, Fim: {end_time}, Tamanho: {size} bytes")
                except json.JSONDecodeError as e:
                    print(f"✗ Erro ao parsear JSON: {e}")
            else:
                # Erro ao buscar gravações
                error_code = nParam1 if nParam1 < 0 else -nParam1
                error_msg = ERROR_CODES.get(error_code, f"Erro desconhecido: {error_code}")
                print(f"! Nenhuma gravação encontrada")
                print(f"  Código: {error_code} - {error_msg}")
                print(f"  Possíveis causas:")
                print(f"    • Canal sem câmera conectada")
                print(f"    • Canal desabilitado no NVR")
                print(f"    • Sem gravações no período especificado")
                print(f"    • Verifique canais disponíveis: 0-15 (seu NVR tem 16 canais)")
                
        elif nMsgId == ESXSDK_MEDIA_START_RECORD_PLAY:
            if nParam1 >= 0:
                print(f"✓ Reprodução de gravação iniciada")
            else:
                print(f"✗ Falha ao iniciar reprodução: {nParam1}")
                
        elif nMsgId == ESXSDK_MEDIA_DOWN_RECORD_FILE:
            if nParam1 >= 0:
                print(f"✓ Download de gravação iniciado")
            else:
                print(f"✗ Falha ao iniciar download: {nParam1}")
                
        elif nMsgId == EXSDK_DATA_MEDIA_ON_PLAY_STATE:
            if nParam1 == EState_Media_DataEnd:
                if nParam2 >= 0:
                    print(f"\n✓ Download/Reprodução concluído com sucesso")
                    if self.download_file:
                        print(f"  Total de {self.download_bytes} bytes baixados")
                        self.download_file.close()
                        self.download_file = None
                    self.download_completed = True  # Marca como concluído
                else:
                    print(f"\n✗ Download/Reprodução falhou: {nParam2}")
                    if self.download_file:
                        self.download_file.close()
                        self.download_file = None
                    self.download_completed = True  # Marca como concluído (com erro)
            elif nParam1 == EState_Media_NetDisConnect:
                print(f"\n! Canal de mídia desconectado")
                if self.download_file:
                    self.download_file.close()
                    self.download_file = None
                self.download_completed = True  # Marca como concluído (desconectado)
        
        elif nMsgId == EXCMD_DOWNLOAD_DATA:
            # Salvar dados do download (ID 1020 - não usado neste SDK)
            if pObject and nParam1 > 0:
                try:
                    if self.download_file:
                        # Ler dados do ponteiro
                        data = ctypes.string_at(pObject, nParam1)
                        self.download_file.write(data)
                        self.download_bytes += len(data)
                        # Mostrar progresso a cada 100KB
                        if self.download_bytes % 102400 < nParam1:
                            print(f"  Baixados: {self.download_bytes / 1024:.1f} KB", end='\r')
                except Exception as e:
                    print(f"❌ Erro ao salvar dados (1020): {e}")
        
        elif nMsgId == EMSG_DOWNLOAD_DATA_CHUNK:
            # REAL message ID para download (1426 = 0x0592)
            # Quando SaveFileName especificado: nParam1 = progresso 0-100
            # Quando SaveFileName vazio: nParam1 = data length, pObject = data
            
            if self.download_file is None:
                # Modo SaveFileName: SDK salva arquivo, exibir progresso
                progress = nParam1
                if progress != self.download_progress:
                    self.download_progress = progress
                    print(f"  📥 Progresso: {progress}%", end='\r')
                    if progress == 100:
                        print()  # Nova linha ao completar
                        self.download_completed = True  # Marca como concluído!
            else:
                # Modo manual (legado): salvar dados via callback
                if nParam1 > 0 and pObject:
                    try:
                        # nParam1 é o tamanho do chunk (geralmente 32768 bytes = 32 KB)
                        data = ctypes.string_at(pObject, nParam1)
                        self.download_file.write(data)
                        self.download_bytes += len(data)
                        # Mostrar progresso a cada 500KB
                        if self.download_bytes % (500 * 1024) < nParam1:
                            print(f"📦 Baixados: {self.download_bytes / 1024:.1f} KB")
                    except Exception as e:
                        print(f"❌ Erro ao salvar dados (1426): {e}")
                        import traceback
                        traceback.print_exc()
        
        elif nMsgId == ESXSDK_DEV_SET_SYS_CONFIG:
            # Sincronização de tempo e configuração do sistema
            if nParam1 >= 0:
                print(f"✓ Sincronização de tempo bem-sucedida")
            else:
                print(f"✗ Falha ao sincronizar tempo: erro {nParam1}")
                
        return 0
    
    def initialize(self, config: Optional[dict] = None):
        """Inicializa o SDK com configuração"""
        if config is None:
            config = {
                "SaveFileType": "mp4",
                "CFG_KEY_Language": "en"
            }
        
        config_json = json.dumps(config).encode('utf-8')
        result = self.sdk.XCloudSDK_Init(config_json)
        
        if result >= 0:
            # Habilita logs (2=arquivo, 1=debug level)
            self.sdk.XCloudSDK_SetLogTypeAndLevel(1, 1)  # 1=console, 1=debug
            
            # Registra callback
            self.callback_func = PXSDK_MessageCallBack(self._message_callback)
            self.h_user = self.sdk.XCloudSDK_RegisterCallback(self.callback_func, None)
            
            print(f"✓ SDK inicializado (handle: {self.h_user})")
            return True
        else:
            print(f"✗ Falha ao inicializar SDK: {result}")
            return False
    
    def set_device_credentials(self, device_id: str, username: str, password: str):
        """Configura credenciais do dispositivo no cache local"""
        result = self.sdk.XCloudSDK_Device_SetLocalUserNameAndPwd(
            device_id.encode('utf-8'),
            username.encode('utf-8'),
            password.encode('utf-8')
        )
        if result == 0:
            print(f"✓ Credenciais configuradas para {device_id}")
            return True
        else:
            print(f"✗ Falha ao configurar credenciais: {result}")
            return False
    
    def login_device(self, device_id: str):
        """Faz login no dispositivo"""
        result = self.sdk.XCloudSDK_Device_DevLogin(
            self.h_user,
            device_id.encode('utf-8'),
            0  # nSeq
        )
        
        if result >= 0:
            print(f"⏳ Aguardando login em {device_id}...")
            # Aguarda callback de login
            import time
            for _ in range(10):  # Timeout de 10 segundos
                time.sleep(1)
                if self.is_logged_in:
                    print(f"ℹ️  Dispositivo tem 16 canais (0-15)")
                    break
            if not self.is_logged_in:
                print(f"✗ Login no NVR não foi concluído para {device_id}")
                print("  Possíveis causas:")
                print("    • Usuário/senha inválidos")
                print("    • Porta/protocolo do NVR incorretos")
                print("    • Usuário sem permissão para acesso remoto")
                print("  Verifique NVR_IP, NVR_PORT, NVR_USERNAME e NVR_PASSWORD")
            return self.is_logged_in
        else:
            print(f"✗ Falha ao iniciar login: {result}")
            return False
    
    def find_recordings(self, device_id: str, channel: int,
                       start_time: str, end_time: str):
        """
        Busca gravações no dispositivo
        
        Args:
            device_id: ID do dispositivo (SN ou IP:Port)
            channel: Número do canal (0-63)
            start_time: Hora inicial (formato: "2024-01-08 00:00:00")
            end_time: Hora final (formato: "2024-01-08 23:59:59")
        """
        self.recordings = []
        
        params = {
            "BeginTime": start_time,
            "EndTime": end_time,
            "Channel": channel,
            "DriverTypeMask": "0x0000FFFF",  # Todos os tipos de drive
            "Event": "*",  # Todos os eventos
            "StreamType": "0x00000000",  # Main stream
            "Type": "h264"
        }
        
        params_json = json.dumps(params).encode('utf-8')
        
        result = self.sdk.XCloudSDK_Device_FindRecordFile(
            self.h_user,
            device_id.encode('utf-8'),
            params_json,
            0  # nSeq
        )
        
        if result >= 0:
            print(f"⏳ Buscando gravações...")
            # Aguarda callback com resultados
            import time
            time.sleep(3)  # Aguarda resposta
            return self.recordings
        else:
            print(f"✗ Falha ao buscar gravações: {result}")
            return []
    
    def download_recording(self, device_id: str, channel: int,
                          start_time: str, end_time: str,
                          output_file: str, stream_type: int = 0):
        """
        Baixa gravação do dispositivo em H.264
        
        IMPORTANTE: Usa SaveFileName com .h264 para conversão automática
        pelo SDK (apenas vídeo, sem áudio).
        
        Args:
            device_id: ID do dispositivo
            channel: Número do canal
            start_time: Hora inicial
            end_time: Hora final
            output_file: Caminho do arquivo de saída (.h264 recomendado)
            stream_type: 0=main stream, 1=sub stream
        """
        # Converter caminho para absoluto
        import os
        output_file = os.path.abspath(output_file)
        
        # Garantir que tem extensão .h264
        # if not output_file.lower().endswith('.h264'):
        #     output_file = output_file.rsplit('.', 1)[0] + '.h264'
        
        params = {
            "SaveFileName": output_file,  # SDK converte para H.264
            "Channel": channel,
            "StreamType": stream_type,
            "BeginTime": start_time,
            "EndTime": end_time,
            "FileName": ""
        }
        
        params_json = json.dumps(params).encode('utf-8')
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Resetar contadores
        self.download_file = None  # SDK gerencia o arquivo
        self.download_bytes = 0
        self.download_progress = 0
        self.download_completed = False  # Resetar flag
        
        result = self.sdk.XCloudSDK_Device_MediaRecordDownloadByTime(
            self.h_user,
            device_id.encode('utf-8'),
            params_json,
            0  # nSeq
        )
        
        if result > 0:
            print(f"✓ Download iniciado (handle: {result})")
            print(f"⏳ Baixando para {output_file}...")
            print(f"   SDK irá converter para H.264 automaticamente")
            print(f"   Formato: H.264 raw stream (apenas vídeo)")
            return result
        else:
            print(f"✗ Falha ao iniciar download: {result}")
            return 0
    
    def sync_device_time(self, device_id: str, time_str: Optional[str] = None):
        """
        Sincroniza a hora do dispositivo
        
        Args:
            device_id: ID do dispositivo (SN ou IP:Port)
            time_str: Hora para sincronizar no formato "YYYY-MM-DD HH:MM:SS"
                     Se None, usa a hora atual do sistema
        
        Returns:
            bool: True se bem-sucedido, False caso contrário
        """
        # Se não especificado, usar hora atual
        if time_str is None:
            from datetime import datetime
            time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Validar formato da hora
        try:
            # Validar se está no formato correto
            datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print(f"✗ Formato de hora inválido: {time_str}")
            print(f"  Use o formato: YYYY-MM-DD HH:MM:SS")
            print(f"  Exemplo: 2026-02-05 14:30:00")
            return False
        
        print(f"⏳ Sincronizando hora do dispositivo para: {time_str}")
        
        result = self.sdk.XCloudSDK_Device_DevSynTime(
            self.h_user,
            device_id.encode('utf-8'),
            time_str.encode('utf-8'),
            0  # nSeq
        )
        
        if result >= 0:
            print(f"✓ Comando de sincronização de hora enviado")
            return True
        else:
            print(f"✗ Falha ao enviar comando de sincronização: {result}")
            return False
    
    def logout_device(self, device_id: str):
        """Faz logout do dispositivo"""
        result = self.sdk.XCloudSDK_Device_DevLogout(device_id.encode('utf-8'))
        if result == 0:
            print(f"✓ Logout de {device_id} realizado")
            return True
        else:
            print(f"✗ Falha ao fazer logout: {result}")
            return False
    
    def cleanup(self):
        """Limpa recursos do SDK"""
        if self.h_user > 0:
            self.sdk.XCloudSDK_UnRegister(self.h_user)
        self.sdk.XCloudSDK_UnInit()
        print("✓ SDK finalizado")


def main():
    """Exemplo de uso do SDK"""
    
    # Carregar variáveis de ambiente do arquivo .env
    load_dotenv()
    
    # Configurações do NVR (via variáveis de ambiente - obrigatórias)
    NVR_IP = os.getenv("NVR_IP")
    NVR_PORT = os.getenv("NVR_PORT")
    USERNAME = os.getenv("NVR_USERNAME")
    PASSWORD = os.getenv("NVR_PASSWORD")
    
    print("JFTech XCloudSDK - Integração Python")
    print("NVR_IP:", NVR_IP)
    print("NVR_PORT:", NVR_PORT)
    print("NVR_USERNAME:", USERNAME)
    print("NVR_PASSWORD:", PASSWORD)
    # Validar variáveis obrigatórias
    missing_vars = []
    if not NVR_IP:
        missing_vars.append("NVR_IP")
    if not NVR_PORT:
        missing_vars.append("NVR_PORT")
    if not USERNAME:
        missing_vars.append("NVR_USERNAME")
    if not PASSWORD:
        missing_vars.append("NVR_PASSWORD")
    
    if missing_vars:
        print("✗ Erro: Variáveis de ambiente obrigatórias não definidas:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nDefina as variáveis de ambiente:")
        print("  export NVR_IP=\"192.168.0.168\"")
        print("  export NVR_PORT=\"34567\"")
        print("  export NVR_USERNAME=\"service\"")
        print("  export NVR_PASSWORD=\"sua_senha\"")
        return None
    
    NVR_PORT = int(NVR_PORT)
    
    # Formato do device_id para acesso direto via IP
    device_id = f"{NVR_IP}:{NVR_PORT}"
    
    # Processar argumentos de linha de comando
    import sys
    from datetime import datetime, timedelta
    
    # Argumento 1: Canal
    if len(sys.argv) > 1:
        try:
            CHANNEL = int(sys.argv[1])
            print(f"✓ Canal especificado: {CHANNEL}")
        except ValueError:
            print(f"✗ Erro: '{sys.argv[1]}' não é um número válido")
            print("Uso: python3 jftech_integration.py [canal] [data_hora]")
            print("Exemplo: python3 jftech_integration.py 1 \"2026-01-08 14:30:00\"")
            return None
    else:
        # Solicitar canal via input
        try:
            channel_input = input("Digite o número do canal (0-63, padrão=0): ").strip()
            CHANNEL = int(channel_input) if channel_input else 0
            
            if CHANNEL < 0 or CHANNEL > 63:
                print("✗ Canal deve estar entre 0 e 63")
                return None
        except ValueError:
            print("✗ Valor inválido. Usando canal 0.")
            CHANNEL = 0
        except (KeyboardInterrupt, EOFError):
            print("\n✗ Operação cancelada")
            return None
    
    # Argumento 2: Data e hora
    if len(sys.argv) > 2:
        try:
            end_time = datetime.strptime(sys.argv[2], "%Y-%m-%d %H:%M:%S")
            print(f"✓ Data/hora especificada: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        except ValueError:
            print(f"✗ Erro: formato de data/hora inválido: '{sys.argv[2]}'")
            print("Formato esperado: YYYY-MM-DD HH:MM:SS")
            print("Exemplo: \"2026-01-08 14:30:00\"")
            return None
    else:
        # Usar hora atual
        end_time = datetime.now()
        print(f"✓ Usando hora atual: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Calcular período: 15 segundos ANTES da data/hora especificada
    start_time = end_time - timedelta(seconds=15)
    
    start_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
    
    print("\n" + "=" * 60)
    print("JFTech XCloudSDK - Acesso a Gravações")
    print("=" * 60)
    print(f"Dispositivo: {device_id}")
    print(f"Usuário: {USERNAME}")
    print(f"Canal: {CHANNEL}")
    print(f"Período: {start_str} até {end_str}")
    print("=" * 60)
    
    # Inicializa SDK
    sdk = XCloudSDK()
    output_file = None
    
    try:
        # 1. Inicializar SDK
        if not sdk.initialize():
            return None
        
        # 2. Configurar credenciais
        if not sdk.set_device_credentials(device_id, USERNAME, PASSWORD):
            return None
        
        # 3. Login no dispositivo
        if not sdk.login_device(device_id):
            return None
        
        

        # 4. Buscar gravações
        print("\n" + "=" * 60)
        print("BUSCANDO GRAVAÇÕES")
        print("=" * 60)
        # recordings = sdk.find_recordings(device_id, CHANNEL, start_str, end_str)
        
        # 5. Download de gravação (se houver)
        # if recordings:
        #     print("\n" + "=" * 60)
        #     print("DOWNLOAD DE GRAVAÇÃO")
        #     print("=" * 60)
            
        #     # Cria diretório para downloads
        #     os.makedirs("downloads", exist_ok=True)
            
        #     # Baixa primeira gravação encontrada
        #     rec = recordings[0]
        #     rec_start = rec.get("StartTime", start_str)
        #     rec_end = rec.get("EndTime", end_str)
        file_name=f"nvr01_stream{CHANNEL}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        output_file = f"videos/{file_name}"
            
        download_handle = sdk.download_recording(
            device_id, CHANNEL, start_str, end_str, output_file,0
        )
        
        if download_handle > 0:
            # Aguarda download com timeout de 3 minutos
            print("⏳ Aguardando conclusão do download...")
            timeout = 180  # 3 minutos (era 30 segundos - muito curto!)
            start_time = time.time()
            last_bytes = 0
            last_file_size = 0
            file_size_unchanged_count = 0
            
            while not sdk.download_completed:
                time.sleep(1)
                elapsed = int(time.time() - start_time)
                
                # Mostra progresso a cada 5 segundos
                if elapsed % 5 == 0 and sdk.download_bytes > last_bytes:
                    print(f"   {elapsed}s - {sdk.download_bytes} bytes baixados...")
                    last_bytes = sdk.download_bytes
                
                # Detecta quando arquivo parou de crescer (fallback para SDKs que não enviam 100%)
                if output_file and os.path.exists(output_file):
                    current_file_size = os.path.getsize(output_file)
                    if current_file_size > 0:
                        if current_file_size == last_file_size:
                            file_size_unchanged_count += 1
                            # Se arquivo não cresceu por 5 segundos E tem progresso > 80%, considerar concluído
                            if file_size_unchanged_count >= 5 and sdk.download_progress > 80:
                                print(f"\n✅ Download estabilizado!")
                                print(f"   📁 Arquivo: {output_file}")
                                print(f"   📊 Tamanho: {current_file_size / (1024*1024):.2f} MB")
                                print(f"   ✅ Progresso final: {sdk.download_progress}%")
                                sdk.download_completed = True
                                break
                        else:
                            file_size_unchanged_count = 0  # Reset se arquivo cresceu
                            last_file_size = current_file_size
                
                if elapsed > timeout:
                    # Antes de falhar, verificar se arquivo existe e tem conteúdo
                    if output_file and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                        file_size = os.path.getsize(output_file)
                        print(f"\n⚠️  Timeout após {timeout}s, mas arquivo foi criado!")
                        print(f"   📁 Arquivo: {output_file}")
                        print(f"   📊 Tamanho: {file_size / (1024*1024):.2f} MB")
                        print(f"   ✅ Progresso final: {sdk.download_progress}%")
                        print(f"   🔄 Considerando download como bem-sucedido...")
                        sdk.download_completed = True  # Marca como concluído!
                        break
                    else:
                        print(f"\n⚠️  Timeout após {timeout}s! Download pode estar incompleto.")
                        print(f"   Total baixado: {sdk.download_bytes} bytes")
                        output_file = None  # Marca como falha por timeout
                        break
        else:
            output_file = None  # Falha ao iniciar download
    
        # 6. Logout
        print("\n" + "=" * 60)
        print("FINALIZANDO")
        print("=" * 60)
        sdk.logout_device(device_id)
        
    finally:
        sdk.cleanup()
    
    if output_file and sdk.download_completed:
        print(f"\n✓ Processo concluído! Arquivo salvo em: {output_file}")
        return output_file
    else:
        print("\n✗ Download não completado ou falhou.")
        return None

