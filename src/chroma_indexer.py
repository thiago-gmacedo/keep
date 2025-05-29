#!/usr/bin/env python3
"""
ChromaDB Indexer - Indexação de notas estruturadas no ChromaDB

Este módulo converte notas JSON estruturadas em embeddings e as indexa
no ChromaDB para permitir consultas semânticas.
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
import chromadb
from chromadb import Client as ChromaClient
from sentence_transformers import SentenceTransformer
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelo para geração de embeddings (modelo multilingual otimizado)
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

class ChromaIndexer:
    """Classe para indexar notas no ChromaDB"""
    
    def __init__(self, collection_name: str = "handwritten_notes", persist_directory: str = "./chroma_db"):
        """
        Inicializa o indexador ChromaDB
        
        Args:
            collection_name (str): Nome da coleção no ChromaDB
            persist_directory (str): Diretório para persistir o banco de dados
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Inicializar cliente ChromaDB
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Inicializar modelo de embeddings
        logger.info(f"🔄 Carregando modelo de embeddings: {EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        # Criar ou obter coleção
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"✅ Coleção '{collection_name}' carregada com sucesso")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Usar distância cosseno
            )
            logger.info(f"✅ Nova coleção '{collection_name}' criada")
    
    def _extract_content_for_embedding(self, json_data: Dict[str, Any]) -> str:
        """
        Extrai e combina conteúdo relevante para geração de embeddings
        
        Args:
            json_data (dict): Dados JSON da nota
            
        Returns:
            str: Texto combinado para embedding
        """
        content_parts = []
        
        # Adicionar título se disponível
        if json_data.get("title"):
            content_parts.append(f"Título: {json_data['title']}")
        
        # Adicionar resumo
        if json_data.get("summary"):
            content_parts.append(f"Resumo: {json_data['summary']}")
        
        # Adicionar notas
        if json_data.get("notes") and isinstance(json_data["notes"], list):
            notes_text = " ".join(json_data["notes"])
            if notes_text.strip():
                content_parts.append(f"Notas: {notes_text}")
        
        # Adicionar lembretes
        if json_data.get("reminders") and isinstance(json_data["reminders"], list):
            reminders_text = " ".join(json_data["reminders"])
            if reminders_text.strip():
                content_parts.append(f"Lembretes: {reminders_text}")
        
        # Adicionar tarefas (apenas o texto, não o status)
        if json_data.get("tasks") and isinstance(json_data["tasks"], list):
            tasks_text = []
            for task in json_data["tasks"]:
                if isinstance(task, dict) and task.get("task"):
                    tasks_text.append(task["task"])
            if tasks_text:
                content_parts.append(f"Tarefas: {' '.join(tasks_text)}")
        
        # Adicionar palavras-chave
        if json_data.get("keywords") and isinstance(json_data["keywords"], list):
            keywords_text = " ".join(json_data["keywords"])
            if keywords_text.strip():
                content_parts.append(f"Palavras-chave: {keywords_text}")
        
        return " | ".join(content_parts)
    
    def _prepare_metadata(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepara metadados para armazenamento no ChromaDB
        
        Args:
            json_data (dict): Dados JSON da nota
            
        Returns:
            dict: Metadados estruturados
        """
        metadata = {}
        
        # Metadados básicos
        metadata["title"] = json_data.get("title", "")
        metadata["summary"] = json_data.get("summary", "")
        metadata["data"] = json_data.get("data", "")
        
        # Data de criação/indexação
        metadata["indexed_at"] = datetime.now().isoformat()
        
        # Palavras-chave como string
        if json_data.get("keywords"):
            metadata["keywords"] = ", ".join(json_data["keywords"])
        
        # Contar tarefas
        tasks = json_data.get("tasks", [])
        if tasks:
            metadata["total_tasks"] = len(tasks)
            metadata["done_tasks"] = len([t for t in tasks if t.get("status") == "done"])
            metadata["todo_tasks"] = len([t for t in tasks if t.get("status") == "todo"])
        
        # Contar notas e lembretes
        metadata["notes_count"] = len(json_data.get("notes", []))
        metadata["reminders_count"] = len(json_data.get("reminders", []))
        
        # IDs únicos se disponíveis
        if json_data.get("source_id"):
            metadata["source_id"] = json_data["source_id"]
        if json_data.get("vector_id"):
            metadata["vector_id"] = json_data["vector_id"]
        
        return metadata
    
    def _generate_unique_id(self, json_data: Dict[str, Any]) -> str:
        """
        Gera ID único para a nota baseado no conteúdo
        
        Args:
            json_data (dict): Dados JSON da nota
            
        Returns:
            str: ID único
        """
        # Usar vector_id se disponível
        if json_data.get("vector_id"):
            return json_data["vector_id"]
        
        # Usar source_id se disponível
        if json_data.get("source_id"):
            return json_data["source_id"]
        
        # Gerar hash baseado no conteúdo
        content = self._extract_content_for_embedding(json_data)
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def index_note(self, json_data: Dict[str, Any]) -> bool:
        """
        Indexa uma nota no ChromaDB
        
        Args:
            json_data (dict): Dados JSON estruturados da nota
            
        Returns:
            bool: True se indexação foi bem-sucedida, False caso contrário
        """
        try:
            # Gerar ID único
            unique_id = self._generate_unique_id(json_data)
            
            # Verificar se já existe
            existing = None
            try:
                existing = self.collection.get(ids=[unique_id])
                if existing["ids"]:
                    logger.info(f"🔄 Nota {unique_id} já existe. Atualizando...")
            except Exception:
                pass  # Nota não existe, continuar com inserção
            
            # Extrair conteúdo para embedding
            content = self._extract_content_for_embedding(json_data)
            if not content.strip():
                logger.warning(f"⚠️ Conteúdo vazio para nota {unique_id}")
                return False
            
            # Gerar embedding
            logger.info(f"🔄 Gerando embedding para nota {unique_id}")
            embedding = self.embedding_model.encode(content).tolist()
            
            # Preparar metadados
            metadata = self._prepare_metadata(json_data)
            
            # Indexar ou atualizar no ChromaDB
            if existing and existing["ids"]:
                # Atualizar entrada existente
                self.collection.update(
                    ids=[unique_id],
                    embeddings=[embedding],
                    metadatas=[metadata],
                    documents=[content]
                )
                logger.info(f"✅ Nota {unique_id} atualizada com sucesso")
            else:
                # Inserir nova entrada
                self.collection.add(
                    ids=[unique_id],
                    embeddings=[embedding],
                    metadatas=[metadata],
                    documents=[content]
                )
                logger.info(f"✅ Nota {unique_id} indexada com sucesso")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao indexar nota: {e}")
            return False
    
    def search_similar_notes(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Busca notas similares usando consulta semântica
        
        Args:
            query (str): Texto da consulta
            n_results (int): Número máximo de resultados
            
        Returns:
            List[Dict]: Lista de notas similares com metadados
        """
        try:
            # Gerar embedding da consulta
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Buscar no ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Formatar resultados
            formatted_results = []
            for i, doc_id in enumerate(results["ids"][0]):
                formatted_results.append({
                    "id": doc_id,
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similarity": 1 - results["distances"][0][i]  # Converter distância para similaridade
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Erro na busca semântica: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas da coleção
        
        Returns:
            dict: Estatísticas da coleção
        """
        try:
            count = self.collection.count()
            return {
                "total_notes": count,
                "collection_name": self.collection_name,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {"error": str(e)}


def index_note_in_chroma(json_data: Dict[str, Any], chroma_client: ChromaClient = None) -> bool:
    """
    Função de conveniência para indexar uma nota no ChromaDB
    
    Args:
        json_data (dict): Dados JSON estruturados da nota
        chroma_client (ChromaClient, optional): Cliente ChromaDB (se None, cria novo)
        
    Returns:
        bool: True se indexação foi bem-sucedida, False caso contrário
    """
    try:
        # Se não foi fornecido cliente, criar novo indexador
        if chroma_client is None:
            indexer = ChromaIndexer()
        else:
            # Usar cliente fornecido - criar indexador customizado
            indexer = ChromaIndexer()
            # Substituir o cliente padrão pelo fornecido
            indexer.client = chroma_client
            # Recriar a coleção com o cliente fornecido
            try:
                indexer.collection = chroma_client.get_collection(name=indexer.collection_name)
                logger.info(f"✅ Usando coleção existente '{indexer.collection_name}' do cliente fornecido")
            except Exception:
                indexer.collection = chroma_client.create_collection(
                    name=indexer.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info(f"✅ Nova coleção '{indexer.collection_name}' criada no cliente fornecido")
        
        return indexer.index_note(json_data)
        
    except Exception as e:
        logger.error(f"❌ Erro na função index_note_in_chroma: {e}")
        return False


if __name__ == "__main__":
    # Teste básico
    print("🧪 Testando ChromaIndexer...")
    
    # Dados de teste
    test_data = {
        "title": "Teste de Indexação",
        "data": "28/05/2025",
        "summary": "Teste do sistema de indexação no ChromaDB",
        "keywords": ["teste", "chromadb", "embeddings"],
        "tasks": [
            {"task": "Implementar indexação", "status": "done"},
            {"task": "Testar busca semântica", "status": "todo"}
        ],
        "notes": ["Sistema funcionando corretamente"],
        "reminders": ["Verificar performance"]
    }
    
    # Testar indexação
    indexer = ChromaIndexer()
    success = indexer.index_note(test_data)
    
    if success:
        print("✅ Teste de indexação bem-sucedido!")
        
        # Testar busca
        results = indexer.search_similar_notes("teste de sistema", n_results=3)
        print(f"🔍 Encontrados {len(results)} resultados similares")
        
        # Estatísticas
        stats = indexer.get_collection_stats()
        print(f"📊 Estatísticas: {stats}")
    else:
        print("❌ Teste de indexação falhou!")
