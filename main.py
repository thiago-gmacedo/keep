#!/usr/bin/env python3
"""
OCR Keep → Obsidian + Vector DB v1.0.0
Main Pipeline - Centralizador de todo o fluxo de processamento de notas manuscritas

Este módulo executa o pipeline completo:
1. Conecta ao Google Keep
2. Busca novas imagens (não processadas) 
3. Executa OCR
4. Estrutura com LLM
5. Gera arquivos .md no padrão Obsidian
6. Indexa no ChromaDB
7. Move imagens processadas

Autor: Thiago Macedom
Data: 29/05/2025
Versão: 1.0.0
"""

import sys
import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Adicionar diretório raiz ao path para importações
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

# Importações dos módulos existentes
try:
    # Importar funções de conectividade e credenciais do Google Keep
    from ocr_extractor import (
        connect_to_keep, 
        load_keep_credentials,
        transcribe_handwriting,
        download_blob,
        encode_image_to_base64
    )
    
    # Importar módulo de geração Obsidian
    from src.obsidian_writer import json_to_obsidian, validate_json_structure
    
    # Importar módulo de indexação ChromaDB
    from src.chroma_indexer import index_note_in_chroma
    
    print("✅ Todos os módulos importados com sucesso")
    
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("Certifique-se de que todos os módulos estão no local correto")
    sys.exit(1)

# Informações de versão
__version__ = "1.0.0"
__author__ = "Thiago Macedom"
__date__ = "29/05/2025"

# Configurações
IMAGES_DIR = ROOT_DIR / "images"
PROCESSED_DIR = IMAGES_DIR / "processed"
OBSIDIAN_DIR = ROOT_DIR / "obsidian_notes"
PROCESSED_NOTES_FILE = ROOT_DIR / ".processed_notes.json"

# Criar diretórios necessários
IMAGES_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)
OBSIDIAN_DIR.mkdir(exist_ok=True)


def setup_api_keys():
    """Configura as chaves de API necessárias"""
    print("🔑 Verificando configuração de APIs...")
    
    # Carregar credenciais do arquivo de configuração
    config = load_keep_credentials()
    
    # Verificar chave OpenAI
    openai_key = config.get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY')
    if not openai_key or openai_key.startswith('sua-chave'):
        raise ValueError("❌ Chave da API OpenAI não configurada no arquivo .env/config")
    
    # Configurar OpenAI
    try:
        import openai
        openai.api_key = openai_key
    except ImportError:
        print("⚠️ OpenAI não instalado, mas chave configurada")
    
    # Verificar credenciais Google Keep
    email = config.get('GOOGLE_EMAIL')
    master_token = config.get('GOOGLE_MASTER_TOKEN')
    
    if not email or not master_token:
        raise ValueError("❌ Credenciais do Google Keep não configuradas no arquivo .env/config")
    
    print("✅ APIs configuradas com sucesso")
    return config


def load_processed_notes() -> Dict[str, List[str]]:
    """Carrega a lista de IDs de notas já processadas"""
    if not PROCESSED_NOTES_FILE.exists():
        return {}
    
    try:
        with open(PROCESSED_NOTES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Erro ao carregar registro de notas processadas: {e}")
        return {}


def save_processed_note(note_id: str, label_name: str = "main_pipeline"):
    """Adiciona uma nota ao registro de notas processadas"""
    processed_notes = load_processed_notes()
    
    if label_name not in processed_notes:
        processed_notes[label_name] = []
    
    if note_id not in processed_notes[label_name]:
        processed_notes[label_name].append(note_id)
    
    try:
        with open(PROCESSED_NOTES_FILE, 'w', encoding='utf-8') as f:
            json.dump(processed_notes, f, indent=2, ensure_ascii=False)
        print(f"📝 Nota {note_id[:8]} registrada como processada")
    except Exception as e:
        print(f"⚠️ Erro ao salvar registro: {e}")


def is_note_processed(note_id: str, label_name: str = "main_pipeline") -> bool:
    """Verifica se uma nota já foi processada"""
    processed_notes = load_processed_notes()
    return (label_name in processed_notes and 
            note_id in processed_notes[label_name])


def get_new_notes_with_images(keep, label_name: Optional[str] = None) -> List[Any]:
    """
    Busca notas de HOJE com imagens que ainda não foram processadas
    
    Args:
        keep: Instância conectada do Google Keep
        label_name: Nome da label para filtrar (opcional)
    
    Returns:
        Lista de notas de hoje não processadas com anexos de imagem
    """
    from datetime import timezone
    
    # Data atual (UTC) - filtra apenas notas de hoje
    hoje = datetime.now(timezone.utc).date()
    print(f"🔍 Buscando notas de HOJE ({hoje.strftime('%d/%m/%Y')}) com imagens não processadas...")
    
    try:
        if label_name:
            print(f"🏷️ Filtrando por label: {label_name}")
            label = keep.findLabel(label_name)
            if not label:
                print(f"⚠️ Label '{label_name}' não encontrada")
                return []
            notes = list(keep.find(labels=[label]))
        else:
            print("📋 Buscando em todas as notas")
            notes = list(keep.all())
        
        print(f"📊 Total de notas encontradas: {len(notes)}")
        
        # Filtrar notas de HOJE
        notes_today = [note for note in notes if note.timestamps.updated.date() == hoje]
        print(f"📅 Notas de hoje: {len(notes_today)}")
        
        # Filtrar notas com anexos
        notes_with_blobs = []
        for note in notes_today:
            if hasattr(note, 'blobs') and note.blobs:
                notes_with_blobs.append(note)
        
        print(f"📎 Notas de hoje com anexos: {len(notes_with_blobs)}")
        
        # Filtrar notas não processadas
        new_notes = []
        pipeline_label = f"main_pipeline_{label_name}" if label_name else "main_pipeline"
        
        for note in notes_with_blobs:
            if not is_note_processed(note.id, pipeline_label):
                new_notes.append(note)
        
        print(f"🆕 Notas de hoje novas para processar: {len(new_notes)}")
        return new_notes
        
    except Exception as e:
        print(f"❌ Erro ao buscar notas: {e}")
        return []


def download_note_images(keep, note) -> List[Path]:
    """
    Baixa todas as imagens de uma nota
    
    Args:
        keep: Instância do Google Keep
        note: Nota do Google Keep
    
    Returns:
        Lista de caminhos das imagens baixadas
    """
    print(f"📥 Baixando imagens da nota: {note.title or 'Sem título'}")
    
    downloaded_images = []
    
    for i, blob in enumerate(note.blobs):
        try:
            print(f"📷 Processando anexo {i+1}/{len(note.blobs)}...")
            
            # Definir keep como variável global temporariamente para compatibilidade
            import ocr_extractor
            ocr_extractor.keep = keep
            
            # Baixar o blob usando a função existente
            img_path = download_blob(blob, note.title or "sem_titulo", i)
            
            if img_path and img_path.exists():
                # Mover para o diretório correto se necessário
                if img_path.parent != IMAGES_DIR:
                    new_path = IMAGES_DIR / img_path.name
                    shutil.move(str(img_path), str(new_path))
                    img_path = new_path
                
                print(f"✅ Imagem salva: {img_path}")
                downloaded_images.append(img_path)
            else:
                print(f"❌ Falha ao baixar anexo {i+1}")
                
        except Exception as e:
            print(f"⚠️ Erro ao processar anexo {i+1}: {e}")
            continue
    
    return downloaded_images


def process_image_ocr(image_path: Path) -> str:
    """
    Executa OCR em uma imagem
    
    Args:
        image_path: Caminho da imagem
    
    Returns:
        Texto extraído da imagem
    """
    print(f"🔍 Executando OCR em: {image_path.name}")
    
    try:
        # Validar que é uma imagem
        from PIL import Image
        with Image.open(image_path) as img:
            print(f"📊 Imagem validada - Formato: {img.format}, Tamanho: {img.size}")
        
        # Executar OCR usando a função existente
        extracted_text = transcribe_handwriting(str(image_path))
        
        print(f"✅ OCR concluído - {len(extracted_text)} caracteres extraídos")
        return extracted_text
        
    except Exception as e:
        print(f"❌ Erro no OCR: {e}")
        raise


def parse_text_to_json(text: str) -> Optional[Dict[str, Any]]:
    """
    Converte texto extraído em JSON estruturado
    
    Args:
        text: Texto extraído do OCR
    
    Returns:
        Dicionário JSON estruturado ou None se falhar
    """
    print("🧠 Estruturando texto com LLM...")
    
    try:
        # Tentar extrair JSON do texto (pode vir com markdown code blocks)
        import re
        
        # Primeiro, tentar encontrar blocos de código JSON
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL | re.IGNORECASE)
        if json_match:
            json_content = json_match.group(1).strip()
        else:
            # Se não há code blocks, usar o texto inteiro
            json_content = text.strip()
        
        # Tentar fazer parse do JSON
        json_data = json.loads(json_content)
        
        # Validar estrutura básica
        required_fields = ['title', 'summary', 'keywords', 'tasks', 'notes', 'reminders']
        for field in required_fields:
            if field not in json_data:
                json_data[field] = [] if field in ['keywords', 'tasks', 'notes', 'reminders'] else ""
        
        print("✅ Texto estruturado com sucesso em JSON")
        return json_data
        
    except json.JSONDecodeError:
        print("⚠️ Não foi possível estruturar como JSON - salvando como texto puro")
        return None
    except Exception as e:
        print(f"❌ Erro na estruturação: {e}")
        return None


def save_json_data(json_data: Dict[str, Any], image_path: Path) -> Path:
    """
    Salva dados JSON estruturados
    
    Args:
        json_data: Dados estruturados
        image_path: Caminho da imagem original
    
    Returns:
        Caminho do arquivo JSON salvo
    """
    json_path = image_path.with_suffix('.json')
    
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 JSON salvo: {json_path}")
        return json_path
        
    except Exception as e:
        print(f"❌ Erro ao salvar JSON: {e}")
        raise


def save_text_data(text: str, image_path: Path) -> Path:
    """
    Salva texto puro (fallback quando JSON falha)
    
    Args:
        text: Texto extraído
        image_path: Caminho da imagem original
    
    Returns:
        Caminho do arquivo de texto salvo
    """
    text_path = image_path.with_suffix('.txt')
    
    try:
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"📄 Texto salvo: {text_path}")
        return text_path
        
    except Exception as e:
        print(f"❌ Erro ao salvar texto: {e}")
        raise


def generate_obsidian_note(json_data: Dict[str, Any]) -> bool:
    """
    Gera arquivo Markdown para Obsidian
    
    Args:
        json_data: Dados estruturados
    
    Returns:
        True se geração foi bem-sucedida
    """
    print("📚 Gerando nota Obsidian...")
    
    try:
        # Validar estrutura do JSON
        if not validate_json_structure(json_data):
            print("⚠️ Estrutura JSON inválida para Obsidian")
            return False
        
        # Gerar arquivo Obsidian
        json_to_obsidian(json_data, str(OBSIDIAN_DIR))
        print("✅ Nota Obsidian gerada com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar nota Obsidian: {e}")
        return False


def index_in_chromadb(json_data: Dict[str, Any]) -> bool:
    """
    Indexa dados no ChromaDB para busca semântica
    
    Args:
        json_data: Dados estruturados
    
    Returns:
        True se indexação foi bem-sucedida
    """
    print("🧠 Indexando no ChromaDB...")
    
    try:
        success = index_note_in_chroma(json_data)
        if success:
            print("✅ Dados indexados no ChromaDB com sucesso")
        else:
            print("⚠️ Falha na indexação no ChromaDB")
        return success
        
    except Exception as e:
        print(f"❌ Erro na indexação ChromaDB: {e}")
        return False


def move_processed_image(image_path: Path) -> bool:
    """
    Move imagem processada para o diretório processed/
    
    Args:
        image_path: Caminho da imagem processada
    
    Returns:
        True se movimentação foi bem-sucedida
    """
    try:
        processed_path = PROCESSED_DIR / image_path.name
        shutil.move(str(image_path), str(processed_path))
        print(f"📁 Imagem movida para: {processed_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao mover imagem: {e}")
        return False


def process_single_image(image_path: Path, note_id: str = None) -> Dict[str, bool]:
    """
    Processa uma única imagem através de todo o pipeline
    
    Args:
        image_path: Caminho da imagem
        note_id: ID da nota (opcional)
    
    Returns:
        Dicionário com status de cada etapa
    """
    print(f"\n{'='*60}")
    print(f"🔄 Processando imagem: {image_path.name}")
    print(f"{'='*60}")
    
    results = {
        'ocr': False,
        'json_parsing': False,
        'obsidian': False,
        'chromadb': False,
        'move_image': False
    }
    
    try:
        # Etapa 1: OCR
        extracted_text = process_image_ocr(image_path)
        results['ocr'] = True
        
        # Etapa 2: Estruturação em JSON
        json_data = parse_text_to_json(extracted_text)
        
        if json_data:
            # Salvar JSON
            save_json_data(json_data, image_path)
            results['json_parsing'] = True
            
            # Etapa 3: Gerar nota Obsidian
            if generate_obsidian_note(json_data):
                results['obsidian'] = True
            
            # Etapa 4: Indexar no ChromaDB
            if index_in_chromadb(json_data):
                results['chromadb'] = True
        else:
            # Fallback: salvar como texto puro
            save_text_data(extracted_text, image_path)
            print("💾 Conteúdo salvo como texto puro")
        
        # Etapa 5: Mover imagem processada
        if move_processed_image(image_path):
            results['move_image'] = True
        
        print(f"✅ Processamento de {image_path.name} concluído")
        
    except Exception as e:
        print(f"❌ Erro no processamento de {image_path.name}: {e}")
    
    return results


def run_pipeline(label_name: Optional[str] = None):
    """
    Executa o pipeline completo de processamento
    
    Args:
        label_name: Nome da label para filtrar notas (opcional)
    """
    print(f"\n{'='*80}")
    print(f"🚀 OCR KEEP → OBSIDIAN + VECTOR DB v{__version__}")
    print(f"📝 PIPELINE DE PROCESSAMENTO DE NOTAS MANUSCRITAS")
    print(f"👤 Autor: {__author__} | 📅 Data: {__date__}")
    print(f"{'='*80}")
    
    start_time = datetime.now()
    
    try:
        # Etapa 1: Configurar APIs
        setup_api_keys()
        
        # Etapa 2: Conectar ao Google Keep
        print("\n🔗 Conectando ao Google Keep...")
        keep = connect_to_keep()
        
        # Etapa 3: Buscar novas notas com imagens
        new_notes = get_new_notes_with_images(keep, label_name)
        
        if not new_notes:
            print("ℹ️ Nenhuma nota nova para processar")
            return
        
        # Estatísticas
        total_notes = len(new_notes)
        processed_notes = 0
        failed_notes = 0
        total_images = 0
        processed_images = 0
        
        pipeline_label = f"main_pipeline_{label_name}" if label_name else "main_pipeline"
        
        # Processar cada nota
        for note_idx, note in enumerate(new_notes, 1):
            print(f"\n{'='*60}")
            print(f"📝 Processando nota {note_idx}/{total_notes}")
            print(f"📋 Título: {note.title or 'Sem título'}")
            print(f"🆔 ID: {note.id[:8]}...")
            print(f"{'='*60}")
            
            try:
                # Baixar imagens da nota
                images = download_note_images(keep, note)
                total_images += len(images)
                
                if not images:
                    print("⚠️ Nenhuma imagem baixada desta nota")
                    continue
                
                # Processar cada imagem
                note_success = True
                for image_path in images:
                    results = process_single_image(image_path, note.id)
                    
                    # Verificar se pelo menos OCR funcionou
                    if results['ocr']:
                        processed_images += 1
                    else:
                        note_success = False
                
                # Marcar nota como processada se pelo menos uma imagem foi processada
                if note_success and processed_images > 0:
                    save_processed_note(note.id, pipeline_label)
                    processed_notes += 1
                else:
                    failed_notes += 1
                    
            except Exception as e:
                print(f"❌ Erro ao processar nota {note.title or 'sem título'}: {e}")
                failed_notes += 1
                continue
        
        # Resumo final
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n{'='*80}")
        print(f"✅ PIPELINE CONCLUÍDO")
        print(f"{'='*80}")
        print(f"⏱️ Duração: {duration}")
        print(f"📊 Estatísticas:")
        print(f"   📝 Notas processadas: {processed_notes}/{total_notes}")
        print(f"   ❌ Notas com falha: {failed_notes}")
        print(f"   🖼️ Imagens processadas: {processed_images}/{total_images}")
        print(f"📁 Diretórios:")
        print(f"   🖼️ Imagens processadas: {PROCESSED_DIR}")
        print(f"   📚 Notas Obsidian: {OBSIDIAN_DIR}")
        print(f"   🧠 ChromaDB: ./chroma_db")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"❌ Erro crítico no pipeline: {e}")
        raise


if __name__ == "__main__":
    """
    Ponto de entrada principal
    Aceita argumentos opcionais para filtrar por label
    """
    
    # Verificar argumentos de linha de comando
    label_filter = None
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            print("\n📋 USO DO PIPELINE:")
            print("  python main.py              # Processar todas as notas")
            print("  python main.py LABEL        # Processar notas com label específica")
            print("  python main.py --help       # Exibir esta ajuda")
            print("\nEXEMPLOS:")
            print("  python main.py diario       # Processar notas com label 'diario'")
            print("  python main.py OCR          # Processar notas com label 'OCR'")
            sys.exit(0)
        else:
            label_filter = sys.argv[1]
            print(f"🏷️ Filtrando por label: {label_filter}")
    
    try:
        run_pipeline(label_filter)
    except KeyboardInterrupt:
        print("\n⏹️ Pipeline interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")
        sys.exit(1)
