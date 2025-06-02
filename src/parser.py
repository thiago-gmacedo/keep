#!/usr/bin/env python3
"""
Parser - Módulo de parsing de texto OCR para estrutura JSON

Este módulo contém a lógica para enviar texto extraído do OCR para o LLM
e obter uma estrutura JSON padronizada.
"""

import json
import re
import openai
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def parse_ocr_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Converte texto extraído do OCR em estrutura JSON usando LLM
    
    Args:
        text (str): Texto extraído do OCR
        
    Returns:
        Optional[Dict[str, Any]]: Dados estruturados em JSON ou None se falhar
    """
    if not text or not text.strip():
        logger.warning("Texto vazio fornecido para parsing")
        return None
    
    try:
        logger.info("🔄 Enviando texto para estruturação com LLM...")
        
        # Prompt otimizado para estruturação
        prompt = _get_parsing_prompt()
        
        # Chamada para OpenAI
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user", 
                    "content": f"Texto para estruturar:\n\n{text}"
                }
            ],
            temperature=0.1,  # Baixa temperatura para consistência
            max_tokens=2000
        )
        
        structured_text = response.choices[0].message.content.strip()
        logger.info("✅ Resposta recebida do LLM")
        
        # Extrair JSON da resposta
        json_data = _extract_json_from_response(structured_text)
        
        if json_data:
            logger.info("✅ JSON estruturado extraído com sucesso")
            return json_data
        else:
            logger.warning("⚠️ Não foi possível extrair JSON válido da resposta")
            return None
            
    except openai.OpenAIError as e:
        logger.error(f"❌ Erro da API OpenAI: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Erro no parsing: {e}")
        return None


def _get_parsing_prompt() -> str:
    """
    Retorna o prompt otimizado para estruturação de texto
    
    Returns:
        str: Prompt para o LLM
    """
    return """Você é um assistente especializado em estruturar notas manuscritas em formato JSON.

Sua tarefa é analisar o texto fornecido e organizá-lo em uma estrutura JSON consistente com os seguintes campos:

- "title": Título da nota (se houver, ou uma data no formato "dd/mm/aa" se for um diário)
- "data": Data encontrada no texto (formato "dd/mm/aa") ou string vazia se não houver
- "summary": Resumo conciso do conteúdo em uma frase
- "keywords": Array de até 5 palavras-chave relevantes
- "tasks": Array de objetos {"task": "descrição", "status": "done" ou "todo"}
- "notes": Array de anotações gerais e observações
- "reminders": Array de lembretes e coisas a não esquecer

REGRAS IMPORTANTES:
1. TODO o texto deve ser extraído e organizado nos campos apropriados
2. Se algo estiver ilegível, use lógica para completar lacunas
3. Tarefas podem estar marcadas com ✓, ✅, ou similar = "done"
4. Tarefas sem marcação ou com ○, -, • = "todo"
5. Retorne APENAS o JSON válido, sem explicações adicionais
6. Use encoding UTF-8 para caracteres especiais

Exemplo de saída:
{
  "title": "Planejamento Semanal",
  "data": "28/05/25",
  "summary": "Organização de tarefas e compromissos da semana",
  "keywords": ["planejamento", "trabalho", "estudos"],
  "tasks": [
    {"task": "Reunião com cliente", "status": "done"},
    {"task": "Finalizar relatório", "status": "todo"}
  ],
  "notes": ["Priorizar tarefas urgentes"],
  "reminders": ["Ligar para João às 14h"]
}"""


def _extract_json_from_response(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Extrai JSON da resposta do LLM, tratando diferentes formatos
    
    Args:
        response_text (str): Texto da resposta do LLM
        
    Returns:
        Optional[Dict[str, Any]]: JSON extraído ou None se falhar
    """
    try:
        # Tentar extrair JSON de markdown code blocks primeiro
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', response_text, re.DOTALL | re.IGNORECASE)
        if json_match:
            json_content = json_match.group(1).strip()
        else:
            # Se não há code blocks, usar o texto inteiro
            json_content = response_text.strip()
        
        # Tentar fazer parse do JSON
        json_data = json.loads(json_content)
        
        # Validar estrutura básica
        if _validate_json_structure(json_data):
            return json_data
        else:
            logger.warning("⚠️ Estrutura JSON inválida")
            return None
            
    except json.JSONDecodeError as e:
        logger.error(f"❌ Erro ao decodificar JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Erro na extração de JSON: {e}")
        return None


def _validate_json_structure(json_data: Dict[str, Any]) -> bool:
    """
    Valida se a estrutura JSON contém os campos esperados
    
    Args:
        json_data (Dict[str, Any]): Dados JSON para validar
        
    Returns:
        bool: True se estrutura é válida
    """
    required_fields = ["title", "data", "summary", "keywords", "tasks", "notes", "reminders"]
    
    # Verificar se todos os campos obrigatórios existem
    for field in required_fields:
        if field not in json_data:
            logger.warning(f"⚠️ Campo obrigatório ausente: {field}")
            return False
    
    # Verificar tipos de dados
    if not isinstance(json_data.get("keywords"), list):
        logger.warning("⚠️ Campo 'keywords' deve ser uma lista")
        return False
        
    if not isinstance(json_data.get("tasks"), list):
        logger.warning("⚠️ Campo 'tasks' deve ser uma lista")
        return False
        
    if not isinstance(json_data.get("notes"), list):
        logger.warning("⚠️ Campo 'notes' deve ser uma lista")
        return False
        
    if not isinstance(json_data.get("reminders"), list):
        logger.warning("⚠️ Campo 'reminders' deve ser uma lista")
        return False
    
    # Validar estrutura de tarefas
    for task in json_data.get("tasks", []):
        if not isinstance(task, dict):
            logger.warning("⚠️ Cada tarefa deve ser um dicionário")
            return False
        if "task" not in task or "status" not in task:
            logger.warning("⚠️ Cada tarefa deve ter 'task' e 'status'")
            return False
        if task.get("status") not in ["done", "todo"]:
            logger.warning("⚠️ Status da tarefa deve ser 'done' ou 'todo'")
            return False
    
    return True


def clean_and_validate_json(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Limpa e valida dados JSON, corrigindo problemas comuns
    
    Args:
        json_data (Dict[str, Any]): Dados JSON para limpar
        
    Returns:
        Dict[str, Any]: Dados JSON limpos e validados
    """
    cleaned_data = {}
    
    # Campos de string
    string_fields = ["title", "data", "summary"]
    for field in string_fields:
        cleaned_data[field] = str(json_data.get(field, "")).strip()
    
    # Campos de lista
    list_fields = ["keywords", "notes", "reminders"]
    for field in list_fields:
        raw_data = json_data.get(field, [])
        if isinstance(raw_data, list):
            cleaned_data[field] = [str(item).strip() for item in raw_data if str(item).strip()]
        else:
            cleaned_data[field] = []
    
    # Campo de tarefas (estrutura especial)
    tasks = json_data.get("tasks", [])
    cleaned_tasks = []
    
    for task in tasks:
        if isinstance(task, dict):
            task_text = str(task.get("task", "")).strip()
            task_status = task.get("status", "todo")
            
            # Normalizar status
            if task_status not in ["done", "todo"]:
                task_status = "todo"
            
            if task_text:
                cleaned_tasks.append({
                    "task": task_text,
                    "status": task_status
                })
    
    cleaned_data["tasks"] = cleaned_tasks
    
    logger.info("✅ JSON limpo e validado")
    return cleaned_data


if __name__ == "__main__":
    # Teste básico do parser
    print("🧪 Testando parser...")
    
    test_text = """
    Planejamento 28/05/25
    
    Tarefas:
    ✓ Reunião com cliente
    - Finalizar relatório
    - Estudar para prova
    
    Notas:
    - Priorizar projeto urgente
    - Revisar código
    
    Lembretes:
    - Ligar para João às 14h
    """
    
    result = parse_ocr_text(test_text)
    if result:
        print("✅ Teste bem-sucedido!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("❌ Teste falhou!")
