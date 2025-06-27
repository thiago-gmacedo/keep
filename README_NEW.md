# 📝 Google Keep OCR Pipeline

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4%20Vision-orange)](https://openai.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Database-purple)](https://chromadb.com)

> **Pipeline automatizado para processamento e análise de anotações do Google Keep com OCR**

Pipeline que extrai imagens do Google Keep, executa OCR com GPT‑4 Vision, estrutura o texto com modelos de linguagem e indexa no ChromaDB para busca semântica inteligente.

![Demo Placeholder](https://via.placeholder.com/800x400/2196F3/ffffff?text=🚀+Google+Keep+OCR+Pipeline+%2B+ChromaDB)

## ✨ Visão Geral

- 🔗 Conecta automaticamente ao Google Keep via master token
- 🏷️ Filtra notas por labels e datas
- 🔍 Executa OCR avançado em imagens manuscritas
- 📊 Estrutura o conteúdo em JSON estruturado
- 🧠 Indexa o resultado no ChromaDB para busca semântica
- ⏰ Execução automática via scheduler

## 🚀 **Fluxo de Processamento**

| Etapa         | Tecnologia                   | Descrição                 |
|---------------|------------------------------|---------------------------|
| Sincronização | Google Keep API              | Busca imagens por label   |
| OCR           | GPT-4 Vision                 | Extração de texto         |
| Estruturação  | LLM (GPT-4)                 | Parsing semântico         |
| Indexação     | ChromaDB + Embeddings       | Busca vetorial            |
| Agendamento   | Python Schedule             | Execução automática       |

## 🔧 **Instalação Rápida**

### **Opção 1: Docker (Recomendado)**

```bash
# Clone o repositório
git clone https://github.com/your-username/google-keep-ocr-pipeline.git
cd google-keep-ocr-pipeline

# Configure as variáveis de ambiente
cp .env.example .env
nano .env  # Configure suas credenciais

# Execute com Docker
docker-compose up --build -d
```

### **Opção 2: Instalação Local**

```bash
# Clone e instale dependências
git clone https://github.com/your-username/google-keep-ocr-pipeline.git
cd google-keep-ocr-pipeline
pip install -r requirements.txt

# Configure ambiente
cp .env.example .env
nano .env

# Execute
python -m src.main
```

## ⚙️ **Configuração**

### **Variáveis de Ambiente (.env/config)**

```env
# Google Keep Authentication
KEEP_MASTER_TOKEN=your_master_token_here
KEEP_USERNAME=your_email@gmail.com

# OpenAI API
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4-vision-preview

# Configurações de Processamento
DEFAULT_LABEL=Anotações diárias
CHROMA_DB_PATH=chroma_db
RAG_CHUNK_COUNT=5
```

### **Credenciais Google Keep**

1. **Obter Master Token:**
   - Faça login no Google Keep no navegador
   - Abra Developer Tools → Network
   - Procure por requests com header `Authorization`
   - Copie o token após `Master `

2. **Configurar no .env:**
   ```env
   KEEP_MASTER_TOKEN=aas_et/AFHfNsl...
   KEEP_USERNAME=seu_email@gmail.com
   ```

## 💻 **Uso Básico**

### **Comandos Principais**

```bash
# Executar pipeline completo
python -m src.main

# Processar label específico
python -m src.main "Anotações diárias"

# Executar scheduler (produção)
python -m src.scheduler
```

### **Scripts de Utilidade**

```bash
# Busca semântica
python scripts/query_interface.py
python scripts/query_interface.py "tarefas pendentes"

# Chat com IA
python scripts/chat_rag.py
python scripts/chat_rag.py "O que preciso fazer esta semana?"

# Verificar status
./check_status.sh

# Limpar dados
python clear_data.py
```

### **Interface de Busca**

```bash
# Executar busca interativa
python scripts/query_interface.py

# Comandos disponíveis:
/help      # Ajuda
/stats     # Estatísticas
/recent    # Notas recentes
/list      # Listar todas
/quit      # Sair
```

## 📁 **Estrutura do Projeto**

```
google-keep-ocr-pipeline/
├── src/
│   ├── main.py              # Pipeline principal
│   ├── scheduler.py         # Agendador automático
│   ├── ocr_extractor.py     # Google Keep + OCR
│   ├── parser.py            # Estruturação LLM
│   ├── chroma_indexer.py    # Indexação vetorial
│   ├── rag_formatter.py     # Formatação RAG
│   └── web_server.py        # API REST
├── scripts/
│   ├── query_interface.py   # Busca semântica
│   ├── chat_rag.py         # Chat IA
│   └── auto_indexer.py     # Indexação batch
├── chroma_db/              # Base vetorial
├── images/                 # Imagens processadas
├── logs/                   # Logs do sistema
├── docker-compose.yml
├── Dockerfile.python
└── requirements.txt
```

## 🔍 **Busca e RAG**

### **ChromaDB + Embeddings**

O sistema indexa automaticamente todas as notas processadas:

```python
# Busca semântica
resultados = indexer.search_similar_notes(
    query="reuniões importantes", 
    n_results=5
)

# Chat RAG
resposta = chat_rag.query("O que discutimos na última reunião?")
```

### **API REST**

```bash
# Iniciar servidor
python -m src.web_server

# Consultar via HTTP
curl "http://localhost:8000/query?text=tarefas%20pendentes"
```

## 🐳 **Deploy com Docker**

### **docker-compose.yml**

```yaml
services:
  keep-processor:
    build: .
    environment:
      - KEEP_MASTER_TOKEN=${KEEP_MASTER_TOKEN}
      - KEEP_USERNAME=${KEEP_USERNAME}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./chroma_db:/app/chroma_db
      - ./logs:/app/logs
      - ./images:/app/images
    restart: unless-stopped
```

### **Comandos Docker**

```bash
# Build e execução
docker-compose up --build -d

# Logs
docker-compose logs -f keep-processor

# Parar
docker-compose down
```

## 📊 **Monitoramento**

### **Health Check**

```bash
# Status do sistema
./check_status.sh

# Output exemplo:
📊 Status do Pipeline Keep (27/06/2025 14:30)
✅ Google Keep: Conectado (última sincronização: 14:25)
✅ OpenAI API: Configurada
✅ ChromaDB: 127 notas indexadas
📁 Caminhos:
  🖼️ Imagens: /app/images (15 processadas)
  🧠 ChromaDB: /app/chroma_db
```

### **Logs Estruturados**

```bash
# Logs em tempo real
tail -f logs/pipeline.log
tail -f logs/scheduler.log

# Logs específicos
grep "ERROR" logs/pipeline.log
grep "OCR" logs/pipeline.log | tail -10
```

## 🛠️ **Desenvolvimento**

### **Ambiente de Desenvolvimento**

```bash
# Container interativo
docker-compose run --rm keep-processor bash

# Instalar dependências de dev
pip install -r requirements-dev.txt

# Testes
python -m pytest tests/
```

### **Extensibilidade**

- **Novos OCR Engines**: Adicionar em `ocr_extractor.py`
- **Modelos LLM**: Configurar em `parser.py`
- **Formatos Export**: Estender `rag_formatter.py`
- **APIs**: Expandir `web_server.py`

## 🎯 **Roadmap**

- [ ] **LightRAG Integration** - Sistema de grafos de conhecimento
- [ ] **Interface Web** - Dashboard completo
- [ ] **Mobile API** - Integração apps móveis
- [ ] **Advanced Analytics** - Insights e tendências
- [ ] **Multi-idioma** - Suporte internacional
- [ ] **Plugin System** - Arquitetura extensível

## 🐛 **Troubleshooting**

### **Problemas Comuns**

**Google Keep não conecta:**
```bash
# Verificar master token
python scripts/test_keep_connection.py

# Renovar token se necessário
```

**OCR com baixa qualidade:**
```bash
# Ajustar pré-processamento de imagem
export IMAGE_PREPROCESSING=true

# Testar imagem específica
python scripts/test_ocr.py image.png
```

**ChromaDB vazio:**
```bash
# Reindexar todas as notas
python scripts/auto_indexer.py --rebuild

# Verificar logs
grep "ChromaDB" logs/pipeline.log
```

## 📄 **Licença**

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🤝 **Contribuição**

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

**Desenvolvido com ❤️ para automatizar o processamento de anotações manuscritas**
