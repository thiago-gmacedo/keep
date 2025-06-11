# 📝 OCR Keep → Obsidian + Vector DB

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4%20Vision-orange)](https://openai.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Database-purple)](https://chromadb.com)

> **Transforme suas notas manuscritas em conhecimento digital estruturado**

Pipeline que extrai imagens do Google Keep, executa OCR com GPT‑4 Vision, estrutura o texto com modelos de linguagem e gera arquivos Markdown prontos para o Obsidian. As notas também são indexadas no ChromaDB para busca semântica.

![Demo Placeholder](https://via.placeholder.com/800x400/2196F3/ffffff?text=🚀+Pipeline+OCR+Keep+→+Obsidian+%2B+ChromaDB)

## ✨ Visão Geral

- Conecta automaticamente ao Google Keep via master token
- Filtra notas por labels e datas
- Executa OCR avançado em imagens manuscritas
- Estrutura o conteúdo em JSON e Markdown
- Indexa o resultado no ChromaDB
- Permite automação agendada e logs detalhados

## 🛠️ Tecnologias

| Componente     | Tecnologia                    | Função             |
|---------------|------------------------------|--------------------|
| OCR           | GPT‑4 Vision                 | Extração de texto manuscrito |
| Backend       | Python 3.8+                  | Pipeline principal |
| Keep API      | gkeepapi                     | Conexão com Google Keep |
| Vector DB     | ChromaDB                     | Busca semântica |
| Embeddings    | Sentence Transformers        | Indexação multilíngue |
| Output        | Markdown + YAML              | Compatibilidade Obsidian |
| Config        | python-dotenv                | Carregamento do arquivo `.env` |

## 📋 Requisitos

- Python 3.8 ou superior
- Conta Google com acesso ao Keep
- API key da OpenAI (GPT‑4 Vision)
- Master token do Google Keep (veja [CONFIG.md](CONFIG.md))
- Linux ou macOS (Windows via WSL)

## ⚡ Instalação Rápida

```bash
# Clone o repositório
git clone https://github.com/thiago-gmacedo/ocr-keep-obsidian.git
cd ocr-keep-obsidian

# (Opcional) crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # no Windows use venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

Crie e edite o arquivo de configuração:

```bash
mkdir -p .env
cp CONFIG.md .env/
nano .env/config  # ou seu editor preferido
```

Exemplo de `.env/config`:

```env
GOOGLE_EMAIL=seu.email@gmail.com
GOOGLE_MASTER_TOKEN=token
OPENAI_API_KEY=sua_chave_openai
OBS_PATH=~/Documents/ObsidianVault     # opcional
CHROMA_DB_PATH=~/databases/chroma      # opcional
```

Verifique o setup:

```bash
chmod +x setup_check.sh run_loop.sh
./setup_check.sh
```

## 🚀 Comandos Principais

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `python -m src.main` | Executa pipeline completo | Processa notas de hoje |
| `python -m src.main "Label"` | Filtra por label específica | `python -m src.main "Anotacoes"` |
| `python scripts/query_interface.py` | Interface de busca ChromaDB | Consulta interativa |
| `python clear_data.py` | **Limpar todos os dados** | Remove ChromaDB, Obsidian e logs |
| `./run_loop.sh` | Execução agendada | Roda em horários configurados |
| `./setup_check.sh` | Diagnóstico rápido | Verificação do sistema |
| `tail -f logs/pipeline.log` | Acompanhar logs | Monitoramento em tempo real |

## 💻 Uso Básico

```bash
source venv/bin/activate
python -m src.main
python -m src.main "Estudos"
python scripts/query_interface.py
./setup_check.sh
```

### Uso em Servidor

```bash
./run_loop.sh
```

### Monitoramento

```bash
tail -f logs/pipeline.log
tail -20 logs/pipeline.log
ls -la obsidian_notes/
ls -la chroma_db/
```

### Limpeza e Reset

```bash
python clear_data.py
python clear_data.py --help
```

### Debug e Diagnóstico

```bash
./setup_check.sh
tail -50 logs/pipeline.log
python --version
pip list | grep -E "(openai|gkeepapi|chromadb|python-dotenv)"
cat .env/config | grep -v TOKEN
python scripts/query_interface.py --stats
python -m src.main --verbose
export PYTHONPATH=.
export DEBUG=1
python -m src.main
```

### Comandos RAG

```bash
python scripts/chat_rag.py
python scripts/chat_rag.py "O que preciso fazer esta semana?"
python scripts/chat_rag.py --stats
```

## 📁 Estrutura do Projeto

```
ocr-keep-obsidian/
├── src/               # módulos principais
├── scripts/           # utilitários CLI
├── obsidian_notes/    # arquivos .md gerados
├── chroma_db/         # base vetorial
├── logs/              # registros de execução
└── .env/              # credenciais e configurações
```

## 🔄 Como Funciona o Pipeline

1. Autentica no Google Keep e baixa imagens novas
2. Executa OCR com GPT‑4 Vision
3. Estrutura o texto em JSON
4. Gera Markdown compatível com Obsidian
5. Indexa no ChromaDB para busca semântica
6. Move arquivos processados e registra no log

## ⚙️ Configuração Avançada

- Detalhes sobre o master token estão em [CONFIG.md](CONFIG.md)
- A coleção padrão do ChromaDB é `handwritten_notes`
- Para ajustar horários de execução, edite `run_loop.sh`

## 🚨 Solução de Problemas

- Erro de autenticação: gere um novo master token
- Módulos não encontrados: ative o ambiente virtual
- Sem notas encontradas: verifique labels e datas
- Veja os logs em `logs/pipeline.log` para mais detalhes

## 📄 Licença

Distribuído sob a [MIT License](LICENSE).

## 🙏 Agradecimentos

- OpenAI pelo GPT‑4 Vision
- ChromaDB e Sentence Transformers
- gkeepapi e Obsidian

Para suporte ou dúvidas, abra uma issue no [repositório](https://github.com/thiago-gmacedo/ocr-keep-obsidian).
