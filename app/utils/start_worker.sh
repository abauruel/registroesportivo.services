#!/bin/bash
# Script para executar RQ worker do diretório correto

# Vai para o diretório app
cd "$(dirname "$0")"

echo "🚀 Iniciando RQ Worker..."
echo "📂 Diretório: $(pwd)"
echo "📡 Fila: ${1:-download_queue}"
echo "="

# Executa o worker
if [ -f "../.venv/bin/rq" ]; then
    # Se existe venv, usa ele
    echo "🐍 Usando ambiente virtual"
    ../.venv/bin/rq worker "${1:-download_queue}"
else
    # Senão usa rq do sistema
    echo "🐍 Usando RQ do sistema"
    rq worker "${1:-download_queue}"
fi
