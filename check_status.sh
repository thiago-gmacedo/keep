#!/bin/bash
# Script de verificação de status do pipeline OCR Keep

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔍 STATUS DO PIPELINE OCR KEEP"
echo "================================"

# Verificar se o processo está rodando
if pgrep -f "run_loop.sh" > /dev/null; then
    echo "✅ Pipeline em execução (PID: $(pgrep -f 'run_loop.sh'))"
else
    echo "❌ Pipeline não está rodando"
fi

# Verificar logs recentes
if [ -f "logs/pipeline.log" ]; then
    echo ""
    echo "📋 ÚLTIMAS 10 LINHAS DO LOG:"
    echo "----------------------------"
    tail -n 10 logs/pipeline.log
    echo ""
    echo "📊 ESTATÍSTICAS DO LOG:"
    echo "----------------------"
    echo "Total de linhas: $(wc -l < logs/pipeline.log)"
    echo "Sucessos: $(grep -c "✅" logs/pipeline.log)"
    echo "Erros: $(grep -c "❌" logs/pipeline.log)"
else
    echo "⚠️ Arquivo de log não encontrado"
fi

# Verificar configuração
echo ""
echo "⚙️ CONFIGURAÇÃO:"
echo "---------------"
if [ -f ".env/config" ]; then
    echo "✅ Arquivo de configuração encontrado"
    echo "Caminhos configurados:"
    if grep -q "OBS_PATH" .env/config; then
        echo "  📁 Obsidian: $(grep "OBS_PATH" .env/config | cut -d'=' -f2)"
    fi
    if grep -q "CHROMA_DB_PATH" .env/config; then
        echo "  🧠 ChromaDB: $(grep "CHROMA_DB_PATH" .env/config | cut -d'=' -f2)"
    fi
else
    echo "❌ Arquivo de configuração não encontrado"
fi

# Verificar diretórios
echo ""
echo "📁 DIRETÓRIOS:"
echo "-------------"
obs_path=$(grep "OBS_PATH" .env/config 2>/dev/null | cut -d'=' -f2)
chroma_path=$(grep "CHROMA_DB_PATH" .env/config 2>/dev/null | cut -d'=' -f2)

if [ -n "$obs_path" ] && [ -d "$obs_path" ]; then
    note_count=$(find "$obs_path" -name "*.md" 2>/dev/null | wc -l)
    echo "  📚 Obsidian: $obs_path ($note_count notas)"
else
    echo "  ❌ Diretório Obsidian não encontrado"
fi

if [ -n "$chroma_path" ] && [ -d "$chroma_path" ]; then
    echo "  🧠 ChromaDB: $chroma_path"
else
    echo "  ❌ Diretório ChromaDB não encontrado"
fi

echo ""
echo "🕐 Última execução: $(date)"
