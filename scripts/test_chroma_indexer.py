#!/usr/bin/env python3
"""
Script de teste para o ChromaIndexer

Este script testa a funcionalidade de indexação semântica utilizando arquivos JSON reais
extraídos do OCR de notas manuscritas.
"""

import os
import sys
import json
from pathlib import Path

# Adicionar o diretório raiz ao path para importar módulos do projeto
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

# Importar o módulo ChromaIndexer
from src.chroma_indexer import ChromaIndexer, index_note_in_chroma

# Configurar diretório de persistência do ChromaDB para testes
CHROMA_TEST_DIR = ROOT_DIR / "test_db"

def test_indexing_with_real_files():
    """Testa a indexação usando arquivos JSON reais"""
    print("🧪 Testando indexação com arquivos JSON reais...")
    
    # Criar diretório para teste se não existir
    if not CHROMA_TEST_DIR.exists():
        CHROMA_TEST_DIR.mkdir(parents=True)
    
    # Inicializar o ChromaIndexer com diretório de teste
    indexer = ChromaIndexer(
        collection_name="test_handwritten_notes",
        persist_directory=str(CHROMA_TEST_DIR)
    )
    
    # Diretório com arquivos JSON para teste
    json_dir = ROOT_DIR / "image"
    
    # Encontrar todos os arquivos JSON no diretório
    json_files = list(json_dir.glob("*.json"))
    
    if not json_files:
        print("❌ Nenhum arquivo JSON encontrado para teste.")
        return False
    
    print(f"📁 Encontrados {len(json_files)} arquivos JSON para teste.")
    
    # Variáveis para estatísticas
    total_files = len(json_files)
    success_count = 0
    
    # Processar cada arquivo JSON
    for i, json_file in enumerate(json_files, 1):
        print(f"\n🔄 Processando arquivo {i}/{total_files}: {json_file.name}")
        
        try:
            # Carregar o arquivo JSON
            with open(json_file, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            
            # Indexar a nota
            success = indexer.index_note(json_data)
            
            if success:
                print(f"✅ Arquivo {json_file.name} indexado com sucesso!")
                success_count += 1
            else:
                print(f"❌ Falha ao indexar arquivo {json_file.name}")
        
        except Exception as e:
            print(f"❌ Erro ao processar arquivo {json_file.name}: {e}")
    
    # Exibir estatísticas
    print(f"\n📊 Estatísticas de indexação:")
    print(f"- Total de arquivos processados: {total_files}")
    print(f"- Arquivos indexados com sucesso: {success_count}")
    print(f"- Taxa de sucesso: {(success_count / total_files) * 100:.2f}%")
    
    # Testar busca semântica
    if success_count > 0:
        print("\n🔍 Testando busca semântica...")
        
        # Lista de consultas para teste
        test_queries = [
            "tarefas pendentes",
            "problema de mapeamento",
            "corte de cabelo",
            "análise de dados"
        ]
        
        for query in test_queries:
            print(f"\n🔎 Consulta: '{query}'")
            results = indexer.search_similar_notes(query, n_results=2)
            
            if results:
                print(f"✅ Encontrados {len(results)} resultados:")
                for i, result in enumerate(results, 1):
                    print(f"  Resultado {i}:")
                    print(f"  - ID: {result['id']}")
                    print(f"  - Título: {result['metadata'].get('title', 'N/A')}")
                    print(f"  - Similaridade: {result['similarity']:.4f}")
            else:
                print("❌ Nenhum resultado encontrado.")
        
        # Obter estatísticas da coleção
        stats = indexer.get_collection_stats()
        print(f"\n📊 Estatísticas da coleção: {stats}")
        
        return True
    else:
        print("\n❌ Nenhum arquivo foi indexado com sucesso.")
        return False

def test_convenience_function():
    """Testa a função de conveniência index_note_in_chroma"""
    print("\n🧪 Testando função de conveniência index_note_in_chroma...")
    
    # Carregar um arquivo JSON de exemplo
    json_dir = ROOT_DIR / "image"
    json_files = list(json_dir.glob("*.json"))
    
    if not json_files:
        print("❌ Nenhum arquivo JSON encontrado para teste.")
        return False
    
    # Usar o primeiro arquivo JSON encontrado
    json_file = json_files[0]
    print(f"📄 Usando arquivo de teste: {json_file.name}")
    
    try:
        # Carregar o arquivo JSON
        with open(json_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        
        # Testar a função de conveniência sem cliente específico
        print("🔄 Testando index_note_in_chroma sem cliente específico...")
        success = index_note_in_chroma(json_data)
        
        if success:
            print("✅ Indexação com função de conveniência bem-sucedida!")
        else:
            print("❌ Falha na indexação com função de conveniência.")
        
        return success
    
    except Exception as e:
        print(f"❌ Erro ao testar função de conveniência: {e}")
        return False

if __name__ == "__main__":
    print(f"{'=' * 60}")
    print(f"{'🧪 TESTE DO CHROMA INDEXER':^60}")
    print(f"{'=' * 60}")
    
    # Executar teste com arquivos reais
    indexing_success = test_indexing_with_real_files()
    
    # Executar teste da função de conveniência
    convenience_success = test_convenience_function()
    
    # Resultado final
    print(f"\n{'=' * 60}")
    if indexing_success and convenience_success:
        print("✅ TODOS OS TESTES FORAM BEM-SUCEDIDOS!")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM!")
    print(f"{'=' * 60}")
