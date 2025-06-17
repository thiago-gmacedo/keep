#!/bin/bash
# Script de deploy completo para o sistema Keep OCR
# Substitui toda configuração manual por containers Docker

echo "🚀 DEPLOY COMPLETO - KEEP OCR PIPELINE"
echo "========================================"

# Detectar comando docker-compose
DOCKER_COMPOSE="docker-compose"
if ! command -v docker-compose &> /dev/null; then
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
    else
        echo "❌ Docker Compose não encontrado. Instale docker ou docker-compose"
        exit 1
    fi
fi

echo "🐳 Usando: $DOCKER_COMPOSE"

# Parar serviços antigos se existirem
echo "🛑 Parando serviços antigos..."
pkill -f "run_loop.sh" 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true
sudo systemctl stop keep 2>/dev/null || true

# Parar containers antigos
echo "🐳 Parando containers Docker antigos..."
$DOCKER_COMPOSE down 2>/dev/null || true

# Construir e iniciar novos containers
echo "🔨 Construindo imagens Docker..."
$DOCKER_COMPOSE build

echo "🚀 Iniciando todos os serviços..."
$DOCKER_COMPOSE up -d

# Aguardar inicialização
echo "⏳ Aguardando inicialização dos serviços..."
sleep 10

# Verificar status
echo "📊 Status dos serviços:"
$DOCKER_COMPOSE ps

echo ""
echo "✅ DEPLOY CONCLUÍDO!"
echo "===================="
echo "🌐 Web Server: http://localhost:8000"
echo "📱 WhatsApp Bot: Aguardando QR code (se primeira vez)"
echo "🕒 Scheduler: Executando às 23:45 diariamente"
echo ""
echo "📋 Comandos úteis:"
echo "  $DOCKER_COMPOSE logs -f              # Ver todos os logs"
echo "  $DOCKER_COMPOSE logs -f wa_bot       # Ver logs do bot"
echo "  $DOCKER_COMPOSE logs -f web_server   # Ver logs da API"
echo "  $DOCKER_COMPOSE restart wa_bot       # Reiniciar bot"
echo "  curl http://localhost:8000/health    # Testar API"
