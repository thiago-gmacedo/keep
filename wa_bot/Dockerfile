FROM node:20-bullseye

# Instalar dependências do sistema para Chromium
RUN apt-get update && apt-get install -y \
    chromium \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libxss1 \
    libgconf-2-4 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Verificar o caminho correto do Chromium
RUN which chromium || which chromium-browser || echo "Chromium não encontrado!"

# Definir variável de ambiente para Chromium - CAMINHO ATUALIZADO!
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true

# Criar diretório da aplicação
WORKDIR /app/wa_bot

# Copiar package.json e package-lock.json (se existir)
COPY package*.json ./

# Instalar dependências Node.js
RUN npm install --production

# Copiar código da aplicação
COPY . .

# Tornar script de start executável
RUN chmod +x start.sh

# Criar usuário não-root para segurança
RUN groupadd -g 1001 appgroup && \
    useradd -r -u 1001 -g appgroup appuser

# Criar diretório de sessões e ajustar permissões APÓS criar o usuário
RUN mkdir -p sessions && \
    chmod 755 sessions && \
    chown -R appuser:appgroup /app

USER appuser

# Expor porta (opcional, para healthcheck)
EXPOSE 3000

# Comando para iniciar o bot
CMD ["./start.sh"]
