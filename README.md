# OCR Keep → Obsidian + Vector DB

**Versão:** 1.0.0  
**Data:** 29/05/2025

Pipeline automatizado para processamento de notas manuscritas do Google Keep com OCR, estruturação via LLM, geração de arquivos Obsidian e indexação semântica no ChromaDB.

## 🚀 Funcionalidades

- **Conexão automática** ao Google Keep via master token
- **Filtragem inteligente** de notas de hoje por label/tag
- **OCR avançado** usando GPT-4 Vision para texto manuscrito
- **Estruturação LLM** do texto extraído em JSON padronizado
- **Geração automática** de arquivos Markdown para Obsidian
- **Indexação semântica** no ChromaDB com embeddings multilingues
- **Controle de duplicatas** com rastreamento de notas processadas
- **Organização automática** de imagens processadas
- **Execução agendada** para servidor com horários configuráveis
- **Caminhos configuráveis** via .env para Obsidian e ChromaDB
- **Sistema de logs** completo com timestamps e níveis
- **Deploy universal** para qualquer servidor Linux/macOS

## 📋 Pré-requisitos

- Python 3.8+ 
- Conta Google com Google Keep ativo
- Chave API OpenAI (GPT-4 Vision)
- Master token do Google Keep

## 🛠️ Instalação

1. **Clone o repositório:**
```bash
git clone <repository-url>
cd keep
```

2. **Instale dependências:**
```bash
pip install -r requirements.txt
```

3. **Configure credenciais:**
```bash
cp .env/.env.example .env/config
# Edite .env/config com suas credenciais
```

4. **Verificação automática de setup:**
```bash
chmod +x setup_check.sh
./setup_check.sh
```

## ⚙️ Configuração

Veja o arquivo [CONFIG.md](CONFIG.md) para instruções detalhadas de configuração.

### Estrutura do arquivo `.env/config`:
```env
GOOGLE_EMAIL=seu.email@gmail.com
GOOGLE_MASTER_TOKEN=seu_master_token_aqui
OPENAI_API_KEY=sk-sua_chave_openai_aqui

# Caminhos configuráveis (opcional)
OBS_PATH=~/Documents/ObsidianVault
CHROMA_DB_PATH=~/chroma_db
```

## 🚀 Uso

### Executar pipeline completo:
```bash
python main.py
```

### Executar com schedule de servidor (1h e 4h da manhã):
```bash
chmod +x run_loop.sh
./run_loop.sh
```

### Filtrar por label específica:
```bash
python main.py "Anotações diárias"
python main.py "OCR"
```

### Verificar configuração:
```bash
./setup_check.sh
```

### Ajuda:
```bash
python main.py --help
```

## 📁 Estrutura do Projeto

```
keep/
├── main.py                 # Pipeline principal
├── ocr_extractor.py        # Funções Google Keep + OCR
├── setup_check.sh          # Verificação automática de setup
├── run_loop.sh             # Script execução agendada servidor
├── src/
│   ├── obsidian_writer.py  # Geração arquivos Obsidian
│   ├── chroma_indexer.py   # Indexação ChromaDB
│   └── README_CHROMA.md    # Documentação ChromaDB
├── images/                 # Imagens baixadas
│   └── processed/          # Imagens processadas
├── obsidian_notes/         # Arquivos .md gerados (configurável)
├── chroma_db/              # Banco vetorial ChromaDB (configurável)
├── logs/                   # Logs de execução
│   └── pipeline.log        # Log principal do sistema
├── scripts/                # Scripts auxiliares
├── archive/                # Arquivos obsoletos
└── .processed_notes.json   # Controle duplicatas
```

## 📊 Fluxo do Pipeline

1. **Conecta** ao Google Keep usando master token
2. **Busca** notas de hoje com imagens (filtradas por label)
3. **Baixa** imagens das notas não processadas
4. **Executa OCR** com GPT-4 Vision nas imagens
5. **Estrutura** texto extraído em JSON via LLM
6. **Gera** arquivos .md no formato Obsidian
7. **Indexa** conteúdo no ChromaDB com embeddings
8. **Move** imagens processadas para diretório organizado
9. **Registra** todas operações em logs timestampados

## 🖥️ Deploy em Servidor

O sistema foi adaptado para execução contínua em servidores pessoais com máxima automação:

### 🚀 Setup Rápido para Servidor

1. **Clone e execute verificação:**
```bash
git clone <repository-url>
cd keep
./setup_check.sh
```

2. **Configure credenciais no .env/config:**
```bash
# Credenciais obrigatórias
GOOGLE_EMAIL=seu.email@gmail.com
GOOGLE_MASTER_TOKEN=seu_master_token_aqui
OPENAI_API_KEY=sk-sua_chave_openai_aqui

# Caminhos opcionais (o sistema cria automaticamente se não existirem)
OBS_PATH=~/Documents/ObsidianVault    # Padrão: ./obsidian_notes
CHROMA_DB_PATH=~/databases/chroma     # Padrão: ./chroma_db
```

3. **Iniciar execução agendada:**
```bash
chmod +x run_loop.sh
./run_loop.sh
```

### ⏰ Execução Agendada

O sistema executa automaticamente nos horários:
- **01:00** - Processamento matinal
- **04:00** - Processamento madrugada

**Características:**
- ✅ Previne execuções duplas no mesmo horário
- ✅ Logs completos de todas operações
- ✅ Cria diretórios automaticamente se não existirem
- ✅ Fallback para caminhos padrão se configuração falhar
- ✅ Suporte a caminhos com `~` (home directory)

### 📋 Logs e Monitoramento

```bash
# Ver logs em tempo real
tail -f logs/pipeline.log

# Ver últimas execuções
tail -20 logs/pipeline.log

# Verificar status do sistema
./setup_check.sh
```

### 🔧 Personalização de Horários

Para alterar os horários de execução, edite `run_loop.sh`:

```bash
# Horários atuais: 1h e 4h
EXECUTION_HOURS="1 4"

# Para executar a cada 6 horas (0h, 6h, 12h, 18h):
EXECUTION_HOURS="0 6 12 18"

# Para executar apenas às 2h da manhã:
EXECUTION_HOURS="2"
```

## 🔍 Exemplo de Saída

### JSON Estruturado:
```json
{
  "title": "28/05/25 - Tarefas",
  "data": "28/05/25",
  "summary": "Lista de tarefas e anotações do dia",
  "keywords": ["tarefas", "produtividade"],
  "tasks": [
    {"task": "Revisar código", "status": "done"},
    {"task": "Documentar projeto", "status": "todo"}
  ],
  "notes": ["Manhã produtiva"],
  "reminders": []
}
```

### Arquivo Obsidian (.md):
```markdown
---
title: "28/05/25 - Tarefas"
created: "2025-05-28T00:00:00"
summary: "Lista de tarefas e anotações do dia"
keywords: ["tarefas", "produtividade"]
vector_id: "abc123..."
---

# 28/05/25 - Tarefas

## Resumo
Lista de tarefas e anotações do dia

## Tarefas
- ✅ Revisar código
- 📋 Documentar projeto

## Notas
- Manhã produtiva
```

## 🧠 ChromaDB & Busca Semântica

O projeto indexa automaticamente todo conteúdo no ChromaDB, permitindo:

- **Busca semântica** por similaridade
- **Recuperação** de contexto relevante
- **Embeddings multilingues** otimizados
- **Metadados estruturados** para filtragem

## 🐛 Troubleshooting

### Problemas comuns:

1. **Erro de autenticação Google Keep:**
   - Verifique master token no `.env/config`
   - Confirme email correto

2. **Erro API OpenAI:**
   - Verifique chave API válida
   - Confirme créditos disponíveis

3. **Nenhuma nota encontrada:**
   - Confirme que há notas de hoje
   - Verifique se label existe
   - Confirme notas têm anexos de imagem

4. **Problemas de caminho/configuração:**
   - Execute `./setup_check.sh` para diagnóstico completo
   - Verifique logs em `logs/pipeline.log`
   - Confirme permissões de escrita nos diretórios

5. **Script não executa no servidor:**
   - Verifique permissões: `chmod +x run_loop.sh setup_check.sh`
   - Confirme que o arquivo `.env/config` existe
   - Verifique logs para detalhes do erro

## 📝 Changelog

### v2.0.0 (30/05/2025) - Deploy de Servidor
- ✨ **Execução agendada** para servidores (1h e 4h da manhã)
- ✨ **Caminhos configuráveis** via .env (OBS_PATH, CHROMA_DB_PATH)
- ✨ **Sistema de logs** completo com timestamps e níveis
- ✨ **Setup automático** com script de verificação
- ✨ **Deploy universal** funciona em qualquer servidor Linux/macOS
- ✨ **Criação automática** de diretórios se não existirem
- ✨ **Suporte ~** (home directory) em caminhos
- ✨ **Prevenção de execuções duplas** no mesmo horário
- 🔧 **Segurança** com permissões 600 para arquivos de configuração

### v1.0.0 (29/05/2025)
- Pipeline completo funcional
- Integração Google Keep + OCR + Obsidian + ChromaDB
- Sistema de controle de duplicatas
- Filtragem por labels/tags
- Documentação completa

## 📄 Licença

Este projeto está sob licença MIT. Veja [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

**Desenvolvido com ❤️ para automatizar o processamento de notas manuscritas**