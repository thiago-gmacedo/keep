#!/usr/bin/env python3
"""
Auto Indexador - Monitora a pasta de imagens e indexa automaticamente novos JSONs no ChromaDB

Este script monitora a pasta 'image' por novos arquivos JSON gerados pelo OCR
e os indexa automaticamente no ChromaDB.
"""

import sys
import json
import time
from pathlib import Path
import logging

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

# Importar o módulo ChromaIndexer
from src.chroma_indexer import index_note_in_chroma

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup():
    """Configura o ambiente e verifica dependências"""
    # Verificar se o diretório de imagens existe
    image_dir = ROOT_DIR / "image"
    if not image_dir.exists():
        logger.error(f"❌ Diretório de imagens não encontrado: {image_dir}")
        sys.exit(1)
    
    # Criar arquivo de controle para rastreamento
    processed_file = ROOT_DIR / ".indexed_notes.json"
    if not processed_file.exists():
        with open(processed_file, "w", encoding="utf-8") as f:
            json.dump([], f)
    
    return image_dir, processed_file

def get_processed_files(processed_file):
    """Carrega a lista de arquivos já processados"""
    try:
        with open(processed_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"❌ Erro ao carregar arquivo de controle: {e}")
        return []

def save_processed_file(processed_file, file_path):
    """Adiciona um arquivo à lista de processados"""
    processed = get_processed_files(processed_file)
    processed.append(str(file_path))
    
    try:
        with open(processed_file, "w", encoding="utf-8") as f:
            json.dump(processed, f, indent=2)
    except Exception as e:
        logger.error(f"❌ Erro ao salvar arquivo de controle: {e}")

def process_new_files(image_dir, processed_file):
    """Processa novos arquivos JSON na pasta de imagens"""
    # Obter lista de arquivos já processados
    processed_files = get_processed_files(processed_file)
    
    # Encontrar todos os arquivos JSON
    json_files = list(image_dir.glob("*.json"))
    
    # Filtrar arquivos não processados
    new_files = [f for f in json_files if str(f) not in processed_files]
    
    if not new_files:
        logger.info("ℹ️ Nenhum arquivo novo encontrado para indexar.")
        return 0
    
    logger.info(f"🔍 Encontrados {len(new_files)} novos arquivos para indexar.")
    
    # Processar cada arquivo novo
    success_count = 0
    for json_file in new_files:
        logger.info(f"🔄 Processando arquivo: {json_file.name}")
        
        try:
            # Carregar o arquivo JSON
            with open(json_file, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            
            # Indexar no ChromaDB
            success = index_note_in_chroma(json_data)
            
            if success:
                logger.info(f"✅ Arquivo indexado com sucesso: {json_file.name}")
                save_processed_file(processed_file, json_file)
                success_count += 1
            else:
                logger.error(f"❌ Falha ao indexar arquivo: {json_file.name}")
        
        except Exception as e:
            logger.error(f"❌ Erro ao processar arquivo {json_file.name}: {e}")
    
    return success_count

def run_once():
    """Executa uma varredura única da pasta"""
    image_dir, processed_file = setup()
    return process_new_files(image_dir, processed_file)

def monitor_mode(interval=60):
    """Monitora continuamente a pasta por novos arquivos"""
    image_dir, processed_file = setup()
    
    logger.info(f"🔍 Iniciando monitoramento da pasta: {image_dir}")
    logger.info(f"⏱️ Intervalo de verificação: {interval} segundos")
    
    try:
        while True:
            count = process_new_files(image_dir, processed_file)
            if count > 0:
                logger.info(f"📊 {count} arquivos indexados nesta verificação")
            
            logger.info(f"💤 Aguardando próxima verificação em {interval} segundos...")
            time.sleep(interval)
    
    except KeyboardInterrupt:
        logger.info("👋 Monitoramento interrompido pelo usuário")
        sys.exit(0)

def main():
    """Função principal"""
    print("\n" + "=" * 60)
    print("🤖 AUTO INDEXADOR DE NOTAS PARA CHROMADB")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        # Modo de monitoramento contínuo
        interval = 60  # Padrão: 1 minuto
        
        if len(sys.argv) > 2:
            try:
                interval = int(sys.argv[2])
            except ValueError:
                logger.warning(f"⚠️ Intervalo inválido: {sys.argv[2]}. Usando padrão de 60 segundos.")
        
        monitor_mode(interval)
    else:
        # Modo de execução única
        count = run_once()
        print(f"\n📊 Resumo:")
        print(f"- {count} novos arquivos indexados")
        print("\nPara monitoramento contínuo, execute:")
        print("python scripts/auto_indexer.py --monitor [intervalo_em_segundos]")

if __name__ == "__main__":
    main()
