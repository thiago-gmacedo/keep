# OCR de Notas Manuscritas (Versão 0.2)

Ferramenta para extrair texto de imagens de notas manuscritas utilizando a API de visão OpenAI (GPT-4o). 
Esta versão permite tanto processar imagens locais quanto extrair automaticamente imagens de notas do Google Keep que contenham uma label específica, com opção de filtrar por data de atualização.

## Pré-requisitos

- Python 3.x
- Conta na OpenAI com API key válida
- Conta do Google para acessar o Google Keep
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

### OpenAI API

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

### Google Keep

Para acessar o Google Keep, você precisará fornecer suas credenciais no arquivo de configuração:

**Arquivo de configuração**: Configure o arquivo `.env/config` com:
```
GOOGLE_EMAIL=seu-email@gmail.com
GOOGLE_MASTER_TOKEN=seu-master-token-aqui
```

**IMPORTANTE**: Esta versão utiliza um master token do Google Keep para autenticação, eliminando a necessidade de fornecer email e senha a cada execução.

Para obter um master token:
1. Execute o script Python conforme instruções no arquivo CONFIG.md
2. O token gerado deve ser adicionado ao arquivo de configuração
3. O token tem validade prolongada e é mais seguro que armazenar uma senha

Se o arquivo de configuração não contiver o master token, o sistema informará a pendência para configuração.

[Saiba mais sobre master tokens](https://gkeepapi.readthedocs.io/en/latest/#obtaining-a-master-token)

## Execução

Certifique-se de que o ambiente virtual está ativado e execute o script:

```bash
# Ativar ambiente virtual (se ainda não estiver ativado)
source venv/bin/activate  # Linux/Mac
# ou
# venv\Scripts\activate    # Windows

# 1. Modo Local - usar a imagem padrão (ink.png da pasta image)
python ocr_extractor.py

# 2. Modo Local - especificar uma imagem
python ocr_extractor.py caminho/para/sua/imagem.png

# 3. Modo Google Keep - especificar uma label
python ocr_extractor.py MinhaLabel
```

### Como usar labels no Google Keep

Para utilizar a funcionalidade de busca por label no Google Keep:

1. Acesse o [Google Keep](https://keep.google.com/) no seu navegador
2. Crie uma nova nota ou abra uma existente
3. Clique no ícone de etiquetas (rótulos) no menu inferior
4. Crie uma nova etiqueta ou selecione uma existente
5. Use esta etiqueta como parâmetro ao executar o script

Ao executar o script com uma label, você terá a opção de:
1. Processar apenas notas atualizadas hoje
2. Processar todas as notas com a label especificada

**Nota**: Por padrão, o script filtra notas pela **data de atualização** (hoje), já que a API do Google Keep não fornece diretamente a data de criação. Portanto, ele processará as notas que contêm a label especificada conforme sua seleção.

A transcrição será exibida no terminal e também salva em um arquivo `.txt` com o mesmo nome no mesmo diretório.

### Nomeação de arquivos

Os arquivos baixados do Google Keep são salvos com nomes informativos que incluem:
- Título da nota
- Data e hora de extração
- Identificador único do anexo (baseado no ID interno do Google Keep)
- Tipo de anexo (desenho, imagem, etc.)
- Índice do anexo na nota

Por exemplo: `MinhaNota_20250520123045_sid-abcd1234_drawing_1.png`

Esta nomeação facilita a organização e identificação de múltiplas versões de um mesmo arquivo.

## Exemplo de resultado

Para uma imagem de nota manuscrita processada, o script gerará:

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
│   └── config           # Arquivo de configuração (chaves API e credenciais)
└── image/               # Pasta contendo imagens para OCR
    ├── ink.png          # Imagem padrão utilizada pelo script
    └── *                # Imagens baixadas do Google Keep e suas transcrições
```
