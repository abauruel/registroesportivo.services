#!/usr/bin/env python3
"""
Testes mocados para validar funcionalidades dos serviços
Executa testes sem dependências de hardware (GPIO, Redis, SDK JFTech)
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
import sys
import os
from datetime import datetime

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestJFTechIntegration(unittest.TestCase):
    """Testes para jftech_integration"""
    
    @patch('services.jftecth_integration.load_dotenv')
    @patch('services.jftecth_integration.os.getenv')
    @patch('services.jftecth_integration.XCloudSDK')
    def test_main_success(self, mock_sdk_class, mock_getenv, mock_load_dotenv):
        """Testa execução bem-sucedida do main"""
        # Mock das variáveis de ambiente
        def getenv_side_effect(key):
            env_vars = {
                'NVR_IP': '192.168.0.100',
                'NVR_PORT': '34567',
                'NVR_USERNAME': 'admin',
                'NVR_PASSWORD': 'password123'
            }
            return env_vars.get(key)
        
        mock_getenv.side_effect = getenv_side_effect
        
        # Mock do SDK
        mock_sdk = MagicMock()
        mock_sdk.initialize.return_value = True
        mock_sdk.set_device_credentials.return_value = True
        mock_sdk.login_device.return_value = True
        mock_sdk.download_recording.return_value = 1
        mock_sdk.download_completed = False
        mock_sdk_class.return_value = mock_sdk
        
        # Simula sys.argv
        with patch('sys.argv', ['jftech_integration.py', '1', '2026-02-18 14:30:00']):
            # Mock de os.makedirs para não criar diretórios
            with patch('os.makedirs'):
                # Simula o comportamento assíncrono do download
                def simulate_download(*args):
                    mock_sdk.download_completed = True
                
                mock_sdk.download_recording.side_effect = lambda *args: (
                    simulate_download() or 1
                )
                
                from services.jftecth_integration import main
                result = main()
        
        # Verifica que retornou um caminho de arquivo
        self.assertIsNotNone(result)
        self.assertIn('nvr01_stream1_', result)
        self.assertTrue(result.endswith('.mp4'))
        
        # Verifica que as funções foram chamadas
        mock_sdk.initialize.assert_called_once()
        mock_sdk.set_device_credentials.assert_called_once()
        mock_sdk.login_device.assert_called_once()
        mock_sdk.logout_device.assert_called_once()
        mock_sdk.cleanup.assert_called_once()
    
    @patch('services.jftecth_integration.load_dotenv')
    @patch('services.jftecth_integration.os.getenv')
    def test_main_missing_env_vars(self, mock_getenv, mock_load_dotenv):
        """Testa quando faltam variáveis de ambiente"""
        mock_getenv.return_value = None
        
        from services.jftecth_integration import main
        result = main()
        
        # Deve retornar None quando faltam variáveis
        self.assertIsNone(result)


class TestDownloadService(unittest.TestCase):
    """Testes para download_service"""
    
    @patch('download_service.jftech_main')
    @patch('download_service.process_video')
    @patch('download_service.upload_queue')
    @patch('download_service.os.path.exists')
    def test_download_video_success(self, mock_exists, mock_queue, mock_process, mock_jftech):
        """Testa download bem-sucedido"""
        # Mock do retorno do jftech_main
        expected_file = 'videos/nvr01_stream0_20260218_143000.mp4'
        mock_jftech.return_value = expected_file
        mock_exists.return_value = True
        
        # Mock do sys.argv
        with patch('sys.argv', ['download_service.py']):
            from download_service import download_video
            
            result = download_video(
                timestamp='2026-02-18 14:30:00',
                channel=0
            )
        
        # Verifica resultado
        self.assertEqual(result, expected_file)
        
        # Verifica que chamou as funções corretas
        mock_jftech.assert_called_once()
        mock_process.assert_called_once_with(expected_file)
        mock_queue.enqueue.assert_called_once()
    
    @patch('download_service.jftech_main')
    def test_download_video_failure(self, mock_jftech):
        """Testa falha no download"""
        # Mock do retorno None (falha)
        mock_jftech.return_value = None
        
        with patch('sys.argv', ['download_service.py']):
            from download_service import download_video
            
            result = download_video(
                timestamp='2026-02-18 14:30:00',
                channel=0
            )
        
        # Deve retornar None em caso de falha
        self.assertIsNone(result)
    
    def test_download_video_invalid_timestamp(self):
        """Testa timestamp inválido"""
        with patch('sys.argv', ['download_service.py']):
            from download_service import download_video
            
            result = download_video(
                timestamp='invalid-timestamp',
                channel=0
            )
        
        # Deve retornar None para timestamp inválido
        self.assertIsNone(result)
    
    @patch('download_service.jftech_main')
    @patch('download_service.datetime')
    def test_download_video_default_timestamp(self, mock_datetime, mock_jftech):
        """Testa uso de timestamp padrão (hora atual)"""
        # Mock da hora atual
        mock_now = MagicMock()
        mock_now.strftime.return_value = '2026-02-18 14:30:00'
        mock_datetime.now.return_value = mock_now
        mock_datetime.strptime = datetime.strptime
        
        mock_jftech.return_value = 'videos/test.mp4'
        
        with patch('sys.argv', ['download_service.py']):
            with patch('download_service.os.path.exists', return_value=False):
                from download_service import download_video
                
                # Chama sem timestamp (deve usar hora atual)
                download_video(channel=1)
        
        # Verifica que foi chamado
        mock_jftech.assert_called_once()


class TestProducerService(unittest.TestCase):
    """Testes para producer_service (sem GPIO real)"""
    
    @patch('producer_service.datetime')
    @patch('producer_service.download_queue')
    def test_trigger_event(self, mock_queue, mock_datetime):
        """Testa evento de trigger"""
        # Mock da hora atual
        mock_now = MagicMock()
        mock_now.strftime.return_value = '2026-02-18 14:30:00'
        mock_datetime.now.return_value = mock_now
        
        # Mock GPIO para evitar erro de hardware
        with patch.dict('sys.modules', {'RPi': MagicMock(), 'RPi.GPIO': MagicMock()}):
            from producer_service import trigger_event
            
            # Executa trigger
            trigger_event()
        
        # Verifica que enfileirou a tarefa
        mock_queue.enqueue.assert_called_once()
        
        # Verifica os argumentos
        args, kwargs = mock_queue.enqueue.call_args
        self.assertEqual(args[0], 'download_service.download_video')
        self.assertEqual(kwargs['timestamp'], '2026-02-18 14:30:00')
        self.assertEqual(kwargs['channel'], 0)


class TestUploadService(unittest.TestCase):
    """Testes para upload_service"""
    
    @patch('upload_service.requests.post')
    @patch('upload_service.os.remove')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake video data')
    def test_upload_video_success(self, mock_file, mock_remove, mock_post):
        """Testa upload bem-sucedido"""
        # Mock da resposta HTTP
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        from upload_service import upload_video
        
        test_file = '/tmp/test_video.mp4'
        upload_video(test_file)
        
        # Verifica que fez POST
        mock_post.assert_called_once()
        
        # Verifica que removeu o arquivo
        mock_remove.assert_called_once_with(test_file)
    
    @patch('upload_service.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake video data')
    def test_upload_video_failure(self, mock_file, mock_post):
        """Testa falha no upload"""
        # Mock da resposta HTTP com erro
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        from upload_service import upload_video
        
        test_file = '/tmp/test_video.mp4'
        
        # Deve lançar exceção em caso de erro
        with self.assertRaises(Exception):
            upload_video(test_file)


class TestIntegrationFlow(unittest.TestCase):
    """Testes de integração do fluxo completo"""
    
    @patch('producer_service.download_queue')
    @patch('download_service.jftech_main')
    @patch('download_service.process_video')
    @patch('download_service.upload_queue')
    @patch('upload_service.requests.post')
    @patch('os.path.exists')
    @patch('os.remove')
    def test_complete_flow(self, mock_remove, mock_exists, mock_upload_post, 
                          mock_upload_queue, mock_process, mock_jftech, mock_download_queue):
        """Testa fluxo completo: trigger -> download -> process -> upload"""
        
        # 1. Simula trigger do producer
        with patch('producer_service.datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_now.strftime.return_value = '2026-02-18 14:30:00'
            mock_datetime.now.return_value = mock_now
            
            with patch.dict('sys.modules', {'RPi': MagicMock(), 'RPi.GPIO': MagicMock()}):
                from producer_service import trigger_event
                trigger_event()
        
        # Verifica enfileiramento do download
        mock_download_queue.enqueue.assert_called_once()
        
        # 2. Simula execução do download
        test_video_file = 'videos/nvr01_stream0_20260218_143000.mp4'
        mock_jftech.return_value = test_video_file
        mock_exists.return_value = True
        
        with patch('sys.argv', ['download_service.py']):
            from download_service import download_video
            result = download_video(timestamp='2026-02-18 14:30:00', channel=0)
        
        # Verifica que processou e enfileirou upload
        self.assertEqual(result, test_video_file)
        mock_process.assert_called_once_with(test_video_file)
        mock_upload_queue.enqueue.assert_called_once()
        
        # 3. Simula execução do upload
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_upload_post.return_value = mock_response
        
        with patch('builtins.open', mock_open(read_data=b'video data')):
            from upload_service import upload_video
            upload_video(test_video_file)
        
        # Verifica que fez upload e removeu arquivo
        mock_upload_post.assert_called_once()
        mock_remove.assert_called_once_with(test_video_file)


def run_tests():
    """Executa todos os testes"""
    print("=" * 70)
    print("EXECUTANDO TESTES MOCADOS DOS SERVIÇOS")
    print("=" * 70)
    print()
    
    # Cria test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Adiciona todos os testes
    suite.addTests(loader.loadTestsFromTestCase(TestJFTechIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestDownloadService))
    suite.addTests(loader.loadTestsFromTestCase(TestProducerService))
    suite.addTests(loader.loadTestsFromTestCase(TestUploadService))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationFlow))
    
    # Executa testes com verbosidade
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Sumário
    print()
    print("=" * 70)
    print("SUMÁRIO DOS TESTES")
    print("=" * 70)
    print(f"Total de testes: {result.testsRun}")
    print(f"✓ Sucessos: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"✗ Falhas: {len(result.failures)}")
    print(f"✗ Erros: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
