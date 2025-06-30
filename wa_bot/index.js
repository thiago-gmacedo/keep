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

// Variáveis para reconexão
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

// Configurar cliente WhatsApp com opções otimizadas
const client = new Client({
    authStrategy: new LocalAuth({
        clientId: "keep-ocr-bot",
        dataPath: "./sessions"
    }),
    puppeteer: {
        // Usar novo modo headless para compatibilidade
        headless: 'new',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu',
            '--disable-extensions',
            '--disable-component-extensions-with-background-pages',
            '--disable-default-apps',
            '--mute-audio',
            '--no-default-browser-check',
            '--disable-features=site-per-process',
            '--disable-web-security'
        ],
        executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/google-chrome-stable',
        timeout: 120000, // 2 minutos de timeout
        ignoreHTTPSErrors: true
    },
    webVersionCache: {
        type: 'none', // Desativar cache de versão
    }
});

// Adicionar logs detalhados para depuração
console.log('🔄 Puppeteer configurado com configuração robusta para ambientes Docker.');
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

// Função para inicializar com tratamento de erro
function initializeClient() {
    try {
        console.log('🔄 Inicializando cliente WhatsApp...');
        client.initialize().catch(error => {
            console.error('❌ Erro durante a inicialização:', error);
            handleReconnect();
        });
    } catch (error) {
        console.error('❌ Exceção ao inicializar cliente:', error);
        handleReconnect();
    }
}

// Função para lidar com reconexão
function handleReconnect() {
    reconnectAttempts++;
    
    if (reconnectAttempts <= maxReconnectAttempts) {
        console.log(`🔄 Tentativa de reconexão ${reconnectAttempts}/${maxReconnectAttempts} em 15 segundos...`);
        setTimeout(() => {
            initializeClient();
        }, 15000); // 15 segundos entre tentativas
    } else {
        console.error('❌ Número máximo de tentativas de reconexão atingido. Reiniciando container...');
        process.exit(1); // Docker irá reiniciar o container se configurado com restart policy
    }
}

// Event listeners
client.on('qr', (qr) => {
    console.log('📱 QR Code gerado! Escaneie com seu WhatsApp:');
    qrcode.generate(qr, { small: true });
    console.log('💡 Dica: Após escanear, a sessão será salva e não será necessário escanear novamente.');
    // Reset reconexão após QR bem-sucedido
    reconnectAttempts = 0;
});

client.on('ready', () => {
    console.log('✅ WhatsApp Web está pronto!');
    console.log('🔄 Bot está rodando e aguardando mensagens que começam com "!"');
    // Reset reconexão após inicialização bem-sucedida
    reconnectAttempts = 0;
});

client.on('authenticated', () => {
    console.log('🔐 Autenticado com sucesso!');
    // Reset reconexão após autenticação bem-sucedida
    reconnectAttempts = 0;
});

client.on('auth_failure', (msg) => {
    console.error('❌ Falha na autenticação:', msg);
    handleReconnect();
});

client.on('disconnected', (reason) => {
    console.log('🔌 Desconectado:', reason);
    handleReconnect();
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

// Inicializar cliente com tratamento de erros
initializeClient();
