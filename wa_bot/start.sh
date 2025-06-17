#!/bin/bash
# Script de inicialização para o bot WhatsApp
# Garante que o diretório sessions tenha as permissões corretas

echo "🔧 Preparando ambiente do bot WhatsApp..."

# Criar diretório sessions se não existir
mkdir -p /app/wa_bot/sessions

# Garantir permissões corretas
chmod 755 /app/wa_bot/sessions

echo "✅ Ambiente preparado. Iniciando bot..."

# Executar o bot
exec node index.js
