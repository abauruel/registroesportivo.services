#!/bin/bash
# Atalhos para facilitar o desenvolvimento do projeto RE

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ROOT="/home/abauruel/www/onvif_learn/RE"
APP_DIR="$PROJECT_ROOT/app"
VENV_BIN="$PROJECT_ROOT/.venv/bin"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 Atalhos do Projeto RE${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Para adicionar esses atalhos ao seu terminal, execute:"
echo -e "${YELLOW}source $APP_DIR/aliases.sh${NC}"
echo ""
echo "Ou adicione ao ~/.bashrc:"
echo -e "${YELLOW}echo 'source $APP_DIR/aliases.sh' >> ~/.bashrc${NC}"
echo ""
echo -e "${BLUE}========================================${NC}"
echo ""

# Função: Verificar ambiente
re_check() {
    cd "$APP_DIR" && "$VENV_BIN/python" check_worker_env.py
}

# Função: Executar worker
re_worker() {
    local queue="${1:-download_queue}"
    cd "$APP_DIR"
    echo -e "${GREEN}🚀 Iniciando worker para fila: $queue${NC}"
    "$APP_DIR/start_worker.sh" "$queue"
}

# Função: Limpar jobs falhados
re_clean() {
    cd "$APP_DIR" && "$VENV_BIN/python" clear_failed_jobs.py
}

# Função: Ver jobs falhados
re_jobs() {
    cd "$APP_DIR" && "$VENV_BIN/python" check_job.py "$@"
}

# Função: Executar simulador
re_sim() {
    local channel="${1:-1}"
    cd "$APP_DIR"
    echo -e "${GREEN}🎮 Simulando evento no canal $channel${NC}"
    "$VENV_BIN/python" simulator.py --channel "$channel"
}

# Função: Simulação rápida
re_quick() {
    cd "$APP_DIR"
    echo -e "${GREEN}⚡ Teste rápido - canal 1${NC}"
    "$VENV_BIN/python" simulator.py --quick
}

# Função: Ver logs do Redis
re_redis_logs() {
    podman logs -f redis_edge
}

# Função: Ver fila no Redis
re_queue() {
    local queue="${1:-download_queue}"
    echo -e "${BLUE}📊 Tamanho da fila $queue:${NC}"
    podman exec -it redis_edge redis-cli LLEN "$queue"
}

# Função: Ajuda
re_help() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}📚 Comandos Disponíveis${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${GREEN}re_check${NC}          - Verifica ambiente (EXECUTE PRIMEIRO!)"
    echo -e "${GREEN}re_worker [fila]${NC}  - Inicia worker (padrão: download_queue)"
    echo -e "${GREEN}re_clean${NC}          - Limpa jobs falhados"
    echo -e "${GREEN}re_jobs [ID]${NC}      - Lista jobs falhados ou ver específico"
    echo -e "${GREEN}re_sim <canal>${NC}    - Simula evento em canal (1-63)"
    echo -e "${GREEN}re_quick${NC}          - Teste rápido (canal 1)"
    echo -e "${GREEN}re_queue [fila]${NC}   - Mostra tamanho da fila"
    echo -e "${GREEN}re_redis_logs${NC}     - Mostra logs do Redis"
    echo -e "${GREEN}re_help${NC}           - Mostra esta ajuda"
    echo ""
    echo -e "${YELLOW}Exemplos:${NC}"
    echo "  re_check              # Verifica se ambiente está OK"
    echo "  re_worker             # Inicia worker download_queue"
    echo "  re_worker upload_queue  # Inicia worker upload_queue"
    echo "  re_clean              # Limpa jobs antigos"
    echo "  re_sim 2              # Simula evento canal 2"
    echo "  re_quick              # Teste rápido"
    echo "  re_jobs               # Lista jobs falhados"
    echo "  re_jobs abc123...     # Ver job específico"
    echo "  re_queue              # Ver tamanho da fila"
    echo ""
    echo -e "${BLUE}========================================${NC}"
}

# Exporta as funções
export -f re_check
export -f re_worker
export -f re_clean
export -f re_jobs
export -f re_sim
export -f re_quick
export -f re_redis_logs
export -f re_queue
export -f re_help

# Mostra ajuda se executado diretamente
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    re_help
fi
