# Testes Mocados - Guia de Uso

Este diretório contém testes mocados para validar as funcionalidades dos serviços sem necessidade de hardware real (GPIO, Redis, SDK JFTech).

## Arquivos de Teste

### 1. `tests/test_mock_simple.py` - Testes Simples e Diretos
Teste rápido e fácil de entender, ideal para validação inicial.

**Execução:**
```bash
cd /home/abauruel/www/onvif_learn/RE/app
python3 tests/test_mock_simple.py
```

**O que testa:**
- ✓ JFTech Integration: mock do SDK e download
- ✓ Download Service: integração com jftech_main
- ✓ Producer Trigger: enfileiramento de tarefas
- ✓ Upload Service: envio para API externa
- ✓ Fluxo Completo: validação conceitual end-to-end

**Características:**
- Saída clara e colorida
- Não requer unittest
- Ideal para debug rápido

### 2. `tests/test_services.py` - Testes Unitários Completos
Testes mais robustos usando unittest do Python.

**Execução:**
```bash
cd /home/abauruel/www/onvif_learn/RE/app
python3 tests/test_services.py
```

ou

```bash
python3 -m unittest tests.test_services -v
```

**O que testa:**
- TestJFTechIntegration:
  - Sucesso no download
  - Falha por variáveis de ambiente ausentes
  
- TestDownloadService:
  - Download bem-sucedido
  - Download com falha
  - Timestamp inválido
  - Uso de timestamp padrão (hora atual)
  
- TestProducerService:
  - Trigger de evento e enfileiramento
  
- TestUploadService:
  - Upload bem-sucedido
  - Falha no upload
  
- TestIntegrationFlow:
  - Fluxo completo: producer → download → process → upload

**Características:**
- Coverage completo
- Casos de sucesso e erro
- Relatórios detalhados

## Estrutura dos Mocks

### Mocks Utilizados

1. **GPIO (RPi.GPIO)**: Mock do Raspberry Pi GPIO
2. **Redis/RQ**: Mock das filas Redis
3. **XCloudSDK**: Mock do SDK JFTech
4. **Variáveis de Ambiente**: Mock de credenciais do NVR
5. **Filesystem**: Mock de leitura/escrita de arquivos
6. **HTTP Requests**: Mock de chamadas API

### Exemplo de Mock

```python
# Mock do SDK JFTech
with patch('services.jftecth_integration.XCloudSDK') as mock_sdk:
    mock_sdk.initialize.return_value = True
    mock_sdk.login_device.return_value = True
    mock_sdk.download_recording.return_value = 1
    
    # Executa função
    result = main()
```

## Execução Rápida

```bash
# Teste simples (recomendado para início)
python3 tests/test_mock_simple.py

# Testes completos
python3 tests/test_services.py

# Validação de estrutura
python3 tests/test_validation.py
```

## Resultado Esperado

### ✓ Sucesso
Todos os testes devem passar sem erros:
```
Total: 5/5 testes aprovados
```

### ✗ Falha
Se algum teste falhar, verifique:
1. Todas as dependências instaladas: `pip3 install -r requirements.txt`
2. Estrutura de arquivos correta
3. Imports corretos nos módulos

## Dependências

```bash
# Não requer hardware
# Não requer Redis rodando
# Não requer SDK JFTech instalado

# Apenas Python 3 e bibliotecas padrão:
- unittest (built-in)
- unittest.mock (built-in)
```

## Validação de Funcionalidades

### Fluxo Testado

```
1. Producer Service (GPIO)
   ↓ (detecta botão pressionado)
   └→ enfileira tarefa com timestamp e canal

2. Download Service
   ↓ (processa fila)
   └→ chama jftech_integration.main()
      ↓ (conecta NVR via SDK)
      └→ retorna caminho do arquivo baixado

3. Video Processor
   ↓ (processamento opcional)
   └→ processa vídeo

4. Upload Service
   ↓ (processa fila de upload)
   └→ envia para API externa
      └→ remove arquivo local após sucesso
```

## Próximos Passos

Após testes mocados passarem:

1. **Testes de Integração Real**: teste com Redis/RQ rodando
2. **Testes com SDK Real**: teste com NVR JFTech real
3. **Testes em Raspberry Pi**: teste com GPIO real
4. **Testes End-to-End**: fluxo completo no ambiente de produção

## Troubleshooting

### Erro: ModuleNotFoundError
```bash
# Adicione o diretório ao PYTHONPATH
export PYTHONPATH=/home/abauruel/www/onvif_learn/RE/app:$PYTHONPATH
python3 test_mock_simple.py
```

### Erro: ImportError
Verifique que todos os arquivos estão presentes:
- config.py
- download_service.py
- producer_service.py
- upload_service.py
- video_processor.py
- services/jftecth_integration.py

## Contribuindo

Para adicionar novos testes:

1. Adicione caso de teste em `test_services.py`
2. Use mocks apropriados para evitar dependências
3. Teste casos de sucesso e falha
4. Execute todos os testes para garantir que nada quebrou
