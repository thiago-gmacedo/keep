#!/usr/bin/env python3
"""
OCR de Notas Manuscritas - Extrator de texto manuscrito usando OpenAI Vision API

"""

import openai
import gkeepapi
import base64
import os
import sys
import time
import getpass
import tempfile
import shutil
import requests
import json
from pathlib import Path
from PIL import Image
from datetime import datetime, timezone

# Importar ChromaIndexer para indexação semântica
try:
    from .chroma_indexer import index_note_in_chroma
    CHROMA_AVAILABLE = True
except ImportError:
    try:
        # Fallback para importação absoluta
        from src.chroma_indexer import index_note_in_chroma
        CHROMA_AVAILABLE = True
    except ImportError:
        CHROMA_AVAILABLE = False
        print("⚠️ Aviso: ChromaIndexer não encontrado. A indexação semântica não estará disponível.")

MODEL_NAME = "gpt-4o"  # modelo atual com suporte a visão
IMAGE_DIR = Path(__file__).parent.parent / "images"  # Diretório para salvar imagens (raiz do projeto)
PROCESSED_NOTES_FILE = Path(__file__).parent.parent / ".processed_notes.json"  # Arquivo para registro de notas processadas

# Flag para controlar a indexação no ChromaDB
ENABLE_CHROMA_INDEXING = True  # Por padrão, ativar indexação


def convert_json_to_obsidian(json_data, output_folder="obsidian_notes"):
    """
    Converte dados JSON para arquivo Markdown do Obsidian
    
    Args:
        json_data (dict): Dados JSON estruturados
        output_folder (str): Diretório de saída (padrão: obsidian_notes)
    
    Returns:
        bool: True se conversão foi bem-sucedida, False caso contrário
    """
    try:
        # Importar dinamicamente para evitar problemas de importação circular
        import importlib.util
        
        # Caminho para o módulo obsidian_writer (agora na mesma pasta)
        obsidian_writer_path = Path(__file__).parent / "obsidian_writer.py"
        
        # Carregar o módulo dinamicamente
        spec = importlib.util.spec_from_file_location("obsidian_writer", obsidian_writer_path)
        obsidian_writer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(obsidian_writer)
        
        # Validar estrutura do JSON
        if not obsidian_writer.validate_json_structure(json_data):
            print("⚠️ Estrutura JSON inválida para conversão Obsidian")
            return False
        
        # Converter para Obsidian
        obsidian_writer.json_to_obsidian(json_data, output_folder)
        return True
        
    except Exception as e:
        print(f"⚠️ Erro ao converter para Obsidian: {e}")
        return False


def encode_image_to_base64(path):
    """Converte uma imagem para base64"""
    try:
        return base64.b64encode(Path(path).read_bytes()).decode()
    except Exception as e:
        sys.exit(f"Erro ao processar a imagem: {e}")


def transcribe_handwriting(image_path: str) -> str:
    """Transcreve texto manuscrito de uma imagem usando a API OpenAI Vision"""
    # Verificar extensão da imagem
    valid_extensions = ['.png', '.jpg', '.jpeg']
    if Path(image_path).suffix.lower() not in valid_extensions:
        sys.exit(f"Extensão não suportada. Use: {', '.join(valid_extensions)}")
    
    try:
        base64_img = encode_image_to_base64(image_path)
        
        response = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Todo o texto utilizado para gerar o JSON deve ser extraido da imagem."
                                "A imagem contém texto manuscrito que deve ser transcrito e organizado."
                                "A transcrição deve ser feita de forma precisa e fiel ao conteúdo da imagem"
                                "caso alguma parte fique ilegivel, use a logica para completar a lacuna."
                                "Todo a imagem virá dividida em blocos de texto, tarefas, notas e lembretes."
                                "Organize o seguinte texto OCR em formato JSON com os campos:"
                                "title (se houver, ou o dia neste formato dia/mes/ano - segunda-feira(dia da semana)),"
                                "Todas as partes devem vir encaixadas em algum dos campos definidos" 
                                "data (data encontrada no texto ou deixe vazio),"
                                "summary (resuma o conteúdo em uma frase),"
                                "keywords (até 5 palavras-chave relevantes),"
                                "tasks (lista de tarefas com status done ou todo),"
                                "notes (lista de anotações gerais),"
                                "reminders (lista de lembretes, coisas a lembrar ou não esquecer)."
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_img}"}
                        }
                    ],
                }
            ],
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        sys.exit(f"Erro da API OpenAI: {e}")
    except Exception as e:
        sys.exit(f"Erro ao transcrever texto: {e}")


def process_single_image(img_path):
    """Processa uma única imagem local (funcionalidade original)"""
    if not Path(img_path).is_file():
        sys.exit("❌ Arquivo não encontrado.")
    
    # Transcrever o texto manuscrito
    print("🔍 Processando a imagem...")
    texto = transcribe_handwriting(img_path)
    print("\n📄 Transcrição:")
    print("-" * 50)
    print(texto)
    print("-" * 50)
    
    # Salvar transcrição em arquivo
    try:
        # Detectar se o conteúdo é JSON válido
        json_data = None
        json_content = None
        
        # Tentar extrair JSON de markdown code blocks primeiro
        import re
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', texto, re.DOTALL | re.IGNORECASE)
        if json_match:
            json_content = json_match.group(1).strip()
        else:
            # Se não há code blocks, tentar o texto inteiro
            json_content = texto.strip()
        
        try:
            json_data = json.loads(json_content)
            # É JSON válido, salvar como .json
            out_file = Path(img_path).with_suffix(".json")
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            print(f"✅ JSON estruturado salvo em {out_file}")
            
            # Automaticamente converter para Obsidian
            print("🔄 Convertendo automaticamente para Obsidian...")
            if convert_json_to_obsidian(json_data):
                print("✅ Arquivo Obsidian gerado com sucesso!")
            else:
                print("⚠️ Falha na conversão para Obsidian")
            
            # Indexar no ChromaDB para busca semântica
            if CHROMA_AVAILABLE and ENABLE_CHROMA_INDEXING:
                print("🔄 Indexando no ChromaDB para busca semântica...")
                if index_note_in_chroma(json_data):
                    print("✅ Nota indexada com sucesso no ChromaDB!")
                else:
                    print("⚠️ Falha na indexação no ChromaDB")
                
        except json.JSONDecodeError:
            # Não é JSON válido, salvar como .txt
            out_file = Path(img_path).with_suffix(".txt")
            out_file.write_text(texto, encoding="utf-8")
            print(f"✅ Transcrição salva em {out_file}")
    except Exception as e:
        print(f"❌ Erro ao salvar o arquivo de saída: {e}")


def main():
    """Função principal do programa"""
    # Verificar argumentos
    if len(sys.argv) == 1:
        # Modo local - usar a imagem padrão
        img_path = Path(__file__).parent / "images" / "ink.png"
        print(f"🖼️ Modo Local: Usando imagem padrão: {img_path}")
        process_single_image(str(img_path))
    elif len(sys.argv) == 2 and sys.argv[1] == "--help":
        # Exibir ajuda
        print("\n📋 Uso do OCR de Notas Manuscritas:")
        print("  python ocr_extractor.py                     # Processar imagem padrão")
        print("  python ocr_extractor.py imagem.png          # Processar imagem específica")
        print("  python ocr_extractor.py MinhaLabel          # Processar notas do Google Keep com esta label")
        print("\nOpções:")
        print("  --no-index, --disable-indexing              # Desativar indexação no ChromaDB")
        print("  --help                                      # Exibir esta ajuda")
        sys.exit(0)
    elif len(sys.argv) == 2 and (Path(sys.argv[1]).is_file() or sys.argv[1].startswith("/")):
        # Modo local - imagem específica
        print(f"🖼️ Modo Local: Processando imagem específica: {sys.argv[1]}")
        process_single_image(sys.argv[1])
    elif len(sys.argv) == 2:
        # Modo Google Keep - processar notas com a label especificada
        print(f"🔄 Modo Google Keep: Buscando notas com a label '{sys.argv[1]}'")
        process_keep_notes(sys.argv[1])
    else:
        sys.exit("📋 Uso:\n"
                 "1. Para processar uma imagem local com a imagem padrão:\n"
                 "   python ocr_extractor.py\n\n"
                 "2. Para processar uma imagem local específica:\n"
                 "   python ocr_extractor.py caminho/para/sua/imagem.png\n\n"
                 "3. Para processar notas do Google Keep com uma label específica:\n"
                 "   python ocr_extractor.py MinhaLabel")


def connect_to_keep():
    """Conecta à conta do Google Keep usando master token"""
    keep = gkeepapi.Keep()
    
    # Carregar configuração
    config = load_keep_credentials()
    email = config.get('GOOGLE_EMAIL')
    master_token = config.get('GOOGLE_MASTER_TOKEN')
    
    # Verifica se as credenciais estão no arquivo de configuração
    if not email or not master_token:
        sys.exit("❌ Credenciais do Google Keep não encontradas."
                "\nPor favor, configure o GOOGLE_EMAIL e o GOOGLE_MASTER_TOKEN no arquivo .env/config"
                "\nVeja CONFIG.md para instruções sobre como obter o master token.")
        
    try:
        # Tentar fazer login usando o master token
        print(f"🔑 Autenticando com a conta {email} usando master token...")
        keep.resume(email, master_token)
        
        print(f"✅ Conectado com sucesso à conta Google Keep!")
        return keep
    except Exception as e:
        error_message = str(e)
        sys.exit(f"❌ Erro de login no Google Keep: {error_message}\n"
                "Possíveis soluções:\n"
                "1. Verifique se o email está correto\n"
                "2. O master token pode ter expirado ou ser inválido\n"
                "3. Gere um novo master token seguindo as instruções em CONFIG.md\n"
                "4. Configure suas credenciais no arquivo .env/config")


def load_keep_credentials():
    """Carrega as credenciais do Google Keep do arquivo de configuração"""
    env_file = Path(__file__).parent.parent / '.env' / 'config'
    config = {}
    
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            config[key] = value
        except Exception as e:
            print(f"Aviso: Não foi possível ler o arquivo de configuração: {e}")
    
    # Se o arquivo ainda contém a senha antiga (compatibilidade), avisa para atualizar
    if 'GOOGLE_PASSWORD' in config:
        print("\n⚠️ Aviso: Seu arquivo de configuração ainda está usando o formato antigo (GOOGLE_PASSWORD).")
        print("Por motivos de segurança, recomendamos atualizar para usar o master token.")
        print("Veja as instruções em CONFIG.md sobre como obter e configurar o master token.\n")
    
    return config


def save_keep_credentials(email, master_token=None):
    """Salva as credenciais do Google Keep no arquivo de configuração"""
    env_dir = Path(__file__).parent.parent / '.env'
    env_file = env_dir / 'config'
    
    # Criar diretório .env se não existir
    if not env_dir.exists():
        env_dir.mkdir()
    
    config = load_keep_credentials() or {}
    config['GOOGLE_EMAIL'] = email
    
    # Salvar master token apenas se fornecido
    if master_token:
        config['GOOGLE_MASTER_TOKEN'] = master_token
    
    # Manter a chave OpenAI se existir
    if 'OPENAI_API_KEY' not in config:
        config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY', 'sua-chave-api-aqui')
    
    try:
        with open(env_file, 'w') as f:
            f.write("# Arquivo de configuração para o OCR de Notas Manuscritas\n")
            f.write("# Chave da API OpenAI e credenciais do Google Keep\n\n")
            
            for key, value in config.items():
                f.write(f"{key}={value}\n")
    except Exception as e:
        print(f"Aviso: Não foi possível salvar o arquivo de configuração: {e}")


def download_blob(blob, note_title, index, keep_instance=None):
    """Baixa qualquer tipo de blob (anexo) de uma nota do Google Keep com método simplificado"""
    # Se não foi passado keep_instance, tenta usar a variável global
    if keep_instance is None:
        # Tenta importar e usar variável global se disponível
        try:
            global keep
            keep_instance = keep
        except NameError:
            print("❌ Instância do Google Keep não disponível")
            return None
    
    # Criar diretório se não existir
    if not IMAGE_DIR.exists():
        IMAGE_DIR.mkdir(parents=True)
    
    # Sanitizar o título para nome de arquivo
    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in note_title)
    safe_title = safe_title.strip().replace(" ", "_")
    if not safe_title:
        safe_title = "nota"
    
    # Identificador único: usar ID ou server_id do blob
    blob_id = None
    if hasattr(blob, 'id') and blob.id:
        blob_id = blob.id[:8]
    elif hasattr(blob, 'server_id') and blob.server_id:
        blob_id = blob.server_id[:8]
    
    # Timestamp para garantir unicidade
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # Nome do arquivo: titulo_timestamp_id_index.png
    file_name = f"{safe_title}_{timestamp}"
    if blob_id:
        file_name += f"_{blob_id}"
    file_name += f"_{index+1}.png"
    
    file_path = IMAGE_DIR / file_name
    print(f"🏷️ Nome do arquivo: {file_name}")
    
    # Método Único: implementa estratégia de fallback em um único método
    
    # Estratégia 1: Usar getMediaLink (método oficial e preferido)
    try:
        print("🔄 Tentando download via getMediaLink (método principal)...")
        media_url = keep_instance.getMediaLink(blob)
        if media_url:
            response = requests.get(media_url)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Imagem salva com sucesso via getMediaLink")
                return file_path
    except Exception as e:
        print(f"ℹ️ getMediaLink falhou: {e}")
    
    # Estratégia 2: Tenta acessar dados binários diretamente (para desenhos)
    try:
        print("🔄 Tentando acessar dados binários diretamente...")
        binary_data = None
        
        # Tenta extrair bytes do desenho, se disponível
        if hasattr(blob, 'drawable') and hasattr(blob.drawable, 'getBytes'):
            binary_data = blob.drawable.getBytes()
        
        if binary_data:
            with open(file_path, 'wb') as f:
                f.write(binary_data)
            print(f"✅ Imagem salva com sucesso via dados binários")
            return file_path
    except Exception as e:
        print(f"ℹ️ Acesso a dados binários falhou: {e}")
    
    # Estratégia 3: URL direta baseada no server_id
    try:
        if hasattr(blob, 'server_id') and blob.server_id:
            print("🔄 Tentando URL direta baseada no server_id...")
            server_id = blob.server_id
            api_url = f"https://keep.google.com/media/v2/{server_id}"
            response = requests.get(api_url)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Imagem salva com sucesso via URL direta")
                return file_path
    except Exception as e:
        print(f"ℹ️ URL direta falhou: {e}")
    
    print("❌ Todas as estratégias de download falharam")
    return None


# A função extract_drawing foi integrada ao download_blob para simplificar o código


def process_keep_notes(label_name):
    """Processa notas do Google Keep com a label especificada e criadas hoje"""
    # Conectar ao Google Keep
    global keep  # Tornar a variável global para uso em outras funções
    keep = connect_to_keep()
    
    # Encontrar a label especificada
    try:
        print(f"🔍 Buscando a label '{label_name}' no Google Keep...")
        label = keep.findLabel(label_name)
        if not label:
            sys.exit(f"❌ Label '{label_name}' não encontrada. Verifique se você criou esta label no Google Keep.")
    except Exception as e:
        sys.exit(f"❌ Erro ao buscar a label: {e}")
    
    # Opções de data: hoje, todas, ou apenas novas
    print("\nEscolha uma opção:")
    print("1. Processar apenas notas de hoje")
    print("2. Processar todas as notas com esta label")
    print("3. Processar apenas notas novas (não processadas anteriormente)")
    escolha = input("\nSua escolha [1/2/3]: ").strip()
    
    # Data atual (UTC)
    hoje = datetime.now(timezone.utc).date()
    if escolha == "2":
        print(f"🔍 Buscando todas as notas com a label '{label_name}'...")
    elif escolha == "3":
        print(f"🔍 Buscando notas não processadas anteriormente com a label '{label_name}'...")
    else:
        print(f"🔍 Buscando notas com a label '{label_name}' atualizadas hoje ({hoje.strftime('%d/%m/%Y')})...")
    
    # Encontrar notas com a label especificada
    try:
        notes_with_label = list(keep.find(labels=[label]))
    except Exception as e:
        sys.exit(f"❌ Erro ao buscar notas: {e}")
    
    # Mostrar total de notas encontradas com a label
    print(f"📋 Total de notas com a label '{label_name}': {len(notes_with_label)}")
    
    # Filtrar notas conforme a escolha
    if escolha == "1":
        # Apenas notas de hoje
        notes_to_process = [note for note in notes_with_label if note.timestamps.updated.date() == hoje]
    elif escolha == "3":
        # Apenas notas não processadas anteriormente
        notes_to_process = [note for note in notes_with_label 
                           if not is_note_processed(note.id, label_name)]
    else:
        # Todas as notas
        notes_to_process = notes_with_label
    
    if not notes_to_process:
        if escolha == "1":
            print(f"ℹ️ Nenhuma nota com a label '{label_name}' foi encontrada para a data de hoje.")
        elif escolha == "3":
            print(f"ℹ️ Todas as notas com a label '{label_name}' já foram processadas anteriormente.")
        else:
            print(f"ℹ️ Nenhuma nota com a label '{label_name}' foi encontrada.")
        return
    
    print(f"✅ Encontradas {len(notes_to_process)} notas para processar.")
    
    # Processar cada nota
    processed_count = 0
    skipped_count = 0
    
    for note in notes_to_process:
        print(f"\n{'=' * 50}")
        print(f"📝 Nota: {note.title or 'Sem título'} (ID: {note.id[:8]})")
        
        # Verificar se a nota já foi processada (verificação extra)
        if is_note_processed(note.id, label_name):
            print("⏭️ Esta nota já foi processada anteriormente. Pulando...")
            skipped_count += 1
            continue
            
        print(f"{'=' * 50}")
        
        # Verificar se a nota tem anexos (blobs)
        if note.blobs:
            print(f"📎 Encontrados {len(note.blobs)} anexos.")
            blobs_processed = False
            
            # Processar cada anexo
            for i, blob in enumerate(note.blobs):
                try:
                    print(f"\n🖼️ Processando anexo {i+1}...")
                    
                    # Caminho da imagem a ser processada
                    img_path = None
                    
                    # Abordagem simplificada: tentar baixar o anexo
                    try:
                        print("🔄 Baixando anexo...")
                        img_path = download_blob(blob, note.title or "sem_titulo", i, keep)
                        if img_path:
                            print(f"💾 Anexo salvo em: {img_path}")
                        else:
                            print("❌ Não foi possível baixar o anexo")
                            continue  # Passa para o próximo anexo
                    except Exception as download_error:
                        print(f"⚠️ Erro ao baixar anexo: {download_error}")
                        print("❌ Falha ao baixar anexo")
                        continue  # Passa para o próximo anexo
                    
                    # Verificar se é uma imagem válida
                    if img_path:
                        try:
                            with Image.open(img_path) as img:
                                img_format = img.format
                                print(f"✅ Imagem validada (Formato: {img_format})")
                        except Exception as img_error:
                            print(f"⚠️ O arquivo não é uma imagem válida: {img_error}")
                            continue
                    
                    # Transcrever o texto manuscrito
                    print("🔍 Executando OCR com OpenAI Vision...")
                    texto = transcribe_handwriting(str(img_path))
                    
                    # Exibir a transcrição
                    print("\n📄 Transcrição:")
                    print("-" * 50)
                    print(texto)
                    print("-" * 50)
                    
                    # Salvar a transcrição
                    try:
                        # Detectar se o conteúdo é JSON válido
                        json_data = None
                        json_content = None
                        
                        # Tentar extrair JSON de markdown code blocks primeiro
                        import re
                        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', texto, re.DOTALL | re.IGNORECASE)
                        if json_match:
                            json_content = json_match.group(1).strip()
                        else:
                            # Se não há code blocks, tentar o texto inteiro
                            json_content = texto.strip()
                        
                        try:
                            json_data = json.loads(json_content)
                            # É JSON válido, salvar como .json
                            out_file = img_path.with_suffix(".json")
                            with open(out_file, "w", encoding="utf-8") as f:
                                json.dump(json_data, f, indent=2, ensure_ascii=False)
                            print(f"✅ JSON estruturado salvo em: {out_file}")
                            
                            # Automaticamente converter para Obsidian
                            print("🔄 Convertendo automaticamente para Obsidian...")
                            if convert_json_to_obsidian(json_data):
                                print("✅ Arquivo Obsidian gerado com sucesso!")
                            else:
                                print("⚠️ Falha na conversão para Obsidian")
                            
                            # Indexar no ChromaDB para busca semântica
                            if CHROMA_AVAILABLE and ENABLE_CHROMA_INDEXING:
                                print("🔄 Indexando no ChromaDB para busca semântica...")
                                if index_note_in_chroma(json_data):
                                    print("✅ Nota indexada com sucesso no ChromaDB!")
                                else:
                                    print("⚠️ Falha na indexação no ChromaDB")
                                
                        except json.JSONDecodeError:
                            # Não é JSON válido, salvar como .txt
                            out_file = img_path.with_suffix(".txt")
                            out_file.write_text(texto, encoding="utf-8")
                            print(f"✅ Transcrição salva em: {out_file}")
                        blobs_processed = True
                    except Exception as e:
                        print(f"❌ Erro ao salvar o arquivo de saída: {e}")
                except Exception as e:
                    print(f"⚠️ Erro ao processar anexo {i+1}: {e}")
                    # Depurar informações sobre o blob quando há erro
                    debug_blob_info(blob)
            
            # Registrar a nota como processada apenas se pelo menos um blob foi processado com sucesso
            if blobs_processed:
                save_processed_note(note.id, label_name)
                processed_count += 1
        else:
            print("ℹ️ Esta nota não contém anexos (imagens).")
    
    # Resumo final
    print(f"\n{'=' * 50}")
    print(f"✅ Processamento concluído")
    print(f"- Notas processadas: {processed_count}")
    print(f"- Notas puladas (já processadas): {skipped_count}")
    print(f"- Total considerado: {len(notes_to_process)}")
    print(f"{'=' * 50}")


def debug_blob_info(blob):
    """Função para mostrar informações essenciais de um blob para diagnóstico"""
    print(f"\n🔍 Informações sobre o blob:")
    print(f"- Tipo: {type(blob).__name__}")
    
    # Mostrar apenas informações essenciais
    for attr in ['id', 'type', 'server_id']:
        if hasattr(blob, attr):
            print(f"- {attr}: {getattr(blob, attr)}")
    
    return blob


def load_api_key_from_env_file():
    """Carrega a chave da API OpenAI do arquivo .env/config se disponível"""
    config = load_keep_credentials()
    if config and 'OPENAI_API_KEY' in config:
        return config['OPENAI_API_KEY']
    return None


def load_processed_notes():
    """Carrega a lista de IDs de notas já processadas do arquivo de registro"""
    if not PROCESSED_NOTES_FILE.exists():
        return {}
    
    try:
        with open(PROCESSED_NOTES_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Erro ao carregar registro de notas processadas: {e}")
        return {}


def save_processed_note(note_id, label_name):
    """Adiciona uma nota ao registro de notas processadas"""
    processed_notes = load_processed_notes()
    
    # Organizar por label
    if label_name not in processed_notes:
        processed_notes[label_name] = []
    
    # Adicionar ID da nota se ainda não estiver na lista
    if note_id not in processed_notes[label_name]:
        processed_notes[label_name].append(note_id)
    
    try:
        with open(PROCESSED_NOTES_FILE, 'w') as f:
            json.dump(processed_notes, f, indent=2)
    except Exception as e:
        print(f"⚠️ Erro ao salvar registro de notas processadas: {e}")


def is_note_processed(note_id, label_name):
    """Verifica se uma nota já foi processada anteriormente"""
    processed_notes = load_processed_notes()
    
    return (label_name in processed_notes and 
            note_id in processed_notes[label_name])

if __name__ == "__main__":
    # Processar argumentos de linha de comando para opções
    disable_indexing = False
    
    # Verificar opções nos argumentos
    args_to_remove = []
    for i, arg in enumerate(sys.argv):
        if arg == "--no-index" or arg == "--disable-indexing":
            disable_indexing = True
            args_to_remove.append(i)
    
    # Remover argumentos de opção para não interferir com o processamento normal
    for i in sorted(args_to_remove, reverse=True):
        sys.argv.pop(i)
    
    # Desativar indexação se solicitado
    if disable_indexing:
        ENABLE_CHROMA_INDEXING = False
        print("ℹ️ Indexação no ChromaDB desativada pelo argumento de linha de comando")
    
    # Verificar API key para OpenAI
    api_key = os.environ.get("OPENAI_API_KEY") or load_api_key_from_env_file()
    
    if not api_key:
        sys.exit("Erro: Defina a variável de ambiente OPENAI_API_KEY ou configure-a no arquivo .env/config.")
    elif api_key.startswith("sua-chave-api-aqui"):
        sys.exit("Erro: Substitua 'sua-chave-api-aqui' pela sua chave real da API OpenAI no arquivo .env/config.")
    
    try:
        # Configurar cliente OpenAI com a API key
        openai.api_key = api_key
        
        # Verificar se o arquivo de configuração possui as credenciais do Google Keep
        # para alertar o usuário antecipadamente
        if len(sys.argv) > 1 and not Path(sys.argv[1]).is_file() and not sys.argv[1].startswith("/"):
            config = load_keep_credentials()
            if not config.get('GOOGLE_EMAIL') or not config.get('GOOGLE_MASTER_TOKEN'):
                print("⚠️ Aviso: Credenciais do Google Keep não configuradas!")
                print("Para usar a funcionalidade do Google Keep, configure GOOGLE_EMAIL e GOOGLE_MASTER_TOKEN")
                print("no arquivo .env/config conforme instruções em CONFIG.md")
                choice = input("Deseja continuar mesmo assim? [s/N]: ")
                if choice.lower() != 's':
                    sys.exit("Operação cancelada pelo usuário.")
        
        # Exibir versão atual
        versao = "0.8.0"
        print(f"\n{'=' * 58}\n{'📝 OCR de Notas Manuscritas - Versão ' + versao:^58}\n{'=' * 58}")
        
        main()
    except KeyboardInterrupt:
        sys.exit("\nOperação cancelada pelo usuário.")
    except Exception as e:
        sys.exit(f"Erro não esperado: {e}")

# Função detect_blob_type removida por não estar sendo utilizada
