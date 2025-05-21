#!/usr/bin/env python3
"""
Extrator de desenhos do Google Keep
Script simplificado para extrair apenas desenhos de notas do Google Keep
"""

import gkeepapi
import os
import sys
from pathlib import Path
import requests
from PIL import Image

# Diretório para salvar imagens
IMAGE_DIR = Path(__file__).parent / "image"  

def load_keep_credentials():
    """Carrega as credenciais do Google Keep do arquivo de configuração"""
    env_file = Path(__file__).parent / '.env' / 'config'
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
    
    return config

def connect_to_keep():
    """Conecta à conta do Google Keep usando master token"""
    keep = gkeepapi.Keep()
    
    # Carregar configuração
    config = load_keep_credentials()
    email = config.get('GOOGLE_EMAIL')
    master_token = config.get('GOOGLE_MASTER_TOKEN')
    
    # Verifica se as credenciais estão no arquivo de configuração
    if not email or not master_token:
        sys.exit("❌ Credenciais do Google Keep não encontradas.\n"
                "Por favor, configure o GOOGLE_EMAIL e o GOOGLE_MASTER_TOKEN no arquivo .env/config")
        
    try:
        # Tentar fazer login usando o master token
        print(f"🔑 Autenticando com a conta {email} usando master token...")
        keep.resume(email, master_token)
        
        print(f"✅ Conectado com sucesso à conta Google Keep!")
        return keep
    except Exception as e:
        error_message = str(e)
        sys.exit(f"❌ Erro de login no Google Keep: {error_message}")

def debug_blob_basic(blob):
    """
    Função simplificada que mostra informações básicas de um blob para diagnóstico.
    """
    print("\n📋 Informações do blob:")
    
    # Mostrar apenas informações essenciais
    for attr in ['id', 'type', 'server_id']:
        if hasattr(blob, attr):
            print(f"- {attr}: {getattr(blob, attr)}")
    
    return None

def extract_drawing_alternative(keep, blob, file_path):
    """Tenta extrair um desenho usando métodos alternativos quando getMediaLink falha"""
    # Métodos alternativos para extração de desenhos
    extraction_methods = [
        # Método 1: via atributo drawable direto
        lambda: blob.drawable.getBytes() if hasattr(blob, 'drawable') and hasattr(blob.drawable, 'getBytes') else None,
        
        # Método 2: via drawing_data
        lambda: blob.drawable.drawing_data if hasattr(blob, 'drawable') and hasattr(blob.drawable, 'drawing_data') else None,
        
        # Método 3: via blob interno
        lambda: blob.blob.drawable.getBytes() if hasattr(blob, 'blob') and hasattr(blob.blob, 'drawable') 
                and hasattr(blob.blob.drawable, 'getBytes') else None,
        
        # Método 4: via método específico para mídia binária
        lambda: keep.getMediaData(blob) if hasattr(keep, 'getMediaData') else None
    ]
    
    # Tentar cada método alternativo
    for i, extract_method in enumerate(extraction_methods):
        try:
            print(f"🔄 Tentando método alternativo {i+1}...")
            data = extract_method()
            if data:
                # Salvar os dados
                with open(file_path, 'wb') as f:
                    f.write(data)
                print(f"✅ Desenho extraído com método alternativo {i+1}")
                return True
        except Exception as e:
            print(f"⚠️ Método {i+1} falhou: {str(e)[:100]}")
    
    # Tentar acessar o server_id em diferentes locais do objeto blob
    blob_paths = [
        lambda: blob.server_id if hasattr(blob, 'server_id') else None,
        lambda: blob.blob.server_id if hasattr(blob, 'blob') and hasattr(blob.blob, 'server_id') else None,
        lambda: blob.media_id if hasattr(blob, 'media_id') else None,
        lambda: blob.parent_id if hasattr(blob, 'parent_id') else None
    ]
    
    for path_func in blob_paths:
        try:
            server_id = path_func()
            if server_id:
                print(f"🔍 Encontrado possível ID: {server_id}")
                # Se temos um server_id, tentar construir a URL da API do Keep
                api_url = f"https://keep.google.com/media/v2/{server_id}"
                try:
                    response = requests.get(api_url)
                    if response.status_code == 200:
                        with open(file_path, 'wb') as f:
                            f.write(response.content)
                        print(f"✅ Desenho extraído usando URL alternativa")
                        return True
                except Exception:
                    pass  # Silenciosamente falha e continua
        except Exception:
            pass  # Silenciosamente falha e continua
    
    return False

def detect_blob_type(blob):
    """
    Detecta o tipo de blob com mais precisão examinando múltiplos atributos.
    Retorna uma tupla (tipo_str, é_desenho)
    """
    blob_type = "unknown"
    is_drawing = False
    
    # Verificar tipo diretamente
    if hasattr(blob, 'type'):
        blob_type = str(blob.type)
        if 'Drawing' in blob_type:
            is_drawing = True
    
    # Verificar objeto interno
    elif hasattr(blob, 'blob') and hasattr(blob.blob, 'type'):
        blob_type = str(blob.blob.type)
        if 'Drawing' in blob_type:
            is_drawing = True
    
    # Verificar por atributos típicos de desenhos
    drawing_attrs = ['drawable', 'drawing', 'drawing_data']
    for attr in drawing_attrs:
        if hasattr(blob, attr):
            blob_type = "Drawing"
            is_drawing = True
            break
        if hasattr(blob, 'blob') and hasattr(blob.blob, attr):
            blob_type = "Drawing"
            is_drawing = True
            break
    
    # Verificar mimetype se disponível
    if hasattr(blob, 'mimetype'):
        mime = blob.mimetype
        if mime:
            if 'image/png' in mime or 'image/jpeg' in mime:
                blob_type = "Image"
            elif 'application/pdf' in mime:
                blob_type = "PDF"
            elif 'drawing' in mime.lower():
                blob_type = "Drawing"
                is_drawing = True
    
    # Formato seguro para nomes de arquivos
    safe_type = blob_type.replace("NodeType.", "").replace(".", "_").lower()
    
    return (safe_type, is_drawing)

def extract_drawing_from_note(keep, note, output_dir):
    """Extrai desenhos de uma nota do Google Keep"""
    note_title = note.title or 'Sem_titulo'
    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in note_title)
    safe_title = safe_title.strip().replace(" ", "_")
    if not safe_title:
        safe_title = "nota"
    
    print(f"\n{'=' * 50}")
    print(f"📝 Processando nota: {note_title}")
    
    # Verificar se a nota tem desenhos
    if not note.blobs:
        print("ℹ️ Esta nota não contém anexos.")
        return []
    
    print(f"📎 Encontrados {len(note.blobs)} anexos.")
    extracted_files = []
    
    # Processar cada anexo
    for i, blob in enumerate(note.blobs):
        print(f"\n🖼️ Processando anexo {i+1}...")
        
        # Verificar tipo do anexo usando nossa função melhorada
        blob_type, is_drawing = detect_blob_type(blob)
        
        if is_drawing:
            print(f"🖌️ Detectado desenho do Google Keep (tipo: {blob_type})")
        else:
            print(f"📎 Tipo de anexo detectado: {blob_type}")
        
        # Extrair informações únicas para o nome do arquivo
        identifier = ""
        if hasattr(blob, 'id'):
            identifier += f"id-{blob.id[:8]}_"  # Usar parte do ID como identificador
        elif hasattr(blob, 'server_id') and blob.server_id:
            identifier += f"sid-{blob.server_id[:8]}_"  # Usar parte do server_id
        
        # Verificar data da nota (se disponível)
        date_info = ""
        if hasattr(note, 'timestamps') and hasattr(note.timestamps, 'created'):
            date_info = note.timestamps.created.strftime('%Y%m%d')
            
        # O safe_type já vem da nossa função detect_blob_type
        
        # Nome do arquivo no formato: Título_data_id_tipo_índice.png
        file_name = f"{safe_title}"
        if date_info:
            file_name += f"_{date_info}"
        if identifier:
            file_name += f"_{identifier}"
        file_name += f"{blob_type}_{i+1}.png"
        
        file_path = output_dir / file_name
        
        print(f"📎 Tipo de anexo: {blob_type}")
        print(f"🏷️ Nome do arquivo: {file_name}")
        
        # Método principal: usar getMediaLink
        try:
            # Obter URL para o blob
            media_url = keep.getMediaLink(blob)
            if media_url:
                print(f"🔄 URL para download obtida: {media_url}")
                
                # Baixar o desenho
                response = requests.get(media_url)
                if response.status_code == 200:
                    # Salvar o desenho
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"✅ Desenho salvo em: {file_path}")
                    extracted_files.append(file_path)
                    
                    # Verificar se é uma imagem válida
                    try:
                        with Image.open(file_path) as img:
                            print(f"✅ Imagem validada (Formato: {img.format}, Tamanho: {img.size})")
                    except Exception as img_error:
                        print(f"⚠️ O arquivo não é uma imagem válida: {img_error}")
                else:
                    print(f"❌ Falha ao baixar desenho: {response.status_code}")
                    # Tentar métodos alternativos
                    if extract_drawing_alternative(keep, blob, file_path):
                        extracted_files.append(file_path)
                        print(f"✅ Desenho salvo usando método alternativo")
            else:
                print("❌ Não foi possível obter o link para download")
                # Tentar métodos alternativos
                if extract_drawing_alternative(keep, blob, file_path):
                    extracted_files.append(file_path)
                    print(f"✅ Desenho salvo usando método alternativo")
                else:
                    debug_blob_basic(blob)  # Mostrar diagnóstico básico
        except Exception as e:
            print(f"❌ Erro ao processar anexo: {e}")
            
            # Tentar métodos alternativos
            if extract_drawing_alternative(keep, blob, file_path):
                extracted_files.append(file_path)
                print(f"✅ Desenho salvo usando método alternativo")
            else:
                # Mostrar informações básicas do blob para depuração
                debug_blob_basic(blob)

    return extracted_files

def main():
    """Função principal do programa"""
    # Exibir versão atual
    versao = "0.5.1"
    print(f"\n{'=' * 58}\n{'📝 Extrator de Desenhos do Google Keep - Versão ' + versao:^58}\n{'=' * 58}")
    
    # Verificar argumentos
    if len(sys.argv) != 2:
        sys.exit("\n📋 Uso: python extract_drawing.py <label>\n"
                "Exemplo: python extract_drawing.py Desenhos\n")
    
    label_name = sys.argv[1]
    print(f"🔄 Buscando notas com a label '{label_name}'...")
    
    # Conectar ao Google Keep
    keep = connect_to_keep()
    
    # Criar diretório para salvar imagens
    if not IMAGE_DIR.exists():
        IMAGE_DIR.mkdir(parents=True)
    
    # Encontrar a label especificada
    try:
        label = keep.findLabel(label_name)
        if not label:
            sys.exit(f"❌ Label '{label_name}' não encontrada. Verifique se você criou esta label no Google Keep.")
    except Exception as e:
        sys.exit(f"❌ Erro ao buscar a label: {e}")
    
    # Encontrar notas com a label especificada
    try:
        notes_with_label = list(keep.find(labels=[label]))
        print(f"📋 Total de notas com a label '{label_name}': {len(notes_with_label)}")
        
        if not notes_with_label:
            print(f"ℹ️ Nenhuma nota com a label '{label_name}' foi encontrada.")
            return
        
        # Extrair desenhos de cada nota
        all_extracted_files = []
        for note in notes_with_label:
            files = extract_drawing_from_note(keep, note, IMAGE_DIR)
            all_extracted_files.extend(files)
        
        # Resumo
        print(f"\n{'=' * 50}")
        print(f"✅ Processamento concluído! Extraídos {len(all_extracted_files)} desenhos.")
        if all_extracted_files:
            print(f"🖼️ Os desenhos foram salvos em: {IMAGE_DIR}")
        else:
            print("⚠️ Nenhum desenho foi extraído. Verifique se as notas contêm desenhos.")
        
    except Exception as e:
        sys.exit(f"❌ Erro ao processar notas: {e}")

if __name__ == "__main__":
    main()
