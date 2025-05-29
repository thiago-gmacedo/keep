# 📝 OCR Keep → Obsidian + Vector DB

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4%20Vision-orange)](https://openai.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Database-purple)](https://chromadb.com)

> **Transforme suas notas manuscritas em conhecimento digital estruturado**

Pipeline inteligente e automatizado que extrai, processa e indexa notas manuscritas do Google Keep, utilizando OCR avançado com GPT-4 Vision, estruturação semântica com LLMs, e armazenamento integrado em Obsidian (.md) + ChromaDB para busca semântica.

![Demo Placeholder](https://via.placeholder.com/800x400/2196F3/ffffff?text=🚀+Pipeline+OCR+Keep+→+Obsidian+%2B+ChromaDB)

## ✨ Visão Geral

Este projeto resolve o problema de **digitalização inteligente de notas manuscritas**, oferecendo um pipeline completo que:

- 🔗 **Conecta automaticamente** ao Google Keep via master token
- 🎯 **Filtra inteligentemente** notas por labels/tags e datas
- 🤖 **OCR de alta precisão** usando GPT-4 Vision para manuscritos
- 📊 **Estrutura semanticamente** o conteúdo com LLMs em JSON padronizado
- 📝 **Gera arquivos Markdown** otimizados para Obsidian com frontmatter YAML
- 🔍 **Indexa semanticamente** no ChromaDB com embeddings multilingues
- 🔄 **Executa automaticamente** em horários programados (ideal para servidores)
- 📁 **Organiza inteligentemente** arquivos processados e controla duplicatas
- ⚙️ **Configuração flexível** via .env com caminhos personalizáveis
- 📊 **Logs completos** com timestamps e monitoramento de status

### 🎯 Casos de Uso

- **📚 Pesquisadores**: Digitalize anotações de campo e literatura
- **🎓 Estudantes**: Transforme notas de aula em material de estudo estruturado  
- **💼 Profissionais**: Organize reuniões e brainstorming em conhecimento pesquisável
- **✍️ Escritores**: Capture ideias manuscritas em sistema digital organizado
- **🏠 Uso Pessoal**: Automatize organização de listas, lembretes e notas cotidianas

## 🛠️ Tecnologias Utilizadas

| Componente | Tecnologia | Função |
|------------|------------|---------|
| **OCR** | GPT-4 Vision | Extração de texto manuscrito |
| **Backend** | Python 3.8+ | Pipeline principal |
| **Keep API** | gkeepapi | Conexão com Google Keep |
| **Vector DB** | ChromaDB | Busca semântica |
| **Embeddings** | Sentence Transformers | Indexação multilíngue |
| **Output** | Markdown + YAML | Compatibilidade Obsidian |
| **Automação** | Bash Scripts | Execução agendada |

## 📋 Requisitos

### Obrigatórios
- **Python 3.8+** (recomendado 3.10+)
- **Conta Google** com Google Keep ativo
- **OpenAI API Key** com acesso ao GPT-4 Vision
- **Google Keep Master Token** ([como obter](CONFIG.md))

### Sistema Operacional
- ✅ Linux (testado no Ubuntu 20.04+)
- ✅ macOS (testado no macOS 12+)
- ⚠️ Windows (suporte via WSL)

## ⚡ Instalação Rápida

### 1️⃣ Clone e Configure o Ambiente

```bash
# Clone o repositório
git clone https://github.com/thiago-gmacedo/ocr-keep-obsidian.git
cd ocr-keep-obsidian

# Crie um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou: venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt
```

### 2️⃣ Configure as Credenciais

```bash
# Crie o arquivo de configuração
mkdir -p .env
cp CONFIG.md .env/  # Use como referência

# Edite o arquivo de configuração
nano .env/config  # ou seu editor preferido
```

**Estrutura do `.env/config`:**
```env
# 🔑 Credenciais obrigatórias
GOOGLE_EMAIL=seu.email@gmail.com
GOOGLE_MASTER_TOKEN=seu_master_token_aqui
OPENAI_API_KEY=sk-sua_chave_openai_aqui

# 📁 Caminhos personalizados (opcional)
OBS_PATH=~/Documents/ObsidianVault    # Padrão: ./obsidian_notes
CHROMA_DB_PATH=~/databases/chroma     # Padrão: ./chroma_db
```

### 3️⃣ Verificação do Setup

```bash
# Torne os scripts executáveis
chmod +x setup_check.sh run_loop.sh

# Execute verificação automática
./setup_check.sh
```

✅ **Pronto!** Se a verificação passou, seu sistema está configurado corretamente.

## 🚀 Como Usar

### 📖 Comandos Principais

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `python src/main.py` | Executa pipeline completo | Processa todas as notas de hoje |
| `python src/main.py "Label"` | Filtra por label específica | `python src/main.py "Anotações"` |
| `./run_loop.sh` | Execução agendada (servidor) | Roda às 01:00 e 04:00 diariamente |
| `./setup_check.sh` | Verificação do sistema | Diagnóstico completo |
| `tail -f logs/pipeline.log` | Monitorar logs em tempo real | Ver execução atual |

### 💻 Uso Básico

```bash
# Ative o ambiente virtual
source venv/bin/activate

# Execute o pipeline uma vez
python src/main.py

# Execute com filtro de label
python src/main.py "Estudos"

# Verificar se tudo está funcionando
./setup_check.sh
```

### 🖥️ Uso em Servidor (Automático)

```bash
# Inicie execução contínua (ideal para VPS/servidor)
./run_loop.sh

# O sistema executará automaticamente às 01:00 e 04:00
# Para parar: Ctrl+C ou kill do processo
```

### 📊 Monitoramento

```bash
# Ver logs em tempo real
tail -f logs/pipeline.log

# Ver últimas 20 linhas do log
tail -20 logs/pipeline.log

# Verificar status do sistema
./setup_check.sh

# Ver arquivos gerados
ls -la obsidian_notes/
ls -la chroma_db/
```

## 📁 Estrutura do Projeto

```
📦 ocr-keep-obsidian/
├── 🚀 src/                          # Módulos principais
│   ├── main.py                      # 🎯 Pipeline central
│   ├── obsidian_writer.py           # 📝 Gerador Markdown/Obsidian
│   ├── chroma_indexer.py            # 🔍 Indexador ChromaDB
│   └── README_CHROMA.md             # 📖 Docs ChromaDB
├── 🔧 scripts/                      # Scripts auxiliares
│   ├── auto_indexer.py              # 🔄 Indexação automática
│   └── test_chroma_indexer.py       # 🧪 Testes ChromaDB
├── 📷 images/                       # Imagens baixadas
│   └── processed/                   # ✅ Imagens processadas
├── 📝 obsidian_notes/               # 📁 Arquivos .md gerados
├── 🔍 chroma_db/                    # 💾 Banco vetorial
├── 📊 logs/                         # 📋 Logs do sistema
│   └── pipeline.log                 # 📄 Log principal
├── ⚙️ .env/                         # 🔐 Configurações
│   └── config                       # 🔑 Credenciais
├── 🗃️ archive/                      # 📦 Arquivos legados
├── 🔧 main.py                       # 🎯 Entry point alternativo
├── 🔧 ocr_extractor.py              # 📷 Funções Keep + OCR
├── 🔧 run_loop.sh                   # ⏰ Execução agendada
├── 🔧 setup_check.sh                # ✅ Verificação setup
├── 📋 requirements.txt              # 📦 Dependências Python
├── 📖 README.md                     # 📚 Este arquivo
├── ⚙️ CONFIG.md                     # 🔧 Guia configuração
└── 📄 .processed_notes.json         # 🔄 Controle duplicatas
```

### 📂 Diretórios Importantes

| Diretório | Propósito | Configurável |
|-----------|-----------|--------------|
| `obsidian_notes/` | Arquivos .md gerados | ✅ via `OBS_PATH` |
| `chroma_db/` | Banco vetorial ChromaDB | ✅ via `CHROMA_DB_PATH` |
| `images/` | Imagens baixadas do Keep | ❌ Fixo |
| `logs/` | Logs de execução | ❌ Fixo |

## 🔄 Como Funciona o Pipeline

```mermaid
graph LR
    A[📱 Google Keep] --> B[🔗 Master Token]
    B --> C[📷 Download Images]
    C --> D[🤖 GPT-4 Vision OCR]
    D --> E[📊 LLM Structure]
    E --> F[📝 Obsidian .md]
    E --> G[🔍 ChromaDB Index]
    F --> H[📁 Organized Files]
    G --> H
```

### 🎯 Etapas Detalhadas

1. **🔗 Conexão**: Autentica no Google Keep via master token
2. **🎯 Filtragem**: Busca notas de hoje com imagens (opcionalmente por label)
3. **📥 Download**: Baixa imagens das notas não processadas anteriormente
4. **🤖 OCR**: Extrai texto manuscrito usando GPT-4 Vision
5. **📊 Estruturação**: Organiza conteúdo em JSON padronizado via LLM
6. **📝 Geração**: Cria arquivos .md compatíveis com Obsidian
7. **🔍 Indexação**: Gera embeddings e indexa no ChromaDB
8. **📁 Organização**: Move imagens para pasta `processed/`
9. **📋 Controle**: Registra operação para evitar duplicatas futuras

### 🎨 Exemplo de Transformação

**📷 Input**: Imagem de nota manuscrita
```
✍️ "Reunião cliente X
   - Discutir proposta
   - Agendar follow-up
   💡 Ideia: integração API"
```

**📊 JSON Estruturado**:
```json
{
  "title": "Reunião Cliente X",
  "data": "29/05/25",
  "summary": "Reunião para discussão de proposta e follow-up",
  "keywords": ["reunião", "cliente", "proposta", "API"],
  "tasks": [
    {"task": "Discutir proposta", "status": "done"},
    {"task": "Agendar follow-up", "status": "todo"}
  ],
  "notes": ["Ideia: integração API"],
  "reminders": []
}
```

**📝 Obsidian Output**:
```markdown
---
title: "Reunião Cliente X"
created: "2025-05-29T00:00:00"
summary: "Reunião para discussão de proposta e follow-up"
keywords: ["reunião", "cliente", "proposta", "API"]
---

# Reunião Cliente X

## 📋 Tarefas
- ✅ Discutir proposta  
- 📌 Agendar follow-up

## 📝 Notas
- 💡 Ideia: integração API
```

## ⚙️ Configuração Avançada

### 🔐 Obtendo o Master Token do Google Keep

O master token é mais seguro que armazenar senhas e tem validade estendida.

**Métodos disponíveis:**
1. **📖 Guia Oficial**: [Como obter master token](CONFIG.md)
2. **🔧 Scripts Auxiliares**: [Token Scripts Repository](https://github.com/thiago-gmacedo/token-scripts)
3. **📚 Referência Java**: [GPSAuth Java](https://github.com/rukins/gpsoauth-java)

### 🎛️ Variáveis de Ambiente

```env
# 🔑 OBRIGATÓRIAS
GOOGLE_EMAIL=seu.email@gmail.com
GOOGLE_MASTER_TOKEN=ya29.a0AfH6SMB...
OPENAI_API_KEY=sk-proj-abc123...

# 📁 OPCIONAIS (caminhos personalizados)
OBS_PATH=~/Documents/MyObsidianVault
CHROMA_DB_PATH=~/data/vectordb
```

### ⏰ Configuração de Horários

Edite `run_loop.sh` para personalizar horários de execução:

```bash
# Linha ~21: Modificar função is_execution_time()
if [[ ("$current_hour" == "06" || "$current_hour" == "18") && "$current_minute" -lt "05" ]]; then
    return 0  # Agora executa às 6h e 18h
fi
```

### 🔍 Configuração ChromaDB

O sistema cria automaticamente:
- **Coleção**: `handwritten_notes`
- **Modelo**: `paraphrase-multilingual-MiniLM-L12-v2`
- **Metadados**: Título, data, palavras-chave, resumo

Para consultas avançadas, veja [README_CHROMA.md](src/README_CHROMA.md).

## 🔍 Exemplo de Saída Completa

### 🎯 Busca Semântica no ChromaDB

```python
# Exemplo de busca no ChromaDB
from src.chroma_indexer import ChromaIndexer

indexer = ChromaIndexer()
results = indexer.query_similar_notes("reunião cliente", n_results=3)

# Retorna notas similares com scores de similaridade
```

### 📊 Estrutura JSON Completa

```json
{
  "title": "28/05/25 - Planejamento Semanal",
  "data": "28/05/25",
  "summary": "Organização de tarefas e metas da semana",
  "keywords": ["planejamento", "tarefas", "metas", "produtividade"],
  "tasks": [
    {"task": "Finalizar apresentação", "status": "done"},
    {"task": "Revisar código do projeto", "status": "todo"},
    {"task": "Agendar reunião com cliente", "status": "todo"}
  ],
  "notes": [
    "Priorizar tarefas urgentes",
    "Reservar tempo para revisão de código"
  ],
  "reminders": [
    "Ligar para cliente às 14h",
    "Backup do projeto na sexta"
  ]
}
```

### 📝 Arquivo Obsidian Gerado

```markdown
---
title: "28/05/25 - Planejamento Semanal"
created: "2025-05-28T00:00:00"
last_modified: "2025-05-29T01:23:45"
embedding_date: "2025-05-29T01:23:45"
source_id: "keep_280525_planejamento_semanal"
vector_id: "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6"
summary: "Organização de tarefas e metas da semana"
keywords:
  - "planejamento"
  - "tarefas" 
  - "metas"
  - "produtividade"
---

# 28/05/25 - Planejamento Semanal

## 📝 Resumo
Organização de tarefas e metas da semana

## 📋 Tarefas
- ✅ Finalizar apresentação
- 📌 Revisar código do projeto  
- 📌 Agendar reunião com cliente

## 📓 Notas
- Priorizar tarefas urgentes
- Reservar tempo para revisão de código

## ⏰ Lembretes
- 📞 Ligar para cliente às 14h
- 💾 Backup do projeto na sexta

---
*Processado automaticamente pelo OCR Keep Pipeline*
```

## 🚨 Solução de Problemas

### ❌ Problemas Comuns e Soluções

| Problema | Possível Causa | Solução |
|----------|---------------|---------|
| 🔐 **Erro de autenticação Keep** | Master token inválido/expirado | Regenerar token seguindo [CONFIG.md](CONFIG.md) |
| 💳 **Erro API OpenAI** | Chave inválida ou sem créditos | Verificar chave e saldo na conta OpenAI |
| 📋 **Nenhuma nota encontrada** | Sem notas hoje ou label inexistente | Verificar notas no Keep e labels utilizadas |
| 📁 **Erro de permissão** | Diretórios sem permissão de escrita | `chmod 755` nos diretórios ou usar `sudo` |
| 🐍 **Módulos não encontrados** | Ambiente virtual não ativado | `source venv/bin/activate` |

### 🔧 Comandos de Diagnóstico

```bash
# 🩺 Verificação completa do sistema
./setup_check.sh

# 📊 Verificar logs detalhados
tail -50 logs/pipeline.log

# 🐍 Verificar ambiente Python
python --version
pip list | grep -E "(openai|gkeepapi|chromadb)"

# 📁 Verificar permissões de diretórios
ls -la obsidian_notes/ chroma_db/ logs/

# 🔐 Verificar arquivo de configuração
cat .env/config | grep -v TOKEN  # Mostra config sem expor tokens
```

### 🆘 Debug Modo Verbose

```bash
# Executar com logs detalhados
python src/main.py --verbose

# Ou habilitar debug no código
export PYTHONPATH=.
export DEBUG=1
python src/main.py
```

### 📞 Suporte

1. **📖 Documentação**: Verifique [CONFIG.md](CONFIG.md) para setup detalhado
2. **🔍 Issues**: Reporte problemas no [GitHub Issues](https://github.com/thiago-gmacedo/ocr-keep-obsidian/issues)
3. **📧 Contato**: Para dúvidas específicas, abra uma issue com:
   - Logs relevantes (sem expor credenciais)
   - Versão do Python e SO
   - Passos para reproduzir o problema

## 🗺️ Roadmap & Próximos Passos

### 🎯 Em Desenvolvimento (v2.1.0)
- [ ] **🌐 Interface Web**: Dashboard para monitoramento e controle
- [ ] **📱 App Mobile**: Companion app para captura direta
- [ ] **🔄 Sync Bidireccional**: Obsidian → Keep para edições
- [ ] **🎨 Themes Obsidian**: Templates customizáveis para diferentes tipos de nota

### 🚀 Planejado (v2.2.0)
- [ ] **🤖 Auto-categorização**: IA para classificação automática de notas
- [ ] **📊 Analytics**: Dashboard com estatísticas de produtividade
- [ ] **🔗 Integrações**: Notion, Anki, Logseq
- [ ] **🌍 Multi-idiomas**: Suporte completo a idiomas não-latinos

### 💡 Ideias Futuras
- [ ] **🧠 Knowledge Graph**: Visualização de conexões entre notas
- [ ] **🎤 Audio OCR**: Processamento de notas de voz
- [ ] **📷 Batch Processing**: Processamento de múltiplas imagens simultaneamente
- [ ] **☁️ Cloud Deploy**: Deploy automatizado em cloud (AWS, GCP, Azure)

### 🤝 Como Contribuir

**Áreas que precisam de ajuda:**
- 🐛 **Testing**: Testar em diferentes SOs e configurações
- 📖 **Documentação**: Melhorar guides e tutoriais
- 🌍 **Localização**: Tradução para outros idiomas
- 🎨 **UI/UX**: Design da interface web planejada
- 🔧 **DevOps**: Containerização e deploy automatizado

**Para contribuir:**
1. 🍴 Fork o projeto
2. 🌿 Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push para a branch (`git push origin feature/AmazingFeature`)
5. 🔃 Abra um Pull Request

## 📈 Changelog

### 🚀 v2.0.0 (29/05/2025) - Major Release
- ✨ **Execução agendada** automática para servidores
- ✨ **Caminhos configuráveis** via .env (OBS_PATH, CHROMA_DB_PATH)  
- ✨ **Sistema de logs** robusto com timestamps
- ✨ **Setup automático** com verificação de dependências
- ✨ **Deploy universal** compatível com Linux/macOS
- ✨ **Criação automática** de diretórios inexistentes
- ✨ **Suporte ~** (home directory) em caminhos
- ✨ **Prevenção múltiplas execuções** no mesmo horário
- 🔒 **Segurança melhorada** com permissões restritivas para .env

### 📝 v1.0.0 (28/05/2025) - Initial Release
- 🎉 Pipeline completo funcional
- 🔗 Integração Google Keep + GPT-4 Vision + Obsidian + ChromaDB
- 🔄 Sistema de controle de duplicatas
- 🏷️ Filtragem por labels/tags
- 📚 Documentação completa inicial

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

```
MIT License

Copyright (c) 2025 Thiago Macedo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

### 🤝 Código de Conduta

Este projeto adere ao [Contributor Covenant](https://www.contributor-covenant.org/) código de conduta. Ao participar, você concorda em seguir este código.

## 🙏 Agradecimentos

- **OpenAI** pelo GPT-4 Vision que tornou OCR de manuscritos possível
- **ChromaDB** pela excelente biblioteca de vector database
- **gkeepapi** por tornar a integração com Google Keep simples
- **Sentence Transformers** pelos embeddings multilingues de qualidade
- **Obsidian** pela inspiração no formato de notas estruturadas

## 📬 Contato & Suporte

- **📧 Email**: [seu-email@exemplo.com](mailto:seu-email@exemplo.com)
- **🐙 GitHub**: [@thiago-gmacedo](https://github.com/thiago-gmacedo)
- **🐛 Issues**: [Reportar Problemas](https://github.com/thiago-gmacedo/ocr-keep-obsidian/issues)
- **💬 Discussões**: [GitHub Discussions](https://github.com/thiago-gmacedo/ocr-keep-obsidian/discussions)

---

<div align="center">

**🚀 Transforme suas ideias manuscritas em conhecimento digital estruturado**

[![⭐ Star no GitHub](https://img.shields.io/github/stars/thiago-gmacedo/ocr-keep-obsidian?style=social)](https://github.com/thiago-gmacedo/ocr-keep-obsidian)
[![🍴 Fork](https://img.shields.io/github/forks/thiago-gmacedo/ocr-keep-obsidian?style=social)](https://github.com/thiago-gmacedo/ocr-keep-obsidian/fork)

*Desenvolvido com ❤️ por [Thiago Macedo](https://github.com/thiago-gmacedo)*

</div>