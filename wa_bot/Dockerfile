FROM puppeteer/puppeteer:20.9.0

# Definir diretório de trabalho
WORKDIR /app/wa_bot

# Copiar package.json e package-lock.json
COPY package*.json ./

# Instalar dependências Node.js
RUN npm install --production

# Copiar código da aplicação
COPY . .

# Tornar script de start executável
RUN chmod +x start.sh

# Criar diretório de sessões
RUN mkdir -p sessions && chmod 755 sessions

# Executar como usuário não-root
USER pptruser

# Comando para iniciar o bot
CMD ["./start.sh"]
