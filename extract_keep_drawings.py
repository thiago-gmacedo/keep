#!/usr/bin/env python3
"""
Script para depuração e download direto dos desenhos do Google Keep
utilizando técnicas avançadas de acesso à API.
"""

import gkeepapi
import requests
import os
import sys
from pathlib import Path
from datetime import datetime
import base64
import json

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

def extract_keep_drawings(label_name=None):
    """Extrai e baixa desenhos do Google Keep usando métodos avançados"""
    # Diretório para salvar desenhos
    output_dir = Path(__file__).parent / "keep_drawings"
    if not output_dir.exists():
        output_dir.mkdir()
    
    # Carregar credenciais
    config = load_keep_credentials()
    email = config.get('GOOGLE_EMAIL')
    master_token = config.get('GOOGLE_MASTER_TOKEN')
    
    if not email or not master_token:
        sys.exit("❌ Credenciais do Google Keep não encontradas.")
    
    try:
        # Instanciar API do Keep
        print(f"🔑 Autenticando com a conta {email}...")
        keep = gkeepapi.Keep()
        keep.resume(email, master_token)
        print("✅ Autenticado com sucesso!")
        
        # Obter todas as notas ou filtrar por label
        if label_name:
            label = keep.findLabel(label_name)
            if not label:
                sys.exit(f"❌ Label '{label_name}' não encontrada.")
            notes = list(keep.find(labels=[label]))
            print(f"📝 Encontradas {len(notes)} notas com a label '{label_name}'")
        else:
            notes = list(keep.all())
            print(f"📝 Encontradas {len(notes)} notas no total")
        
        # Filtrar notas com anexos
        notes_with_blobs = []
        for note in notes:
            if hasattr(note, 'blobs') and note.blobs:
                notes_with_blobs.append(note)
        
        print(f"📎 Encontradas {len(notes_with_blobs)} notas com anexos")
        
        if not notes_with_blobs:
            sys.exit("❌ Nenhuma nota com anexos foi encontrada.")
        
        # Agora vamos tentar diversas abordagens para extrair os desenhos
        drawing_count = 0  # Contador de desenhos extraídos com sucesso
        
        # Método 1: Tentar obter informações internas da sessão do Keep
        if hasattr(keep, '_session'):
            session = keep._session
            headers = {}
            
            # Algumas versões do gkeepapi armazenam headers de autenticação
            if hasattr(keep, '_headers'):
                headers = keep._headers
            
            # Vamos tentar obter o token interno para autenticação
            token = None
            if hasattr(keep, '_token'):
                token = keep._token
            elif hasattr(keep, 'token'):
                token = keep.token
            
            if token:
                headers['Authorization'] = f'OAuth {token}'
        
        # Processar cada nota com anexos
        for note_idx, note in enumerate(notes_with_blobs):
            print(f"\n{'='*50}")
            print(f"📝 Processando nota {note_idx+1}/{len(notes_with_blobs)}: {note.title or 'Sem título'}")
            print(f"ID da nota: {note.id}")
            print(f"{'='*50}")
            
            # Processar cada blob na nota
            for blob_idx, blob in enumerate(note.blobs):
                print(f"\n📎 Processando anexo {blob_idx+1}/{len(note.blobs)}:")
                
                # Informações básicas do blob
                if hasattr(blob, 'type'):
                    print(f"- Tipo: {blob.type}")
                if hasattr(blob, 'server_id'):
                    print(f"- Server ID: {blob.server_id}")
                server_id = getattr(blob, 'server_id', None)
                
                if not server_id:
                    print("❌ Não foi possível obter o server_id")
                    continue
                
                # Nome base para arquivos salvos com informações únicas
                safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in (note.title or f"nota_{note_idx+1}"))
                safe_title = safe_title.strip().replace(" ", "_")
                if not safe_title:
                    safe_title = f"nota_{note_idx+1}"
                
                # Adicionar timestamp
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                
                # Extrair server_id para identificação única
                id_info = f"sid-{server_id[:8]}" if server_id else f"idx-{blob_idx}"
                
                # Se disponível, obter tipo do blob para nome do arquivo
                blob_type = "unknown"
                if hasattr(blob, 'type'):
                    blob_type = str(blob.type).replace("NodeType.", "").replace(".", "_").lower()
                
                # Construir nome de arquivo com informações únicas
                file_name = f"{safe_title}_{timestamp}_{id_info}_{blob_type}_{blob_idx+1}"
                output_base = output_dir / file_name
                
                print(f"🏷️ Nome base do arquivo: {file_name}")
                
                # MÉTODO 1: Tentar usar a API direta do Google Keep via requests
                # URLs conhecidas para acessar mídia do Google Keep
                print("🔍 MÉTODO 1: Tentando usar API direta via requests...")
                api_urls = [
                    f"https://keep.googleapis.com/v1/media/{server_id}",
                    f"https://www.googleapis.com/drive/v3/files/{server_id}?alt=media",
                    f"https://keep.google.com/jserv/GetMediaBytes?s={server_id}"
                ]
                
                api_success = False
                if hasattr(keep, '_session'):
                    session = keep._session
                    
                    for url_idx, url in enumerate(api_urls):
                        try:
                            print(f"  Tentativa {url_idx+1}: {url}")
                            response = session.get(url)
                            
                            # Verificar se a resposta parece ser um desenho ou imagem
                            if response.status_code == 200:
                                # Salvar o conteúdo para análise
                                output_file = output_base.with_suffix(f".api{url_idx+1}.png")
                                with open(output_file, 'wb') as f:
                                    f.write(response.content)
                                print(f"✅ Arquivo salvo: {output_file}")
                                api_success = True
                                drawing_count += 1
                                break
                            else:
                                print(f"  ❌ Falhou com status: {response.status_code}")
                        except Exception as e:
                            print(f"  ❌ Erro: {e}")
                
                # MÉTODO 2: Tentar acessar diretamente os atributos do blob
                if not api_success:
                    print("\n🔍 MÉTODO 2: Tentando extrair dados diretos do blob...")
                    
                    # Debug: salvar todos os atributos do blob para análise
                    blob_attrs = {}
                    for attr in dir(blob):
                        if not attr.startswith('_'):
                            try:
                                value = getattr(blob, attr)
                                if not callable(value):
                                    try:
                                        # Tentar converter para string
                                        str_val = str(value)
                                        blob_attrs[attr] = str_val[:100] if len(str_val) > 100 else str_val
                                    except:
                                        blob_attrs[attr] = "OBJETO NÃO SERIALIZÁVEL"
                            except:
                                pass
                    
                    # Salvar atributos como JSON para análise posterior
                    debug_file = output_base.with_suffix(".debug.json")
                    with open(debug_file, 'w') as f:
                        json.dump(blob_attrs, f, indent=2)
                    print(f"📋 Debug do blob salvo em: {debug_file}")
                    
                    # Tentar acessar os bytes do blob de várias maneiras
                    blob_methods = [
                        lambda b: b.get_bytes() if hasattr(b, 'get_bytes') else None,
                        lambda b: b.blob.get_bytes() if hasattr(b, 'blob') and hasattr(b.blob, 'get_bytes') else None,
                        lambda b: b.data if hasattr(b, 'data') else None,
                        lambda b: b.blob.data if hasattr(b, 'blob') and hasattr(b.blob, 'data') else None
                    ]
                    
                    for method_idx, method in enumerate(blob_methods):
                        try:
                            print(f"  Tentativa {method_idx+1}...")
                            data = method(blob)
                            if data:
                                output_file = output_base.with_suffix(f".m{method_idx+1}.png")
                                with open(output_file, 'wb') as f:
                                    f.write(data)
                                print(f"✅ Dados extraídos! Arquivo salvo: {output_file}")
                                drawing_count += 1
                                break
                        except Exception as e:
                            print(f"  ❌ Erro: {e}")
                
                # MÉTODO 3: Tentar usar métodos internos do Keep
                if not api_success:
                    print("\n🔍 MÉTODO 3: Tentando usar métodos internos do Keep...")
                    keep_methods = {
                        'getMediaBytes': lambda k, id: k.getMediaBytes(id) if hasattr(k, 'getMediaBytes') else None,
                        '_media_bytes': lambda k, id: k._media_bytes(id) if hasattr(k, '_media_bytes') else None,
                        'get_blob_bytes': lambda k, id: k.get_blob_bytes(id) if hasattr(k, 'get_blob_bytes') else None,
                        '_getBlobData': lambda k, id: k._getBlobData(id) if hasattr(k, '_getBlobData') else None
                    }
                    
                    for name, method in keep_methods.items():
                        try:
                            print(f"  Tentando método '{name}'...")
                            data = method(keep, server_id)
                            if data:
                                output_file = output_base.with_suffix(f".{name}.png")
                                with open(output_file, 'wb') as f:
                                    f.write(data)
                                print(f"✅ Sucesso! Arquivo salvo: {output_file}")
                                drawing_count += 1
                                break
                        except Exception as e:
                            print(f"  ❌ Erro: {e}")
        
        print(f"\n{'='*50}")
        print(f"✅ Processamento concluído!")
        print(f"📊 Estatísticas:")
        print(f"   - Notas processadas: {len(notes_with_blobs)}")
        print(f"   - Arquivos extraídos: {drawing_count}")
        print(f"📂 Os arquivos foram salvos em: {output_dir}")
        
    except Exception as e:
        print(f"❌ Erro não esperado: {e}")

if __name__ == "__main__":
    # Se um argumento foi fornecido, usar como nome da label
    if len(sys.argv) > 1:
        extract_keep_drawings(sys.argv[1])
    else:
        # Caso contrário, processar todas as notas
        extract_keep_drawings()
