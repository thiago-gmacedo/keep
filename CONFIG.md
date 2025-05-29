# OCR Keep → Obsidian + Vector DB - Guia de Configuração

**Versão:** 1.0.0  
**Data:** 29/05/2025  

## Descrição
Pipeline automatizado para processamento de notas manuscritas do Google Keep com OCR, estruturação via LLM, geração de arquivos Obsidian e indexação semântica no ChromaDB.

## Requisitos
- Python 3.6 ou superior
- Uma conta Google com Google Keep
- Uma chave da API OpenAI (para o OCR)

## Instruções para configurar o Google Keep

Para utilizar o Google Keep com este programa, você precisa obter um master token:

### Como obter um master token do Google Keep:

#### Siga as instruções presentes aqui: https://github.com/rukins/gpsoauth-java

#### Aqui também https://github.com/thiago-gmacedo/token-scripts

## Configuração do arquivo .env/config

O arquivo de configuração deve conter:

```
# Arquivo de configuração para o OCR de Notas Manuscritas
OPENAI_API_KEY=sua-chave-api-aqui

# Credenciais do Google Keep
GOOGLE_EMAIL=seu-email@gmail.com
GOOGLE_MASTER_TOKEN=seu-master-token-aqui
```

O master token é mais seguro que armazenar sua senha do Google e tem validade mais longa.

## Uso

1. Para processar uma imagem local:
   ```
   python ocr_extractor.py caminho/para/imagem.png
   ```

2. Para processar notas do Google Keep com uma label específica:
   ```
   python ocr_extractor.py NomeDaLabel
   ```

3. Para usar a imagem de exemplo:
   ```
   python ocr_extractor.py
   ```
