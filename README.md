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

## ⚙️ Configuração

Veja o arquivo [CONFIG.md](CONFIG.md) para instruções detalhadas de configuração.

### Estrutura do arquivo `.env/config`:
```env
GOOGLE_EMAIL=seu.email@gmail.com
GOOGLE_MASTER_TOKEN=seu_master_token_aqui
OPENAI_API_KEY=sk-sua_chave_openai_aqui
```

## 🚀 Uso

### Executar pipeline completo:
```bash
python main.py
```

### Filtrar por label específica:
```bash
python main.py "Anotações diárias"
python main.py "OCR"
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
├── src/
│   ├── obsidian_writer.py  # Geração arquivos Obsidian
│   ├── chroma_indexer.py   # Indexação ChromaDB
│   └── README_CHROMA.md    # Documentação ChromaDB
├── images/                 # Imagens baixadas
│   └── processed/          # Imagens processadas
├── obsidian_notes/         # Arquivos .md gerados
├── chroma_db/              # Banco vetorial ChromaDB
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

## 📝 Changelog

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