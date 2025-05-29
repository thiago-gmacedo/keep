# 📝 OCR de Notas Manuscritas (Versão 0.7.0)

Ferramenta avançada para extrair e estruturar texto de imagens de notas manuscritas utilizando a API de visão OpenAI (GPT-4o). Esta versão oferece processamento local de imagens, integração completa com Google Keep, geração automática de JSON estruturado e exportação para Obsidian com YAML front-matter.

## ✨ Funcionalidades Principais

- 🔍 **OCR Avançado**: Extração de texto manuscrito usando GPT-4 Vision
- 📋 **Integração Google Keep**: Processa notas diretamente do Google Keep
- 🗂️ **Estruturação Inteligente**: Converte texto em JSON estruturado com campos específicos
- 📚 **Exportação Obsidian**: Gera arquivos Markdown com YAML front-matter compatíveis
- 🏷️ **Sistema de Labels**: Filtra notas por etiquetas do Google Keep
- 📅 **Filtros Avançados**: Processa notas de hoje, todas ou apenas não processadas
- 🔄 **Controle de Processamento**: Evita reprocessar notas já analisadas
- 🎯 **Múltiplas Estratégias de Download**: Fallback robusto para baixar anexos
- 🆔 **IDs Únicos**: Geração de source_id e vector_id para organização
- 📊 **Validação de Dados**: Verificação de estrutura JSON antes da conversão

## 🚀 Instalação Rápida

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositorio>
   cd keep
   ```

2. **Configure o ambiente virtual**
   ```bash
   # Criar ambiente virtual
   python3 -m venv venv
   
   # Ativar ambiente virtual
   source venv/bin/activate  # Linux/Mac
   # ou
   # venv\Scripts\activate    # Windows
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as credenciais**
   ```bash
   # Crie o diretório de configuração
   mkdir -p .env
   
   # Configure suas credenciais
   nano .env/config
   ```

## ⚙️ Configuração

### 📋 Arquivo `.env/config`

Crie o arquivo `.env/config` com suas credenciais:

```bash
# Chave da API OpenAI (obrigatória)
OPENAI_API_KEY=sua-chave-openai-aqui

# Credenciais do Google Keep (para integração)
GOOGLE_EMAIL=seu-email@gmail.com
GOOGLE_MASTER_TOKEN=seu-master-token-aqui
```

### 🔑 Como obter o Master Token do Google Keep

1. **Instale o gkeepapi**
   ```bash
   pip install gkeepapi
   ```

2. **Execute o script de autenticação**
   ```python
   import gkeepapi
   keep = gkeepapi.Keep()
   
   # Faça login com email e senha
   success = keep.login('seu-email@gmail.com', 'sua-senha')
   
   # Obtenha o master token
   token = keep.getMasterToken()
   print(f"Master Token: {token}")
   ```

3. **⚠️ Importante**: Após obter o token, remova a senha do código por segurança!

**Nota**: O master token tem validade prolongada e é mais seguro que armazenar uma senha. Veja mais detalhes em [CONFIG.md](CONFIG.md).

## 🎯 Como Usar

### 1. **Modo Local - Imagem Específica**
```bash
# Processar imagem padrão (image/ink.png)
python ocr_extractor.py

# Processar imagem específica
python ocr_extractor.py caminho/para/sua/imagem.png
```

### 2. **Modo Google Keep - Processamento por Label**
```bash
# Processar notas com uma label específica
python ocr_extractor.py MinhaLabel
```

**Opções de filtro disponíveis:**
- `1`: Apenas notas de hoje
- `2`: Todas as notas com a label
- `3`: Apenas notas não processadas anteriormente

### 📝 Como usar labels no Google Keep

Para utilizar a funcionalidade de busca por label:

1. Acesse o [Google Keep](https://keep.google.com/) no seu navegador
2. Crie uma nova nota ou abra uma existente
3. Clique no ícone de etiquetas (rótulos) no menu inferior
4. Crie uma nova etiqueta ou selecione uma existente
5. Use esta etiqueta como parâmetro ao executar o script

## 📁 Estrutura do Projeto

```
keep/
├── src/
│   ├── __init__.py
│   ├── obsidian_writer.py      # Gerador de arquivos Obsidian
│   └── __pycache__/
├── image/                      # Imagens baixadas e processadas
│   ├── ink.png                 # Imagem padrão para testes
│   ├── *.png                   # Imagens baixadas do Google Keep
│   ├── *.json                  # JSONs estruturados gerados
│   └── *.txt                   # Transcrições em texto puro
├── obsidian_notes/             # Arquivos Markdown gerados
│   ├── 260525.md
│   ├── 270525.md
│   └── *.md
├── .env/
│   └── config                  # Credenciais (não commitado)
├── .processed_notes.json       # Registro de notas processadas
├── ocr_extractor.py           # Script principal
├── requirements.txt           # Dependências
├── README.md                  # Esta documentação
└── CONFIG.md                  # Configurações detalhadas
```

## 📊 Formato de Saída

O sistema gera três tipos de arquivo automaticamente:

### 📄 1. JSON Estruturado
```json
{
  "title": "28/05/25 - segunda-feira",
  "data": "28/05/2025",
  "summary": "Lista de tarefas diárias e nota sobre problema resolvido pela manhã.",
  "keywords": ["tarefas", "análise de dados", "mapeamento", "cabelo", "escritório"],
  "tasks": [
    {"task": "Skin care", "status": "done"},
    {"task": "Arrumar escritório", "status": "done"},
    {"task": "Marcar corte cabelo", "status": "done"},
    {"task": "Estudar análise de dados", "status": "todo"}
  ],
  "notes": [
    "Pela manhã arrumei problema de mapeamento."
  ],
  "reminders": []
}
```

### 📚 2. Markdown para Obsidian
```markdown
---
title: "28/05/25 - segunda-feira"
created: "2025-05-28T00:00:00"
last_modified: "2025-05-28T18:34:49"
embedding_date: "2025-05-28T18:34:49"
source_id: "keep_280525_segunda_feira"
vector_id: "a14ab72e6058c68d1743f129fd5703e9573b7016eab3a3ed42516c21cf002cb0"
summary: "Lista de tarefas diárias e nota sobre problema resolvido pela manhã."
keywords:
  - "tarefas"
  - "análise de dados"
  - "mapeamento"
tasks:
  - task: "Skin care"
    status: "done"
  - task: "Estudar análise de dados"
    status: "todo"
notes:
  - "Pela manhã arrumei problema de mapeamento."
reminders: []
---

# 28/05/25 - segunda-feira

## Resumo
Lista de tarefas diárias e nota sobre problema resolvido pela manhã.

## Tarefas
- ✅ Skin care
- ✅ Arrumar escritório
- ✅ Marcar corte cabelo
- 📋 Estudar análise de dados

## Notas
- Pela manhã arrumei problema de mapeamento.
```

### 📄 3. Texto Puro (Fallback)
Quando o OCR não consegue estruturar em JSON, salva a transcrição em arquivo `.txt`.

## 🔧 Funcionalidades Avançadas

### 🎯 Múltiplas Estratégias de Download
O sistema utiliza 3 estratégias para baixar anexos do Google Keep:
1. **getMediaLink**: Método oficial preferido
2. **Dados binários diretos**: Para desenhos e imagens
3. **URL direta**: Baseada no server_id

### 🆔 Sistema de IDs Únicos
- **source_id**: Baseado no título e data para organização
- **vector_id**: Hash SHA256 do conteúdo para deduplicação

### 📅 Processamento de Datas
- Suporte a múltiplos formatos de data
- Fallback para data atual se não detectada
- Formatação ISO para compatibilidade

### 🔄 Controle de Reprocessamento
- Registro automático em `.processed_notes.json`
- Organização por label
- Opção de processar apenas notas novas

## 🛠️ Dependências

```
openai>=1.0.0
gkeepapi>=0.13.0
Pillow>=9.0.0
requests>=2.28.0
```

## 📋 Exemplos de Uso

### Fluxo Típico - Google Keep
1. Crie uma label no Google Keep (ex: "OCR")
2. Adicione notas manuscritas com essa label
3. Execute: `python ocr_extractor.py OCR`
4. Escolha filtro de data (1, 2 ou 3)
5. Aguarde o processamento
6. Confira os arquivos em:
   - `image/` (imagens e JSONs)
   - `obsidian_notes/` (arquivos Markdown)

### Fluxo Típico - Imagem Local
1. Coloque sua imagem em `image/ink.png` ou use caminho específico
2. Execute: `python ocr_extractor.py`
3. Confira os arquivos gerados:
   - `imagem.json` (dados estruturados)
   - `obsidian_notes/arquivo.md` (Obsidian)

## 🔧 Solução de Problemas

### ❌ Erro de Rede (`Network is unreachable`)
```bash
# Teste sua conectividade
ping google.com
curl -I https://keep.google.com

# Verifique proxy/VPN
echo $HTTP_PROXY
echo $HTTPS_PROXY
```

### 🔑 Problemas de Autenticação
- Verifique se o email está correto
- Gere um novo master token
- Confirme que o arquivo `.env/config` está configurado corretamente

### 📁 Problemas de Permissão
```bash
# Ajuste permissões se necessário
chmod +x ocr_extractor.py
chmod 600 .env/config  # Proteger credenciais
```

### 🖼️ Problemas com Imagens
- Formatos suportados: PNG, JPG, JPEG
- Verifique se a imagem não está corrompida
- Certifique-se de que há texto manuscrito visível

## 📈 Exemplo de Resultado Completo

```
🔄 Modo Google Keep: Buscando notas com a label 'diario'

Escolha uma opção:
1. Processar apenas notas de hoje
2. Processar todas as notas com esta label
3. Processar apenas notas novas (não processadas anteriormente)

Sua escolha [1/2/3]: 1

✅ Encontradas 2 notas para processar.

==================================================
📝 Nota: 28/05/25 (ID: 1970e1d4)
==================================================
📎 Encontrados 1 anexos.

🖼️ Processando anexo 1...
🔄 Baixando anexo...
🔄 Tentando download via getMediaLink (método principal)...
✅ Imagem salva com sucesso via getMediaLink
💾 Anexo salvo em: /home/user/keep/image/280525_20250528183459_1970e1d4_1.png
✅ Imagem validada (Formato: PNG)
🔍 Executando OCR com OpenAI Vision...

📄 Transcrição:
--------------------------------------------------
{
  "title": "28/05/25 - segunda-feira",
  "data": "28/05/2025",
  "summary": "Lista de tarefas diárias e nota sobre problema resolvido.",
  ...
}
--------------------------------------------------
✅ JSON estruturado salvo em: 280525_20250528183459_1970e1d4_1.json
🔄 Convertendo automaticamente para Obsidian...
✅ Arquivo Obsidian gerado com sucesso!

==================================================
✅ Processamento concluído
- Notas processadas: 2
- Notas puladas (já processadas): 0
- Total considerado: 2
==================================================
```

## 🏷️ Versão Atual: 0.7.0

**Principais melhorias desta versão:**
- ✅ Integração completa com Google Keep
- ✅ Geração automática de arquivos Obsidian
- ✅ Sistema de controle de processamento
- ✅ Múltiplas estratégias de download de imagens
- ✅ Validação robusta de estruturas JSON
- ✅ IDs únicos para organização e deduplicação
- ✅ Suporte a múltiplos formatos de data
- ✅ Tratamento de erros robusto

## 📞 Suporte

- 📧 **Issues**: Use o sistema de issues do repositório
- 📚 **Documentação**: Veja `CONFIG.md` para configurações avançadas
- 🔧 **Debug**: Logs detalhados são exibidos durante o processamento

---

**⚠️ Aviso de Segurança**: Nunca commite suas credenciais! O arquivo `.env/config` deve estar no `.gitignore`.

**📝 Nota sobre Formatos**: O sistema detecta automaticamente se o OCR retorna JSON estruturado ou texto puro, salvando no formato apropriado e gerando arquivos Obsidian quando possível.
