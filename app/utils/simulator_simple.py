#!/usr/bin/env python3
"""
Simulador SIMPLES - Testa o fluxo sem Redis
Demonstra chamadas diretas às funções sem infraestrutura
"""

import sys
import os
from datetime import datetime

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def simulate_gpio_event(channel):
    """
    Simula um evento GPIO e executa o fluxo completo (com mocks)
    
    Args:
        channel (int): Número do canal (0-63)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("\n" + "="*70)
    print(f"🔘 SIMULANDO EVENTO GPIO - Canal {channel}")
    print("="*70)
    print(f"  Timestamp: {timestamp}")
    print(f"  Canal: {channel}")
    print()
    
    # Passo 1: Producer captura evento
    print("📥 [1/3] Producer captura evento GPIO...")
    print(f"   ├─ Evento detectado no pino GPIO (simulado)")
    print(f"   ├─ Timestamp capturado: {timestamp}")
    print(f"   └─ Parâmetros: channel={channel}, timestamp='{timestamp}'")
    print()
    
    # Passo 2: Download Service é acionado
    print("⬇️  [2/3] Download Service processa requisição...")
    
    # Simula o processo de download
    output_file = f"videos/channel_{channel}_{timestamp.replace(' ', '_').replace(':', '-')}.mp4"
    
    print(f"   ├─ Conectando ao NVR (simulado)...")
    print(f"   ├─ Canal: {channel}")
    print(f"   ├─ Timestamp: {timestamp}")
    print(f"   ├─ Baixando 15 segundos antes do timestamp...")
    print(f"   ├─ Arquivo gerado: {output_file}")
    print(f"   └─ ✅ Download concluído com sucesso (mock)")
    
    print()
    
    # Passo 3: Upload Service (simulado)
    print("⬆️  [3/3] Upload Service enviaria arquivo...")
    if output_file:
        print(f"   ├─ Arquivo: {output_file}")
        print(f"   ├─ Destino: API de upload (mock)")
        print(f"   └─ Upload concluído (simulado)")
    else:
        print(f"   └─ ⚠️  Sem arquivo para upload")
    
    print()
    print("="*70)
    print("✅ SIMULAÇÃO COMPLETA")
    print("="*70)
    print()
    
    return output_file

def interactive_mode():
    """Modo interativo com menu simples"""
    print("\n" + "="*70)
    print("🎮 SIMULADOR DE EVENTOS GPIO - Modo Interativo")
    print("="*70)
    print("\nComandos disponíveis:")
    print("  1 ou 2     Simular evento no canal 1 ou 2")
    print("  c <num>    Simular evento em canal específico (0-63)")
    print("  q          Sair")
    print("\n" + "="*70)
    
    while True:
        try:
            cmd = input("\n➤ Digite comando: ").strip().lower()
            
            if cmd == 'q':
                print("👋 Encerrando simulador...")
                break
            elif cmd == '1':
                simulate_gpio_event(1)
            elif cmd == '2':
                simulate_gpio_event(2)
            elif cmd.startswith('c '):
                try:
                    channel = int(cmd.split()[1])
                    if 0 <= channel <= 63:
                        simulate_gpio_event(channel)
                    else:
                        print("❌ Canal deve estar entre 0 e 63")
                except (ValueError, IndexError):
                    print("❌ Uso: c <número_do_canal>")
            else:
                print("❌ Comando inválido. Use: 1, 2, c <num> ou q")
        
        except KeyboardInterrupt:
            print("\n\n👋 Simulador interrompido")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

def main():
    """Ponto de entrada principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Simulador simples de eventos GPIO (sem Redis)',
        epilog='Exemplos:\n'
               '  python3 simulator_simple.py --channel 1\n'
               '  python3 simulator_simple.py -i\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-c', '--channel', type=int, metavar='N',
                        help='Simular evento em canal específico (0-63)')
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='Modo interativo com menu')
    
    args = parser.parse_args()
    
    # Se nenhum argumento, mostra help
    if len(sys.argv) == 1:
        interactive_mode()
        return
    
    # Modo interativo
    if args.interactive:
        interactive_mode()
        return
    
    # Modo comando único
    if args.channel is not None:
        if 0 <= args.channel <= 63:
            simulate_gpio_event(args.channel)
        else:
            print("❌ Erro: Canal deve estar entre 0 e 63")
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
