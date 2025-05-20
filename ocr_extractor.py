#!/usr/bin/env python3
"""
OCR de Notas Manuscritas - Extrator de texto manuscrito usando OpenAI Vision API
"""

import openai
import base64
import os
import sys
from pathlib import Path
from PIL import Image

MODEL_NAME = "gpt-4o"  # modelo atual com suporte a visão


def encode_image_to_base64(path):
    """Converte uma imagem para base64"""
    try:
        return base64.b64encode(Path(path).read_bytes()).decode()
    except Exception as e:
        sys.exit(f"Erro ao processar a imagem: {e}")


def transcribe_handwriting(image_path: str) -> str:
    """Transcreve texto manuscrito de uma imagem usando a API OpenAI Vision"""
    # Verificar extensão da imagem
    valid_extensions = ['.png', '.jpg', '.jpeg']
    if Path(image_path).suffix.lower() not in valid_extensions:
        sys.exit(f"Extensão não suportada. Use: {', '.join(valid_extensions)}")
    
    try:
        base64_img = encode_image_to_base64(image_path)
        
        response = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Transcreva TODO o texto manuscrito presente na imagem abaixo. "
                                "Mantenha a ordem das palavras e linhas; se algo estiver ilegível, escreva [ilegível]. "
                                "Não acrescente comentários extras."
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_img}"}
                        }
                    ],
                }
            ],
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        sys.exit(f"Erro da API OpenAI: {e}")
    except Exception as e:
        sys.exit(f"Erro ao transcrever texto: {e}")


def main():
    """Função principal do programa"""
    # Verificar argumentos
    if len(sys.argv) == 1:
        # Usar a imagem padrão da pasta 'image'
        img_path = Path(__file__).parent / "image" / "ink.png"
        print(f"Usando imagem padrão: {img_path}")
    elif len(sys.argv) == 2:
        # Usar a imagem especificada pelo usuário
        img_path = sys.argv[1]
    else:
        sys.exit("Uso: python ocr_extractor.py [caminho_da_imagem]")
    
    if not Path(img_path).is_file():
        sys.exit("Arquivo não encontrado.")

    # Transcrever o texto manuscrito
    print("Processando a imagem...")
    texto = transcribe_handwriting(img_path)
    print("\nTranscrição:")
    print("-" * 50)
    print(texto)
    print("-" * 50)

    # Salvar transcrição em arquivo
    try:
        out_file = Path(img_path).with_suffix(".txt")
        out_file.write_text(texto, encoding="utf-8")
        print(f"\nTranscrição salva em {out_file}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo de saída: {e}")


def load_api_key_from_env_file():
    """Carrega a chave da API OpenAI do arquivo .env/config se disponível"""
    env_file = Path(__file__).parent / '.env' / 'config'
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            if key == 'OPENAI_API_KEY' and value and value != 'sua-chave-api-aqui':
                                return value
        except Exception as e:
            print(f"Aviso: Não foi possível ler o arquivo de configuração: {e}")
    return None

if __name__ == "__main__":
    # Verificar API key
    api_key = os.environ.get("OPENAI_API_KEY") or load_api_key_from_env_file()
    
    if not api_key:
        sys.exit("Erro: Defina a variável de ambiente OPENAI_API_KEY ou configure-a no arquivo .env/config.")
    
    try:
        # Configurar cliente OpenAI com a API key
        openai.api_key = api_key
        main()
    except KeyboardInterrupt:
        sys.exit("\nOperação cancelada pelo usuário.")
    except Exception as e:
        sys.exit(f"Erro não esperado: {e}")
