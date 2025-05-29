import sys
from pathlib import Path

# Adicionar diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.chroma_indexer import ChromaIndexer
from ocr_extractor import load_keep_credentials

# Carregar configuração de caminhos
config = load_keep_credentials()
chroma_path = config.get('CHROMA_DB_PATH', './chroma_db')

# Instanciar o indexador com o caminho configurado
indexer = ChromaIndexer(persist_directory=chroma_path)

# Sua pergunta em linguagem natural
query = "problemas com API do CrowdStrike"

# Buscar notas parecidas com o significado da query
results = indexer.search_similar_notes(query, n_results=5)

# Exibir os resultados
for i, result in enumerate(results, 1):
    print(f"{i}. {result['metadata']['title']}")
    print(f"   📝 Summary: {result['metadata'].get('summary', 'sem resumo')}")
    print(f"   📌 Similaridade: {result['similarity']:.4f}")
    print()
