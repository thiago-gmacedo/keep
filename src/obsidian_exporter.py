#!/usr/bin/env python3
"""
Obsidian Exporter - Converte JSON estruturado em arquivos Markdown para Obsidian

Este módulo fornece uma interface unificada para converter dados JSON extraídos do OCR 
em arquivos .md compatíveis com Obsidian. Centraliza toda a lógica de exportação
que estava distribuída no código.

Autor: Thiago Macedo
Data: 29/05/2025
Versão: 1.0.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Importar o módulo obsidian_writer existente
from .obsidian_writer import json_to_obsidian, validate_json_structure

# Configurar logging
logger = logging.getLogger(__name__)


def convert_to_md(json_data: Dict[str, Any], output_folder: Optional[str] = None) -> bool:
    """
    Converte dados JSON estruturados em arquivo Markdown para Obsidian
    
    Esta é a função principal que deve ser usada por outros módulos para gerar
    arquivos Obsidian. Ela encapsula toda a lógica de validação e conversão.
    
    Args:
        json_data: Dados estruturados do OCR contendo title, data, summary, 
                  keywords, tasks, notes, reminders
        output_folder: Pasta onde salvar o arquivo .md. Se None, usa 'obsidian_notes'
    
    Returns:
        True se a conversão foi bem-sucedida, False caso contrário
        
    Examples:
        >>> data = {"title": "Teste", "summary": "Resumo teste", "tasks": []}
        >>> success = convert_to_md(data, "minha_pasta")
        >>> print(success)  # True
    """
    try:
        # Usar pasta padrão se não especificada
        if output_folder is None:
            output_folder = "obsidian_notes"
        
        logger.info(f"🔄 Convertendo para Obsidian: {json_data.get('title', 'Sem título')}")
        
        # Validar estrutura JSON
        if not validate_json_structure(json_data):
            logger.error("❌ Estrutura JSON inválida para conversão Obsidian")
            return False
        
        # Converter para Obsidian usando o módulo existente
        json_to_obsidian(json_data, output_folder)
        
        logger.info(f"✅ Arquivo Obsidian gerado com sucesso em {output_folder}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao converter para Obsidian: {e}")
        return False


def batch_convert_to_md(json_files: list, output_folder: Optional[str] = None) -> Dict[str, bool]:
    """
    Converte múltiplos arquivos JSON em arquivos Markdown para Obsidian
    
    Args:
        json_files: Lista de caminhos para arquivos JSON
        output_folder: Pasta onde salvar os arquivos .md
    
    Returns:
        Dicionário com o resultado de cada conversão {arquivo: sucesso}
    """
    results = {}
    
    logger.info(f"🔄 Convertendo {len(json_files)} arquivos JSON para Obsidian")
    
    for json_file in json_files:
        try:
            json_path = Path(json_file)
            
            if not json_path.exists():
                logger.warning(f"⚠️ Arquivo não encontrado: {json_file}")
                results[str(json_file)] = False
                continue
            
            # Carregar JSON
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Converter
            success = convert_to_md(json_data, output_folder)
            results[str(json_file)] = success
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar {json_file}: {e}")
            results[str(json_file)] = False
    
    successful = sum(1 for success in results.values() if success)
    logger.info(f"📊 Conversão em lote concluída: {successful}/{len(json_files)} sucessos")
    
    return results


def validate_and_convert_to_md(json_data: Dict[str, Any], output_folder: Optional[str] = None) -> bool:
    """
    Valida dados JSON e converte para Markdown se válidos
    
    Args:
        json_data: Dados JSON para validar e converter
        output_folder: Pasta de destino
    
    Returns:
        True se validação e conversão foram bem-sucedidas
    """
    try:
        # Validação básica de campos obrigatórios
        required_fields = ['title', 'summary']
        missing_fields = [field for field in required_fields if not json_data.get(field)]
        
        if missing_fields:
            logger.warning(f"⚠️ Campos obrigatórios ausentes: {missing_fields}")
            return False
        
        # Converter usando a função principal
        return convert_to_md(json_data, output_folder)
        
    except Exception as e:
        logger.error(f"❌ Erro na validação e conversão: {e}")
        return False


def get_obsidian_output_path(output_folder: Optional[str] = None) -> Path:
    """
    Retorna o caminho absoluto da pasta de saída do Obsidian
    
    Args:
        output_folder: Nome da pasta de saída (opcional)
    
    Returns:
        Path object para a pasta de saída
    """
    if output_folder is None:
        output_folder = "obsidian_notes"
    
    # Se for caminho relativo, usar em relação ao diretório raiz do projeto
    if not Path(output_folder).is_absolute():
        root_dir = Path(__file__).parent.parent
        return root_dir / output_folder
    
    return Path(output_folder)


# Manter compatibilidade com código antigo
def convert_json_to_obsidian(json_data: Dict[str, Any], output_folder: str = "obsidian_notes") -> bool:
    """
    Função de compatibilidade - redireciona para convert_to_md
    
    Args:
        json_data: Dados JSON estruturados
        output_folder: Pasta de destino
    
    Returns:
        True se conversão foi bem-sucedida
    """
    logger.warning("⚠️ Usando função deprecated 'convert_json_to_obsidian'. Use 'convert_to_md' no lugar.")
    return convert_to_md(json_data, output_folder)


if __name__ == "__main__":
    """Teste simples do módulo"""
    import logging
    
    # Configurar logging para teste
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    # Dados de teste
    test_data = {
        "title": "Teste Obsidian Exporter",
        "data": "29/05/2025",
        "summary": "Teste do módulo de exportação para Obsidian",
        "keywords": ["teste", "obsidian", "exportação"],
        "tasks": [
            {"task": "Criar módulo exporter", "status": "done"},
            {"task": "Testar conversão", "status": "todo"}
        ],
        "notes": [
            "Módulo criado com sucesso",
            "Documentação adicionada"
        ],
        "reminders": [
            "Testar com dados reais"
        ]
    }
    
    print("🧪 Testando Obsidian Exporter...")
    
    # Teste da função principal
    success = convert_to_md(test_data, "test_obsidian_output")
    
    if success:
        print("✅ Teste bem-sucedido!")
    else:
        print("❌ Teste falhou!")
