const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');

// Importar node-fetch dinamicamente
let fetch;

// Configurações
const PIPELINE_URL = process.env.PIPELINE_URL || 'http://python_pipeline:8000';
const SESSION_PATH = './sessions/session.json';

console.log('🚀 Iniciando WhatsApp Bot - Keep OCR Query');
console.log(`📡 Pipeline URL: ${PIPELINE_URL}`);

// Criar diretório de sessões se não existir
const sessionsDir = path.dirname(SESSION_PATH);
if (!fs.existsSync(sessionsDir)) {
    fs.mkdirSync(sessionsDir, { recursive: true });
    console.log(`📁 Diretório de sessões criado: ${sessionsDir}`);
}

// Configurar cliente WhatsApp
const client = new Client({
    authStrategy: new LocalAuth({
        clientId: "keep-ocr-bot",
        dataPath: "./sessions"
    }),
    puppeteer: {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--single-process',
            '--disable-gpu'
        ],
        executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/google-chrome-stable'
    }
});

// Adicionar logs detalhados para depuração
console.log('🔄 Puppeteer configurado com configuração otimizada para Docker.');
console.log('📁 Caminho do Chrome:', process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/google-chrome-stable');

// Função para consultar o pipeline
async function queryPipeline(text) {
    try {
        // Carregar fetch se ainda não foi carregado
        if (!fetch) {
            const fetchModule = await import('node-fetch');
            fetch = fetchModule.default;
        }
        
        const url = `${PIPELINE_URL}/query?text=${encodeURIComponent(text)}`;
        console.log(`🔍 Consultando pipeline: ${text.substring(0, 50)}...`);
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Pipeline error ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.text();
        console.log(`✅ Resposta recebida (${result.length} chars)`);
        return result;
        
    } catch (error) {
        console.error(`❌ Erro ao consultar pipeline: ${error.message}`);
        throw error;
    }
}

// Event listeners
client.on('qr', (qr) => {
    console.log('📱 QR Code gerado! Escaneie com seu WhatsApp:');
    qrcode.generate(qr, { small: true });
    console.log('💡 Dica: Após escanear, a sessão será salva e não será necessário escanear novamente.');
});

client.on('ready', () => {
    console.log('✅ WhatsApp Web está pronto!');
    console.log('🔄 Bot está rodando e aguardando mensagens que começam com "!"');
});

client.on('authenticated', () => {
    console.log('🔐 Autenticado com sucesso!');
});

client.on('auth_failure', (msg) => {
    console.error('❌ Falha na autenticação:', msg);
});

client.on('disconnected', (reason) => {
    console.log('🔌 Desconectado:', reason);
});

// Listener principal para mensagens
client.on('message', async (msg) => {
    // Ignorar mensagens de grupos, status e que não começam com !
    if (msg.from.includes('@g.us') || msg.from.includes('status@broadcast') || !msg.body.startsWith('!')) {
        return;
    }
    
    // Extrair query (remover o !)
    const query = msg.body.slice(1).trim();
    
    if (!query) {
        await msg.reply('❓ Por favor, envie uma pergunta após o "!"\nExemplo: !listar tarefas pendentes');
        return;
    }
    
    console.log(`📨 Nova mensagem de ${msg.from}: ${query}`);
    
    try {
        // Indicar que está digitando
        await msg.reply('🔍 Consultando suas notas...');
        
        // Consultar o pipeline
        const answer = await queryPipeline(query);
        
        // Enviar resposta
        await msg.reply(answer);
        
        console.log(`✅ Resposta enviada para ${msg.from}`);
        
    } catch (error) {
        console.error(`❌ Erro ao processar mensagem: ${error.message}`);
        await msg.reply('❌ Erro ao consultar notas. Tente mais tarde.\n\nSe o problema persistir, verifique se o sistema está funcionando.');
    }
});

// Tratamento de erros gerais
client.on('error', (error) => {
    console.error('❌ Erro do cliente WhatsApp:', error);
});

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('\n🛑 Recebido sinal de interrupção. Desconectando...');
    await client.destroy();
    process.exit(0);
});

process.on('SIGTERM', async () => {
    console.log('\n🛑 Recebido sinal de término. Desconectando...');
    await client.destroy();
    process.exit(0);
});

// Inicializar cliente
console.log('🔄 Inicializando cliente WhatsApp...');
client.initialize();
