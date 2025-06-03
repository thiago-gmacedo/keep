#!/usr/bin/env python3
"""
Clear Data Script - Limpa todos os dados gerados pelo sistema

Este script remove todos os dados gerados pelo sistema OCR Keep, incluindo:
- ChromaDB (banco vetorial)
- Arquivos Obsidian (.md)
- Imagens processadas
- Logs do sistema
- Histórico de notas processadas

Respeita os caminhos configurados no .env/config

Autor: Thiago Macedo
Data: 02/06/2025
"""

import sys
import os
import shutil
from pathlib import Path
from typing import Dict

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

# Importar módulos necessários
try:
    from src.ocr_extractor import load_keep_credentials
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)

def load_config_paths() -> Dict[str, Path]:
    """Carrega os caminhos configurados no .env/config"""
    try:
        config = load_keep_credentials()
        
        # Caminhos configuráveis
        obs_path = config.get('OBS_PATH', str(ROOT_DIR / 'obsidian_notes'))
        chroma_path = config.get('CHROMA_DB_PATH', str(ROOT_DIR / 'chroma_db'))
        
        # Converter para Path absoluto
        if not Path(obs_path).is_absolute():
            obs_path = ROOT_DIR / obs_path
        else:
            obs_path = Path(obs_path)
            
        if not Path(chroma_path).is_absolute():
            chroma_path = ROOT_DIR / chroma_path
        else:
            chroma_path = Path(chroma_path)
        
        # Caminhos fixos
        paths = {
            'obsidian': obs_path,
            'chroma_db': chroma_path,
            'images_processed': ROOT_DIR / 'images' / 'processed',
            'logs': ROOT_DIR / 'logs',
            'processed_notes_file': ROOT_DIR / '.processed_notes.json',
            'query_history': ROOT_DIR / '.query_history',
            'chat_history': ROOT_DIR / '.chat_history.json'
        }
        
        return paths
        
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        print("Usando caminhos padrão...")
        
        # Caminhos padrão em caso de erro
        return {
            'obsidian': ROOT_DIR / 'obsidian_notes',
            'chroma_db': ROOT_DIR / 'chroma_db',
            'images_processed': ROOT_DIR / 'images' / 'processed',
            'logs': ROOT_DIR / 'logs',
            'processed_notes_file': ROOT_DIR / '.processed_notes.json',
            'query_history': ROOT_DIR / '.query_history',
            'chat_history': ROOT_DIR / '.chat_history.json'
        }

def show_paths_to_clear(paths: Dict[str, Path]):
    """Mostra os caminhos que serão limpos"""
    print("\n📂 DADOS QUE SERÃO REMOVIDOS:")
    print("=" * 50)
    
    for name, path in paths.items():
        if path.exists():
            if path.is_dir():
                try:
                    file_count = len(list(path.rglob('*')))
                    size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                    size_mb = size / (1024 * 1024)
                    print(f"  📁 {name:<20} {path} ({file_count} arquivos, {size_mb:.1f}MB)")
                except:
                    print(f"  📁 {name:<20} {path} (diretório)")
            else:
                try:
                    size = path.stat().st_size / 1024
                    print(f"  📄 {name:<20} {path} ({size:.1f}KB)")
                except:
                    print(f"  📄 {name:<20} {path} (arquivo)")
        else:
            print(f"  ⚪ {name:<20} {path} (não existe)")

def clear_directory(path: Path, name: str) -> bool:
    """Remove um diretório e todo seu conteúdo"""
    try:
        if path.exists() and path.is_dir():
            shutil.rmtree(path)
            print(f"  ✅ {name} removido: {path}")
            return True
        else:
            print(f"  ⚪ {name} não existe: {path}")
            return False
    except Exception as e:
        print(f"  ❌ Erro ao remover {name}: {e}")
        return False

def clear_file(path: Path, name: str) -> bool:
    """Remove um arquivo específico"""
    try:
        if path.exists() and path.is_file():
            path.unlink()
            print(f"  ✅ {name} removido: {path}")
            return True
        else:
            print(f"  ⚪ {name} não existe: {path}")
            return False
    except Exception as e:
        print(f"  ❌ Erro ao remover {name}: {e}")
        return False

def confirm_action(paths: Dict[str, Path]) -> bool:
    """Solicita confirmação do usuário"""
    print("\n⚠️  ATENÇÃO: Esta operação é IRREVERSÍVEL!")
    print("   Todos os dados listados acima serão PERMANENTEMENTE removidos.")
    print("   Isso inclui:")
    print("   • 🧠 Banco vetorial ChromaDB (busca semântica)")
    print("   • 📝 Arquivos Obsidian gerados")
    print("   • 📷 Imagens processadas")
    print("   • 📊 Logs do sistema")
    print("   • 🗃️ Histórico de processamento")
    
    print("\n" + "=" * 50)
    response = input("Digite 'CONFIRMO' (maiúsculo) para prosseguir: ").strip()
    
    return response == 'CONFIRMO'

def main():
    """Função principal"""
    print("🧹 LIMPEZA COMPLETA DO SISTEMA OCR KEEP")
    print("=" * 50)
    print("Este script remove TODOS os dados gerados pelo sistema.")
    
    # Carregar caminhos configurados
    paths = load_config_paths()
    
    # Mostrar o que será removido
    show_paths_to_clear(paths)
    
    # Solicitar confirmação
    if not confirm_action(paths):
        print("\n❌ Operação cancelada pelo usuário.")
        return
    
    print(f"\n🧹 Iniciando limpeza...")
    print("=" * 30)
    
    # Contadores
    removed_count = 0
    total_count = len(paths)
    
    # Remover diretórios
    directories = ['chroma_db', 'obsidian', 'images_processed', 'logs']
    for dir_name in directories:
        if dir_name in paths:
            if clear_directory(paths[dir_name], dir_name):
                removed_count += 1
    
    # Remover arquivos
    files = ['processed_notes_file', 'query_history', 'chat_history']
    for file_name in files:
        if file_name in paths:
            if clear_file(paths[file_name], file_name):
                removed_count += 1
    
    # Relatório final
    print(f"\n📊 RELATÓRIO DE LIMPEZA:")
    print("=" * 30)
    print(f"✅ Itens removidos: {removed_count}")
    print(f"⚪ Itens inexistentes: {total_count - removed_count}")
    print(f"📁 Total verificado: {total_count}")
    
    if removed_count > 0:
        print(f"\n🎉 Limpeza concluída com sucesso!")
        print("   O sistema foi resetado para estado inicial.")
        print("   Você pode executar o pipeline novamente:")
        print("   python -m src.main")
    else:
        print(f"\n💡 Nenhum dado foi encontrado para remoção.")
        print("   O sistema já estava limpo.")

def show_help():
    """Mostra ajuda do script"""
    print("🧹 SCRIPT DE LIMPEZA - OCR Keep")
    print("=" * 40)
    print("\nUSO:")
    print("  python clear_data.py          # Execução interativa")
    print("  python clear_data.py --help   # Esta ajuda")
    print("\nO QUE É REMOVIDO:")
    print("  📁 ChromaDB        - Banco vetorial para busca")
    print("  📁 Obsidian        - Arquivos .md gerados")
    print("  📁 Logs            - Histórico de execução")
    print("  📁 Processadas     - Imagens já processadas")
    print("  📄 Históricos      - Arquivos de estado")
    print("\nCONFIGURAÇÃO:")
    print("  Os caminhos respeitam as configurações em .env/config")
    print("  - OBS_PATH: diretório Obsidian")
    print("  - CHROMA_DB_PATH: diretório ChromaDB")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        show_help()
    else:
        main()
