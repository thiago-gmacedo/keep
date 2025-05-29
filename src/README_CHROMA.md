# ChromaDB Indexer para Notas Manuscritas

## 📄 Descrição

O `ChromaIndexer` é um componente do sistema OCR de Notas Manuscritas que adiciona capacidades de busca semântica. Ele converte as notas JSON estruturadas extraídas pelo OCR em embeddings vetoriais e os armazena no ChromaDB, permitindo realizar consultas por similaridade semântica.

## 🔧 Funcionalidades

- **Geração de Embeddings**: Converte o conteúdo textual das notas em vetores de alta dimensão
- **Indexação no ChromaDB**: Armazena os embeddings e metadados no banco de dados vetorial
- **Busca Semântica**: Permite encontrar notas semanticamente similares a uma consulta
- **Deduplicação**: Evita indexar conteúdos duplicados usando IDs únicos
- **Persistência**: Armazena os embeddings em disco para uso posterior

## 🚀 Como Usar

### 1. Importação

```python
from src.chroma_indexer import ChromaIndexer, index_note_in_chroma
```

### 2. Indexação de uma Nota

```python
# Método 1: Usando a função de conveniência
import json
from src.chroma_indexer import index_note_in_chroma

# Carregar uma nota JSON
with open("caminho/para/nota.json", "r", encoding="utf-8") as f:
    nota_json = json.load(f)

# Indexar a nota
success = index_note_in_chroma(nota_json)
```

```python
# Método 2: Usando a classe ChromaIndexer diretamente
from src.chroma_indexer import ChromaIndexer

# Criar um indexador
indexer = ChromaIndexer(
    collection_name="minhas_notas",
    persist_directory="./meu_banco_vetorial"
)

# Indexar a nota
success = indexer.index_note(nota_json)
```

### 3. Busca Semântica

```python
# Criar um indexador (ou usar um existente)
indexer = ChromaIndexer()

# Realizar uma busca semântica
resultados = indexer.search_similar_notes(
    query="problema de mapeamento",
    n_results=5
)

# Processar os resultados
for resultado in resultados:
    print(f"ID: {resultado['id']}")
    print(f"Título: {resultado['metadata'].get('title', 'N/A')}")
    print(f"Similaridade: {resultado['similarity']:.4f}")
    print("---")
```

### 4. Estatísticas da Coleção

```python
# Obter estatísticas da coleção
stats = indexer.get_collection_stats()
print(f"Total de notas: {stats['total_notes']}")
```

## 🧪 Scripts de Teste e Exemplo

### Teste do Indexador

```bash
python scripts/test_chroma_indexer.py
```

Este script testa a funcionalidade do ChromaIndexer com arquivos JSON reais do seu sistema.

### Exemplo de Uso

```bash
python scripts/example_chroma_indexer.py
```

Este script demonstra um fluxo completo de uso do ChromaIndexer, desde a indexação até a consulta.

## 📚 Documentação Adicional

Para mais detalhes sobre o funcionamento interno e a API completa, consulte os comentários no código-fonte do módulo `src/chroma_indexer.py`.

## 🔗 Integração com o Sistema

O ChromaIndexer complementa o fluxo existente:

1. OCR de imagens (`ocr_extractor.py`)
2. Geração de JSONs estruturados
3. Conversão para notas Obsidian (`obsidian_writer.py`)
4. **Indexação para busca semântica** (`chroma_indexer.py`)

Isso permite que você não apenas armazene suas notas, mas também as recupere de forma inteligente usando linguagem natural.
