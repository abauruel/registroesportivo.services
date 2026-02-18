# Sistema de Gravação NVR - JFTech

Sistema automatizado para captura e upload de gravações de NVR JFTech via eventos GPIO.

## Quick Start

### Executar Testes
```bash
# Validação completa do sistema
python3 tests/test_validation.py

# Testes com mocks
python3 tests/test_mock_simple.py
```

### Executar Serviços
```bash
# Producer (detecta eventos GPIO)
python3 producer_service.py

# Workers RQ
rq worker download_queue
rq worker upload_queue
```

## Estrutura

```
app/
├── config.py                 # Configurações
├── producer_service.py       # Detecta eventos GPIO
├── download_service.py       # Baixa vídeos do NVR
├── upload_service.py         # Upload para API externa
├── video_processor.py        # Processamento de vídeo
├── services/                 # Serviços auxiliares
│   └── jftecth_integration.py   # SDK JFTech
├── lib/                      # Bibliotecas externas
├── tests/                    # Testes automatizados
│   ├── test_validation.py       # ✓ 9/9 aprovados
│   ├── test_mock_simple.py      # Testes simples
│   └── test_services.py         # Suite completa
└── docs/                     # Documentação
    ├── README.md                # Documentação completa
    └── TESTES_README.md         # Guia de testes
```

## Documentação

📖 **Documentação completa**: [docs/README.md](docs/README.md)

🧪 **Guia de testes**: [docs/TESTES_README.md](docs/TESTES_README.md)

## Fluxo

```
GPIO Trigger → Producer → Download (NVR) → Process → Upload → Cleanup
```

## Configuração Rápida

Crie arquivo `.env`:
```bash
NVR_IP=192.168.0.168
NVR_PORT=34567
NVR_USERNAME=service
NVR_PASSWORD=sua_senha
```

## Dependências

```bash
pip3 install -r requirements.txt
```

## Status

✅ Sistema validado e pronto para uso (9/9 testes aprovados)
