#!/bin/bash
# Script de verificação e setup automático do projeto OCR Keep
# Verifica configurações e cria estrutura necessária

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔍 VERIFICAÇÃO DE SETUP - OCR Keep → Obsidian + Vector DB"
echo "========================================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_ok() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Verificar estrutura de diretórios básica
echo -e "\n📁 Verificando estrutura de diretórios..."

if [ -d "src" ]; then
    log_ok "Diretório src/ encontrado"
else
    log_error "Diretório src/ não encontrado!"
    exit 1
fi

if [ -d ".env" ]; then
    log_ok "Diretório .env/ encontrado"
else
    log_warn "Criando diretório .env/"
    mkdir -p .env
fi

# Verificar arquivo de configuração
echo -e "\n🔑 Verificando configuração..."

if [ -f ".env/config" ]; then
    log_ok "Arquivo de configuração encontrado"
    
    # Verificar se tem as chaves necessárias
    if grep -q "OPENAI_API_KEY=sk-" ".env/config" 2>/dev/null; then
        log_ok "Chave OpenAI configurada"
    else
        log_warn "Chave OpenAI não configurada ou inválida"
    fi
    
    if grep -q "GOOGLE_EMAIL=.*@" ".env/config" 2>/dev/null; then
        log_ok "Email Google configurado"
    else
        log_warn "Email Google não configurado"
    fi
    
    if grep -q "GOOGLE_MASTER_TOKEN=aas_et" ".env/config" 2>/dev/null; then
        log_ok "Master token Google configurado"
    else
        log_warn "Master token Google não configurado"
    fi
    
else
    log_warn "Arquivo de configuração não encontrado"
    if [ -f ".env/config.example" ]; then
        log_info "Copiando exemplo de configuração..."
        cp .env/config.example .env/config
        log_warn "Configure suas credenciais em .env/config"
    else
        log_error "Arquivo de exemplo não encontrado!"
        exit 1
    fi
fi

# Verificar permissões
echo -e "\n🔒 Verificando permissões..."

if [ -f ".env/config" ]; then
    current_perms=$(stat -f "%A" ".env/config" 2>/dev/null || stat -c "%a" ".env/config" 2>/dev/null)
    if [ "$current_perms" = "600" ]; then
        log_ok "Permissões do arquivo de configuração OK (600)"
    else
        log_warn "Ajustando permissões do arquivo de configuração..."
        chmod 600 .env/config
        log_ok "Permissões ajustadas para 600"
    fi
fi

if [ -f "run_loop.sh" ]; then
    if [ -x "run_loop.sh" ]; then
        log_ok "Script run_loop.sh tem permissão de execução"
    else
        log_warn "Ajustando permissões do script..."
        chmod +x run_loop.sh
        log_ok "Permissões de execução adicionadas"
    fi
fi

# Verificar dependências Python
echo -e "\n🐍 Verificando dependências Python..."

if command -v python3 &> /dev/null; then
    log_ok "Python3 encontrado"
    python_version=$(python3 --version)
    log_info "Versão: $python_version"
else
    log_error "Python3 não encontrado!"
    exit 1
fi

if [ -f "requirements.txt" ]; then
    log_info "Verificando dependências do requirements.txt..."
    
    # Verificar algumas dependências críticas
    if python3 -c "import openai" 2>/dev/null; then
        log_ok "OpenAI instalado"
    else
        log_warn "OpenAI não instalado"
    fi
    
    if python3 -c "import gkeepapi" 2>/dev/null; then
        log_ok "gkeepapi instalado"
    else
        log_warn "gkeepapi não instalado"
    fi
    
    if python3 -c "import chromadb" 2>/dev/null; then
        log_ok "ChromaDB instalado"
    else
        log_warn "ChromaDB não instalado"
    fi
    
    echo -e "\n${YELLOW}💡 Para instalar dependências execute:${NC}"
    echo "   pip install -r requirements.txt"
    
else
    log_error "requirements.txt não encontrado!"
fi

# Criar diretórios necessários
echo -e "\n📂 Criando diretórios necessários..."

dirs_to_create=("logs" "images" "images/processed")

for dir in "${dirs_to_create[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        log_ok "Criado: $dir/"
    else
        log_ok "Existe: $dir/"
    fi
done

# Teste rápido de configuração (se possível)
echo -e "\n🧪 Teste rápido de configuração..."

if [ -f ".env/config" ] && python3 -c "import sys; sys.path.insert(0, '.'); from src.main import load_config_paths; load_config_paths()" 2>/dev/null; then
    log_ok "Configuração de caminhos válida"
else
    log_warn "Não foi possível testar configuração (normal se dependências não estão instaladas)"
fi

# Resumo final
echo -e "\n📋 RESUMO DO SETUP"
echo "=================="

if [ -f ".env/config" ] && grep -q "sk-" ".env/config" && grep -q "@" ".env/config"; then
    log_ok "Configuração básica OK"
    echo -e "\n🚀 ${GREEN}PRONTO PARA USAR!${NC}"
    echo -e "\n📖 Para executar:"
    echo "   • Pipeline único: python -m src.main"
    echo "   • Execução contínua: ./run_loop.sh"
    echo "   • Teste de busca: python teste.py"
else
    log_warn "Configuração incompleta"
    echo -e "\n📝 ${YELLOW}PRÓXIMOS PASSOS:${NC}"
    echo "   1. Configure suas credenciais em .env/config"
    echo "   2. Instale dependências: pip install -r requirements.txt"
    echo "   3. Execute: python -m src.main"
fi

echo -e "\n📚 Documentação completa em: README.md e CONFIG.md"
echo "======================================================"
