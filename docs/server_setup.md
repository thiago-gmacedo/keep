# Server Setup Guide

## Deploy Completo com Docker

O sistema Keep OCR agora roda completamente em Docker com 3 serviços:
- **Web Server**: API REST para consultas (porta 8000)
- **Pipeline Scheduler**: Executa pipeline às 23:45 diariamente
- **WhatsApp Bot**: Bot para consultas via WhatsApp

### Deploy Automático

```bash
# Clone e acesse o projeto
git clone <repo> && cd keep
git checkout feat/wa-bot

# Deploy completo
./deploy.sh
```

## Bot WhatsApp

O bot WhatsApp permite fazer consultas ao pipeline OCR Keep através de mensagens que começam com `!`.

### Configuração Inicial

#### 1. Login Local (Primeira Configuração)

Para configurar o bot pela primeira vez, execute localmente para gerar o QR code:

```bash
cd wa_bot
npm install
node index.js
```

1. **Escaneie o QR code** que aparece no terminal com seu WhatsApp
2. Aguarde a mensagem "✅ WhatsApp Web está pronto!"
3. **Pare o processo** (Ctrl+C)
4. **Copie o arquivo de sessão** gerado:

```bash
# O arquivo será criado em wa_bot/sessions/
ls -la wa_bot/sessions/
```

#### 2. Deploy no Servidor

1. **Execute o deploy automático**:

```bash
./deploy.sh
```

2. **Configure WhatsApp (primeira vez)**:

```bash
# Ver logs do bot para QR code
docker-compose logs -f wa_bot

# Aguarde o QR aparecer nos logs, escaneie com WhatsApp
# O bot será autenticado automaticamente
```

3. **Verificar status**:

```bash
docker-compose ps
curl http://localhost:8000/health
```

### Monitoramento

```bash
# Ver todos os logs
docker-compose logs -f

# Ver logs específicos
docker-compose logs -f wa_bot          # Bot WhatsApp
docker-compose logs -f web_server      # API REST
docker-compose logs -f pipeline_scheduler  # Scheduler

# Verificar status dos containers
docker-compose ps

# Testar API
curl "http://localhost:8000/query?text=listar tarefas"
```

### Uso

Envie mensagens que começam com `!` para o número cadastrado:

- `!listar tarefas pendentes` - Lista tarefas pendentes
- `!resumo da semana` - Resumo das anotações da semana
- `!encontrar projeto X` - Busca por projeto específico

### Comandos Úteis

```bash
# Reiniciar serviços
docker-compose restart wa_bot
docker-compose restart web_server

# Parar tudo
docker-compose down

# Reconstruir e reiniciar
docker-compose build && docker-compose up -d

# Backup de dados
tar -czf backup-$(date +%Y%m%d).tar.gz vault/ .env/

# Ver estatísticas
curl http://localhost:8000/stats
```

### Troubleshooting

#### Bot não autentica
- Verifique logs: `docker-compose logs wa_bot`
- QR code aparece nos logs na primeira execução
- Certifique-se que WhatsApp Web não está conectado em outro lugar

#### API não responde
- Verifique: `curl http://localhost:8000/health`
- Ver logs: `docker-compose logs web_server`
- Verificar se ChromaDB tem dados indexados

#### Pipeline não executa
- Ver logs do scheduler: `docker-compose logs pipeline_scheduler`
- Verificar horário configurado (23:45 por padrão)
- Testar execução manual no container

#### Containers não iniciam
- Verificar Docker: `docker --version`
- Verificar compose: `docker-compose --version`
- Reconstruir: `docker-compose build --no-cache`

### Segurança

- O arquivo de sessão contém credenciais sensíveis
- Mantenha o arquivo `wa_bot/sessions/` seguro e privado
- Não compartilhe ou versione os arquivos de sessão
- Use apenas números de WhatsApp confiáveis
