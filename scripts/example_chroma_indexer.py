#!/usr/bin/env python3
"""
Exemplo de uso do ChromaIndexer com arquivos JSON reais.

Este script demonstra como indexar arquivos JSON no ChromaDB e
realizar consultas semânticas para recuperar notas similares.
"""

import sys
import json
from pathlib import Path
import chromadb

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

# Importar o módulo ChromaIndexer
from src.chroma_indexer import index_note_in_chroma, ChromaIndexer

def main():
    """Função principal para demonstração"""
    print("\n📝 DEMONSTRAÇÃO DE USO DO CHROMA INDEXER")
    print("=" * 50)
    
    # Exemplo 1: Carregar e indexar um arquivo JSON usando a função de conveniência
    json_dir = ROOT_DIR / "images"
    json_files = list(json_dir.glob("*.json"))
    
    if not json_files:
        print("❌ Nenhum arquivo JSON encontrado.")
        return
    
    # Escolher o primeiro arquivo como exemplo
    json_file = json_files[0]
    
    print(f"📄 Usando arquivo: {json_file.name}")
    
    # Carregar o arquivo JSON
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print("🔄 Indexando nota usando função de conveniência...")
    
    # Criar cliente ChromaDB
    chroma_client = chromadb.PersistentClient(path=str(ROOT_DIR / "demo_chroma_db"))
    
    # Indexar a nota
    success = index_note_in_chroma(data, chroma_client)
    
    if success:
        print("✅ Nota indexada com sucesso!")
    else:
        print("❌ Falha ao indexar nota.")
        return
    
    # Exemplo 2: Criando um indexador e realizando consultas
    print("\n🔍 REALIZANDO CONSULTAS SEMÂNTICAS")
    print("=" * 50)
    
    # Criar um indexador
    indexer = ChromaIndexer(
        collection_name="handwritten_notes",
        persist_directory=str(ROOT_DIR / "demo_chroma_db")
    )
    
    # Exemplos de consultas
    queries = [
        "tarefas para fazer",
        "notas sobre problemas técnicos",
        "lembretes importantes"
    ]
    
    # Executar consultas
    for query in queries:
        print(f"\n🔎 Consulta: '{query}'")
        results = indexer.search_similar_notes(query, n_results=2)
        
        if results:
            print(f"✅ Encontrados {len(results)} resultados:")
            for i, result in enumerate(results, 1):
                print(f"  Resultado {i}:")
                print(f"  - Título: {result['metadata'].get('title', 'N/A')}")
                print(f"  - Similaridade: {result['similarity']:.4f}")
                if 'summary' in result['metadata'] and result['metadata']['summary']:
                    print(f"  - Resumo: {result['metadata']['summary']}")
        else:
            print("❌ Nenhum resultado encontrado.")
    
    # Exibir estatísticas da coleção
    stats = indexer.get_collection_stats()
    print(f"\n📊 Estatísticas da coleção: {stats}")

if __name__ == "__main__":
    main()
