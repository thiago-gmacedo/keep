#!/usr/bin/env python3
"""
Obsidian Writer - Converte JSON estruturado em arquivos Markdown para Obsidian

Este módulo converte dados JSON extraídos do OCR em arquivos .md com YAML front-matter
compatíveis com o Obsidian.
"""

import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import re


def json_to_obsidian(json_data: dict, output_folder: str) -> None:
    """
    Converte dados JSON estruturados em arquivo Markdown para Obsidian
    
    Args:
        json_data (dict): Dados estruturados do OCR contendo title, data, summary, 
                         keywords, tasks, notes, reminders
        output_folder (str): Caminho para o diretório onde salvar o arquivo .md
    
    Returns:
        None: Salva o arquivo .md no diretório especificado
    """
    # Garantir que o diretório de saída existe
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Extrair dados do JSON
    title = json_data.get("title", "").strip()
    data = json_data.get("data", "").strip()
    summary = json_data.get("summary", "")
    keywords = json_data.get("keywords", [])
    tasks = json_data.get("tasks", [])
    notes = json_data.get("notes", [])
    reminders = json_data.get("reminders", [])
    
    # Processar data e título
    created_date, formatted_date = _process_date(data)
    final_title = _process_title(title, formatted_date)
    
    # Gerar IDs únicos
    source_id = _generate_source_id(final_title, formatted_date)
    vector_id = _generate_vector_id(json_data)
    
    # Data atual para campos de timestamp
    now = datetime.now()
    current_timestamp = now.strftime("%Y-%m-%dT%H:%M:%S")
    
    # Montar YAML front-matter
    yaml_data = {
        "title": final_title,
        "created": created_date,
        "last_modified": current_timestamp,
        "embedding_date": current_timestamp,
        "source_id": source_id,
        "vector_id": vector_id,
        "summary": summary,
        "keywords": keywords,
        "tasks": tasks,
        "notes": notes,
        "reminders": reminders
    }
    
    # Gerar conteúdo do arquivo
    md_content = _generate_markdown_content(yaml_data)
    
    # Gerar nome do arquivo
    filename = _generate_filename(final_title)
    file_path = output_path / f"{filename}.md"
    
    # Salvar arquivo
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"✅ Arquivo Obsidian salvo: {file_path}")
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo {file_path}: {e}")
        raise


def _process_date(data: str) -> tuple[str, str]:
    """
    Processa a data do JSON e retorna formato ISO e formatado
    
    Args:
        data (str): Data extraída do JSON (pode estar vazia)
    
    Returns:
        tuple: (data_iso, data_formatada)
    """
    if data:
        # Tentar parse de vários formatos de data
        date_formats = [
            "%d/%m/%Y",
            "%d/%m/%y", 
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%d.%m.%Y"
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(data, fmt)
                return (
                    parsed_date.strftime("%Y-%m-%dT00:00:00"),
                    parsed_date.strftime("%d/%m/%Y")
                )
            except ValueError:
                continue
    
    # Se não conseguiu parsear ou data está vazia, usar hoje
    today = datetime.now()
    return (
        today.strftime("%Y-%m-%dT00:00:00"),
        today.strftime("%d/%m/%Y")
    )


def _process_title(title: str, formatted_date: str) -> str:
    """
    Processa o título, gerando um padrão se estiver vazio
    
    Args:
        title (str): Título extraído do JSON
        formatted_date (str): Data formatada
    
    Returns:
        str: Título final processado
    """
    if title:
        return title
    else:
        return f"Diário {formatted_date}"


def _generate_source_id(title: str, formatted_date: str) -> str:
    """
    Gera ID de origem baseado no título ou data
    
    Args:
        title (str): Título processado
        formatted_date (str): Data formatada
    
    Returns:
        str: source_id único
    """
    if "Diário" in title:
        # Para diários, usar formato keep_diario_data
        date_slug = formatted_date.replace("/", "")
        return f"keep_diario_{date_slug}"
    else:
        # Para outros títulos, criar slug
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '_', slug)
        return f"keep_{slug}"


def _generate_vector_id(json_data: dict) -> str:
    """
    Gera ID único para vetor baseado no conteúdo do JSON
    
    Args:
        json_data (dict): Dados completos do JSON
    
    Returns:
        str: vector_id único (hash SHA256)
    """
    # Serializar JSON de forma determinística
    json_string = json.dumps(json_data, sort_keys=True, ensure_ascii=False)
    
    # Gerar hash SHA256
    return hashlib.sha256(json_string.encode('utf-8')).hexdigest()


def _generate_filename(title: str) -> str:
    """
    Gera nome de arquivo válido baseado no título
    
    Args:
        title (str): Título do documento
    
    Returns:
        str: Nome de arquivo válido
    """
    # Remover caracteres especiais e espaços
    filename = re.sub(r'[^\w\s-]', '', title)
    filename = re.sub(r'[-\s]+', '_', filename)
    
    # Garantir que não está vazio
    if not filename:
        filename = f"documento_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return filename


def _generate_markdown_content(yaml_data: dict) -> str:
    """
    Gera o conteúdo completo do arquivo Markdown com YAML front-matter
    
    Args:
        yaml_data (dict): Dados para o YAML front-matter
    
    Returns:
        str: Conteúdo completo do arquivo Markdown
    """
    # Início do YAML front-matter
    content = ["---"]
    
    # Adicionar campos do YAML
    content.append(f'title: "{yaml_data["title"]}"')
    content.append(f'created: "{yaml_data["created"]}"')
    content.append(f'last_modified: "{yaml_data["last_modified"]}"')
    content.append(f'embedding_date: "{yaml_data["embedding_date"]}"')
    content.append(f'source_id: "{yaml_data["source_id"]}"')
    content.append(f'vector_id: "{yaml_data["vector_id"]}"')
    content.append(f'summary: "{yaml_data["summary"]}"')
    
    # Keywords como lista YAML
    if yaml_data["keywords"]:
        content.append("keywords:")
        for keyword in yaml_data["keywords"]:
            content.append(f'  - "{keyword}"')
    else:
        content.append("keywords: []")
    
    # Tasks como lista de objetos YAML
    if yaml_data["tasks"]:
        content.append("tasks:")
        for task in yaml_data["tasks"]:
            content.append(f'  - task: "{task.get("task", "")}"')
            content.append(f'    status: "{task.get("status", "todo")}"')
    else:
        content.append("tasks: []")
    
    # Notes como lista YAML
    if yaml_data["notes"]:
        content.append("notes:")
        for note in yaml_data["notes"]:
            content.append(f'  - "{note}"')
    else:
        content.append("notes: []")
    
    # Reminders como lista YAML
    if yaml_data["reminders"]:
        content.append("reminders:")
        for reminder in yaml_data["reminders"]:
            content.append(f'  - "{reminder}"')
    else:
        content.append("reminders: []")
    
    # Fim do YAML front-matter
    content.append("---")
    content.append("")
    
    # Conteúdo do documento (seções baseadas nos dados)
    content.append(f"# {yaml_data['title']}")
    content.append("")
    
    if yaml_data["summary"]:
        content.append("## Resumo")
        content.append(f"{yaml_data['summary']}")
        content.append("")
    
    # Seção de Tarefas
    if yaml_data["tasks"]:
        content.append("## Tarefas")
        content.append("")
        for task in yaml_data["tasks"]:
            status_symbol = "✅" if task.get("status") == "done" else "📋"
            content.append(f"- {status_symbol} {task.get('task', '')}")
        content.append("")
    
    # Seção de Notas
    if yaml_data["notes"]:
        content.append("## Notas")
        content.append("")
        for note in yaml_data["notes"]:
            content.append(f"- {note}")
        content.append("")
    
    # Seção de Lembretes
    if yaml_data["reminders"]:
        content.append("## Lembretes")
        content.append("")
        for reminder in yaml_data["reminders"]:
            content.append(f"- 🔔 {reminder}")
        content.append("")
    
    return "\n".join(content)


def validate_json_structure(json_data: dict) -> bool:
    """
    Valida se o JSON possui a estrutura mínima esperada
    
    Args:
        json_data (dict): Dados JSON a serem validados
    
    Returns:
        bool: True se válido, False caso contrário
    """
    required_fields = ["title", "data", "summary", "keywords", "tasks", "notes", "reminders"]
    
    for field in required_fields:
        if field not in json_data:
            print(f"⚠️ Campo obrigatório ausente: {field}")
            return False
    
    # Validar tipos específicos
    if not isinstance(json_data["keywords"], list):
        print("⚠️ Campo 'keywords' deve ser uma lista")
        return False
    
    if not isinstance(json_data["tasks"], list):
        print("⚠️ Campo 'tasks' deve ser uma lista")
        return False
        
    if not isinstance(json_data["notes"], list):
        print("⚠️ Campo 'notes' deve ser uma lista")
        return False
        
    if not isinstance(json_data["reminders"], list):
        print("⚠️ Campo 'reminders' deve ser uma lista")
        return False
    
    return True


if __name__ == "__main__":
    # Exemplo de teste direto
    example_json = {
        "title": "26/05/25",
        "data": "",
        "summary": "Planejamento e organização de tarefas diárias.",
        "keywords": ["trabalho", "arte", "armazenamento", "skin care", "academia"],
        "tasks": [
            {"task": "Skin care", "status": "done"},
            {"task": "Academia", "status": "todo"},
            {"task": "Estudo", "status": "done"}
        ],
        "notes": [
            "No trabalho: QA CSPM mapeamento do risk rating inválido.",
            "No Marque: uma call com o Alex para debugar.",
            "Dark care: Criei uma arte assinada do Houver para ser o novo plano de fundo."
        ],
        "reminders": [
            "Comprar um HDD para fazer o armazenamento automático de fotos e vídeos."
        ]
    }
    
    print("🧪 Testando obsidian_writer diretamente...")
    json_to_obsidian(example_json, "obsidian_notes")
