#!/bin/bash
# Script de execução programada do pipeline OCR Keep
# Executa diariamente às 23:45
# Processa apenas notas com a label "Anotações diárias"

# Diretório do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Criar diretório de logs se não existir
mkdir -p logs

# Função de log
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a logs/pipeline.log
}

# Função para verificar se é hora de executar (02:45)
is_execution_time() {
    current_hour=$(date '+%H')
    current_minute=$(date '+%M')
    
    # Executar às 02:45 (janela de 5 minutos: 45-49)
    if [[ "$current_hour" == "02" && "$current_minute" -ge "45" && "$current_minute" -le "49" ]]; then
        return 0  # É hora de executar
    else
        return 1  # Não é hora de executar
    fi
}

# Função para calcular próximo horário de execução
next_execution_time() {
    current_hour=$(date '+%H')
    current_minute=$(date '+%M')
    
    if [[ "$current_hour" -lt "02" ]]; then
        echo "hoje às 23:45"
    elif [[ "$current_hour" -eq "02" && "$current_minute" -lt "45" ]]; then
        echo "hoje às 23:45"
    else
        echo "amanhã às 23:45"
    fi
}

log_message "🚀 Iniciando execução agendada do pipeline OCR Keep"
log_message "📁 Diretório: $SCRIPT_DIR"
log_message "🏷️ Filtro de label: 'Anotações diárias'"
log_message "⏰ Horários de execução: 23:45 (diariamente)"
log_message "🔄 Próxima execução: $(next_execution_time)"

# Trap para capturar sinais e parar graciosamente
trap 'log_message "🛑 Execução agendada interrompida pelo usuário"; exit 0' INT TERM

# Função para executar o pipeline
run_pipeline() {
    log_message "🔄 Executando pipeline..."
    
    # Executar o pipeline principal com label 'Anotações diárias'
    python -m src.main "Anotações diárias" >> logs/pipeline.log 2>&1
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log_message "✅ Pipeline executado com sucesso"
    else
        log_message "❌ Pipeline falhou com código de saída: $exit_code"
    fi
    
    return $exit_code
}

# Loop principal para execução agendada
while true; do
    if is_execution_time; then
        log_message "⏰ Horário de execução detectado: $(date '+%H:%M')"
        run_pipeline
        
        # Aguardar até passar da hora atual para evitar múltiplas execuções
        while is_execution_time; do
            log_message "⌛ Aguardando fim da janela de execução..."
            sleep 60  # Aguardar 1 minuto
        done
        
        log_message "📅 Próxima execução: $(next_execution_time)"
        log_message "---"
    else
        # Verificar a cada 5 minutos se chegou o horário
	log_message "Não está no momento schedulado."
        sleep 300
    fi
done
