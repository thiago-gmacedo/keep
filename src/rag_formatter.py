#!/usr/bin/env python3
"""
RAG Formatter - Formatação de resultados do ChromaDB para RAG

Este módulo contém funções para formatar os resultados da busca semântica
do ChromaDB em contexto otimizado para modelos LLM em aplicações RAG.
"""

import json
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def format_for_rag(results: List[Dict[str, Any]], max_tokens: int = 1500) -> str:
    """
    Formata resultados da busca semântica para contexto RAG
    
    Args:
        results (List[Dict]): Lista de resultados do ChromaIndexer.search_similar_notes()
        max_tokens (int): Limite aproximado de tokens (padrão: 1500)
        
    Returns:
        str: Contexto formatado para uso em prompts RAG
    """
    if not results:
        return "Nenhuma nota relevante encontrada."
    
    context_parts = []
    total_chars = 0
    # Estimativa: ~4 caracteres por token
    max_chars = max_tokens * 4
    
    for i, result in enumerate(results, 1):
        try:
            metadata = result.get('metadata', {})
            similarity = result.get('similarity', 0.0)
            
            # Extrair campos principais
            title = metadata.get('title', 'Sem título')
            summary = metadata.get('summary', '')
            date = metadata.get('data', '')
            
            # Formatar seção da nota
            note_section = f"\n--- NOTA {i} ---"
            if title:
                note_section += f"\nTítulo: {title}"
            if date:
                note_section += f"\nData: {date}"
            if summary:
                note_section += f"\nResumo: {summary}"
            
            # Adicionar conteúdo detalhado do documento
            document = result.get('document', '')
            if document:
                note_section += f"\nConteúdo: {document}"
            
            # Adicionar informação de relevância
            note_section += f"\nRelevância: {similarity:.2f}"
            note_section += "\n"
            
            # Verificar limite de tokens
            if total_chars + len(note_section) > max_chars:
                logger.info(f"Limite de tokens atingido. Incluindo {i-1} de {len(results)} notas.")
                break
            
            context_parts.append(note_section)
            total_chars += len(note_section)
            
        except Exception as e:
            logger.warning(f"Erro ao formatar resultado {i}: {e}")
            continue
    
    if not context_parts:
        return "Erro ao processar as notas encontradas."
    
    # Montar contexto final
    context = "=== CONTEXTO DAS SUAS ANOTAÇÕES ===\n"
    context += f"Total de notas relevantes: {len(context_parts)}\n"
    context += "".join(context_parts)
    context += "\n=== FIM DO CONTEXTO ==="
    
    return context


def format_for_rag_detailed(results: List[Dict[str, Any]], max_tokens: int = 1500) -> str:
    """
    Versão detalhada do formatador que inclui tarefas e lembretes estruturados
    
    Args:
        results (List[Dict]): Lista de resultados do ChromaIndexer.search_similar_notes()
        max_tokens (int): Limite aproximado de tokens (padrão: 1500)
        
    Returns:
        str: Contexto detalhado formatado para uso em prompts RAG
    """
    if not results:
        return "Nenhuma nota relevante encontrada."
    
    context_parts = []
    total_chars = 0
    max_chars = max_tokens * 4
    
    for i, result in enumerate(results, 1):
        try:
            metadata = result.get('metadata', {})
            similarity = result.get('similarity', 0.0)
            
            # Extrair campos principais
            title = metadata.get('title', 'Sem título')
            summary = metadata.get('summary', '')
            date = metadata.get('data', '')
            keywords = metadata.get('keywords', '')
            
            # Estatísticas de tarefas
            total_tasks = metadata.get('total_tasks', 0)
            done_tasks = metadata.get('done_tasks', 0)
            todo_tasks = metadata.get('todo_tasks', 0)
            
            # Formar seção da nota
            note_section = f"\n--- NOTA {i}: {title} ---"
            if date:
                note_section += f"\nData: {date}"
            if summary:
                note_section += f"\nResumo: {summary}"
            if keywords:
                note_section += f"\nPalavras-chave: {keywords}"
            
            # Adicionar estatísticas de tarefas se houver
            if total_tasks > 0:
                note_section += f"\nTarefas: {done_tasks} concluídas, {todo_tasks} pendentes"
            
            # Adicionar documento completo
            document = result.get('document', '')
            if document:
                note_section += f"\nConteúdo completo: {document}"
            
            note_section += f"\nRelevância: {similarity:.3f}"
            note_section += "\n"
            
            # Verificar limite
            if total_chars + len(note_section) > max_chars:
                logger.info(f"Limite de tokens atingido. Incluindo {i-1} de {len(results)} notas.")
                break
            
            context_parts.append(note_section)
            total_chars += len(note_section)
            
        except Exception as e:
            logger.warning(f"Erro ao formatar resultado detalhado {i}: {e}")
            continue
    
    if not context_parts:
        return "Erro ao processar as notas encontradas."
    
    # Contexto final
    context = "=== SUAS ANOTAÇÕES PESSOAIS ===\n"
    context += f"Encontradas {len(context_parts)} notas relevantes:\n"
    context += "".join(context_parts)
    context += "\n=== FIM DAS ANOTAÇÕES ==="
    
    return context


def estimate_tokens(text: str) -> int:
    """
    Estima o número de tokens em um texto
    
    Args:
        text (str): Texto para estimar
        
    Returns:
        int: Número estimado de tokens
    """
    # Estimativa simples: ~4 caracteres por token para português
    return len(text) // 4


def truncate_context(context: str, max_tokens: int) -> str:
    """
    Trunca contexto para respeitar limite de tokens
    
    Args:
        context (str): Contexto original
        max_tokens (int): Limite de tokens
        
    Returns:
        str: Contexto truncado
    """
    max_chars = max_tokens * 4
    
    if len(context) <= max_chars:
        return context
    
    # Truncar e adicionar indicação
    truncated = context[:max_chars]
    
    # Tentar truncar em uma quebra de linha
    last_newline = truncated.rfind('\n')
    if last_newline > max_chars * 0.8:  # Se a quebra está nos últimos 20%
        truncated = truncated[:last_newline]
    
    truncated += "\n\n[CONTEXTO TRUNCADO DEVIDO AO LIMITE DE TOKENS]"
    
    return truncated


if __name__ == "__main__":
    # Teste básico do formatador
    print("🧪 Testando RAG Formatter...")
    
    # Dados de teste simulando resultado do ChromaDB
    test_results = [
        {
            "id": "test1",
            "document": "Título: Reunião Cliente | Resumo: Discussão sobre projeto | Notas: Definir cronograma | Tarefas: Preparar proposta",
            "metadata": {
                "title": "Reunião Cliente X",
                "summary": "Discussão sobre novo projeto",
                "data": "28/05/25",
                "keywords": "reunião, cliente, projeto",
                "total_tasks": 2,
                "done_tasks": 1,
                "todo_tasks": 1
            },
            "similarity": 0.89
        },
        {
            "id": "test2", 
            "document": "Título: Planejamento Semanal | Resumo: Organização de tarefas | Notas: Priorizar urgentes",
            "metadata": {
                "title": "Planejamento Semanal",
                "summary": "Organização de tarefas da semana",
                "data": "29/05/25",
                "keywords": "planejamento, tarefas, semana",
                "total_tasks": 3,
                "done_tasks": 1,
                "todo_tasks": 2
            },
            "similarity": 0.76
        }
    ]
    
    # Testar formatação básica
    context = format_for_rag(test_results)
    print("✅ Formatação básica:")
    print(context)
    print(f"\nTokens estimados: {estimate_tokens(context)}")
    
    # Testar formatação detalhada
    detailed_context = format_for_rag_detailed(test_results, max_tokens=800)
    print("\n✅ Formatação detalhada:")
    print(detailed_context)
    print(f"\nTokens estimados: {estimate_tokens(detailed_context)}")
