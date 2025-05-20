# OCR de Notas Manuscritas

Ferramenta simples para extrair texto de imagens de notas manuscritas utilizando a API de visão OpenAI (GPT-4o).

## Pré-requisitos

- Python 3.x
- Conta na OpenAI com API key válida
- Variável de ambiente `OPENAI_API_KEY` configurada com sua chave de API OU chave configurada no arquivo `.env/config`

## Instalação

Clone este repositório e instale as dependências usando um ambiente virtual:

```bash
git clone <repositorio>
cd <diretorio-do-projeto>

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
# venv\Scripts\activate    # Windows

# Instalar dependências
pip install -r requirements.txt
```

## Configuração da API

Você pode configurar sua chave da API OpenAI de duas maneiras:

1. **Variável de ambiente**:
```bash
export OPENAI_API_KEY="sua-chave-api-aqui"
```

2. **Arquivo de configuração**:
Edite o arquivo `.env/config` e substitua `sua-chave-api-aqui` pela sua chave real:
```
OPENAI_API_KEY=sk-sua-chave-api-aqui
```

## Execução

Certifique-se de que o ambiente virtual está ativado e execute o script:

```bash
# Ativar ambiente virtual (se ainda não estiver ativado)
source venv/bin/activate  # Linux/Mac
# ou
# venv\Scripts\activate    # Windows

# Executar o script com a imagem padrão (ink.png da pasta image)
python ocr_extractor.py

# Ou especifique outra imagem (opcional)
python ocr_extractor.py caminho/para/sua/imagem.png
```

A transcrição será exibida no terminal e também salva em um arquivo `.txt` com o mesmo nome no mesmo diretório.

## Exemplo de resultado

Para uma imagem de nota manuscrita `nota.png`, o script gerará:

```
Processando a imagem...

Transcrição:
--------------------------------------------------
Este é um exemplo de texto manuscrito.
A ferramenta OCR consegue identificar
palavras e frases escritas à mão com
boa precisão.
--------------------------------------------------

Transcrição salva em nota.txt
```

## Formatos suportados

- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)

## Estrutura do projeto

```
├── README.md            # Esta documentação
├── requirements.txt     # Dependências do projeto
├── ocr_extractor.py     # Script principal
├── .env/                # Pasta para configurações
│   └── config           # Arquivo de configuração (chave API)
└── image/               # Pasta contendo imagens para OCR
    └── ink.png          # Imagem padrão utilizada pelo script
```
