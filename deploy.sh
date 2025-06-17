#!/bin/bash
"""
Script de deploy completo para o sistema Keep OCR
Substitui toda configuração manual por containers Docker
"""

echo "🚀 DEPLOY COMPLETO - KEEP OCR PIPELINE"
echo "========================================"

# Parar serviços antigos se existirem
echo "🛑 Parando serviços antigos..."
pkill -f "run_loop.sh" 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true
sudo systemctl stop keep-pipeline 2>/dev/null || true

# Parar containers antigos
echo "🐳 Parando containers Docker antigos..."
docker-compose down 2>/dev/null || true

# Construir e iniciar novos containers
echo "🔨 Construindo imagens Docker..."
docker-compose build

echo "🚀 Iniciando todos os serviços..."
docker-compose up -d

# Aguardar inicialização
echo "⏳ Aguardando inicialização dos serviços..."
sleep 10

# Verificar status
echo "📊 Status dos serviços:"
docker-compose ps

echo ""
echo "✅ DEPLOY CONCLUÍDO!"
echo "===================="
echo "🌐 Web Server: http://localhost:8000"
echo "📱 WhatsApp Bot: Aguardando QR code (se primeira vez)"
echo "🕒 Scheduler: Executando às 23:45 diariamente"
echo ""
echo "📋 Comandos úteis:"
echo "  docker-compose logs -f              # Ver todos os logs"
echo "  docker-compose logs -f wa_bot       # Ver logs do bot"
echo "  docker-compose logs -f web_server   # Ver logs da API"
echo "  docker-compose restart wa_bot       # Reiniciar bot"
echo "  curl http://localhost:8000/health   # Testar API"
