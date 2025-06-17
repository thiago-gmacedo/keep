# Server Setup Guide

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

1. **Copie o diretório de sessões** para o servidor:

```bash
# Do local para o servidor
scp -r wa_bot/sessions/ user@servidor:/caminho/para/keep/wa_bot/
```

2. **Inicie os containers** no servidor:

```bash
# No servidor
docker compose up -d wa_bot
```

3. **Verifique os logs**:

```bash
docker compose logs -f wa_bot
```

Você deve ver a mensagem "🔐 Autenticado com sucesso!" seguida de "✅ WhatsApp Web está pronto!".

### Uso

Envie mensagens que começam com `!` para o número cadastrado:

- `!listar tarefas pendentes` - Lista tarefas pendentes
- `!resumo da semana` - Resumo das anotações da semana
- `!encontrar projeto X` - Busca por projeto específico

### Troubleshooting

#### Bot não autentica
- Verifique se o arquivo de sessão foi copiado corretamente
- Tente fazer login local novamente
- Verifique se o WhatsApp Web não está conectado em outro dispositivo

#### Erro de conexão com pipeline
- Verifique se o serviço `python_pipeline` está rodando:
  ```bash
  docker compose ps python_pipeline
  ```
- Teste o endpoint diretamente:
  ```bash
  curl "http://localhost:8000/query?text=teste"
  ```

#### Container wa_bot não inicia
- Verifique os logs:
  ```bash
  docker compose logs wa_bot
  ```
- Reconstrua a imagem:
  ```bash
  docker compose build wa_bot
  ```

### Comandos Úteis

```bash
# Parar apenas o bot
docker compose stop wa_bot

# Reiniciar o bot
docker compose restart wa_bot

# Ver logs em tempo real
docker compose logs -f wa_bot

# Executar localmente para debug
cd wa_bot
PIPELINE_URL=http://localhost:8000 node index.js
```

### Segurança

- O arquivo de sessão contém credenciais sensíveis
- Mantenha o arquivo `wa_bot/sessions/` seguro e privado
- Não compartilhe ou versione os arquivos de sessão
- Use apenas números de WhatsApp confiáveis
