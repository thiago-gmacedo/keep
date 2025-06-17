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

# Definir variável de ambiente para Chromium
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Criar diretório da aplicação
WORKDIR /app/wa_bot

# Copiar package.json e package-lock.json (se existir)
COPY package*.json ./

# Instalar dependências Node.js
RUN npm install --production

# Copiar código da aplicação
COPY . .

# Criar usuário não-root para segurança
RUN groupadd -g 1001 appgroup && \
    useradd -r -u 1001 -g appgroup appuser && \
    chown -R appuser:appgroup /app

USER appuser

# Expor porta (opcional, para healthcheck)
EXPOSE 3000

# Comando para iniciar o bot
CMD ["npm", "start"]
