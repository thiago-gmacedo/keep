#!/bin/bash
# Script de execução programada do pipeline OCR Keep
# Executa diariamente às 1h e 4h da manhã
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

# Função para verificar se é hora de executar (1h ou 4h da manhã)
is_execution_time() {
    current_hour=$(date '+%H')
    current_minute=$(date '+%M')
    
    # Executar às 1:00 ou 4:00 (janela de 5 minutos: 00-04)
    if [[ "$current_hour" == "02" && "$current_minute" == "45" ]]; then
        return 0  # É hora de executar
    else
        return 1  # Não é hora de executar
    fi
}

# Função para calcular próximo horário de execução
next_execution_time() {
    current_hour=$(date '+%H')
    current_minute=$(date '+%M')
    
    if [[ "$current_hour" -lt "01" ]]; then
        echo "hoje às 01:00"
    elif [[ "$current_hour" -eq "01" && "$current_minute" -ge "05" ]] || [[ "$current_hour" -gt "01" && "$current_hour" -lt "04" ]]; then
        echo "hoje às 04:00"
    elif [[ "$current_hour" -eq "04" && "$current_minute" -ge "05" ]] || [[ "$current_hour" -gt "04" ]]; then
        echo "amanhã às 01:00"
    else
        echo "hoje às $(date '+%H'):$(date '+%M')"
    fi
}

log_message "🚀 Iniciando execução agendada do pipeline OCR Keep"
log_message "📁 Diretório: $SCRIPT_DIR"
log_message "🏷️ Filtro de label: 'Anotações diárias'"
log_message "⏰ Horários de execução: 01:00 e 04:00 (diariamente)"
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
