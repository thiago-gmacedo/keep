#!/usr/bin/env python3
"""
Scheduler para execução automática do pipeline OCR Keep
Substitui o run_loop.sh com execução em container Docker
"""

import schedule
import time
import subprocess
import logging
import sys
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def log_message(message: str):
    """Log com timestamp formatado"""
    logger.info(f"🕒 {message}")

def run_pipeline():
    """Executa o pipeline principal"""
    try:
        log_message("🚀 Iniciando execução agendada do pipeline OCR Keep")
        log_message("🏷️ Filtro de label: 'Anotações diárias'")
        
        # Executar pipeline principal
        result = subprocess.run([
            sys.executable, "-m", "src.main", "Anotações diárias"
        ], 
        cwd="/app",
        capture_output=True, 
        text=True,
        timeout=1800  # 30 minutos timeout
        )
        
        if result.returncode == 0:
            log_message("✅ Pipeline executado com sucesso")
            log_message(f"📊 Saída: {result.stdout[-200:]}")  # Últimos 200 chars
        else:
            log_message(f"❌ Pipeline falhou com código: {result.returncode}")
            log_message(f"🔍 Erro: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        log_message("⏰ Pipeline excedeu tempo limite de 30 minutos")
    except Exception as e:
        log_message(f"💥 Erro inesperado: {e}")

def next_execution_time():
    """Calcula próximo horário de execução"""
    current_hour = datetime.now().hour
    current_minute = datetime.now().minute
    
    if current_hour < 23 or (current_hour == 23 and current_minute < 45):
        return "hoje às 23:45"
    else:
        return "amanhã às 23:45"

def main():
    """Função principal do scheduler"""
    log_message("🔄 Iniciando scheduler do pipeline Keep")
    log_message("⏰ Horários programados: 23:45 (diariamente)")
    log_message(f"🔄 Próxima execução: {next_execution_time()}")
    
    # Agendar execução diária às 23:45
    schedule.every().day.at("23:45").do(run_pipeline)
    
    # Manter o scheduler rodando
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Verificar a cada minuto
            
        except KeyboardInterrupt:
            log_message("🛑 Scheduler interrompido pelo usuário")
            break
        except Exception as e:
            log_message(f"❌ Erro no scheduler: {e}")
            time.sleep(300)  # Aguardar 5 minutos antes de tentar novamente

if __name__ == "__main__":
    main()
