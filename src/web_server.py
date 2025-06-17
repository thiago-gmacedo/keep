#!/usr/bin/env python3
"""
Servidor Web para API do pipeline OCR Keep
Expõe endpoint HTTP para consultas RAG via WhatsApp bot
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager
import sys
import os
from pathlib import Path
import logging
import uvicorn

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instância global do ChatRAG
chat_rag = None

def initialize_chat_rag():
    """Inicializa o sistema ChatRAG"""
    global chat_rag
    try:
        # Importar ChatRAG
        sys.path.insert(0, str(ROOT_DIR / 'scripts'))
        from chat_rag import ChatRAG
        
        chat_rag = ChatRAG()
        logger.info("✅ Sistema ChatRAG inicializado com sucesso")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar ChatRAG: {e}")
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciamento do ciclo de vida da aplicação"""
    # Startup
    logger.info("🚀 Iniciando servidor web do pipeline Keep...")
    success = initialize_chat_rag()
    if not success:
        logger.error("❌ Falha na inicialização. Servidor pode não funcionar corretamente.")
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando servidor web do pipeline Keep...")

app = FastAPI(
    title="Keep OCR Pipeline API",
    description="API para consultas ao sistema RAG baseado em notas manuscritas",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    """Verificação de saúde do servidor"""
    if chat_rag is None:
        raise HTTPException(status_code=503, detail="Sistema RAG não inicializado")
    return {"status": "healthy", "service": "keep-ocr-pipeline"}

@app.get("/query", response_class=PlainTextResponse)
async def query_notes(text: str = Query(..., description="Texto da consulta")):
    """
    Endpoint para consultas ao sistema RAG
    
    Args:
        text: Texto da consulta/pergunta
        
    Returns:
        Resposta em texto simples
    """
    if chat_rag is None:
        raise HTTPException(status_code=503, detail="Sistema RAG não inicializado")
    
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Parâmetro 'text' é obrigatório")
    
    try:
        logger.info(f"📝 Nova consulta: {text[:100]}...")
        
        # Buscar contexto
        context = chat_rag.search_context(text.strip())
        
        # Gerar resposta
        response = chat_rag.generate_response(text.strip(), context)
        
        logger.info(f"✅ Resposta gerada ({len(response)} chars)")
        return response
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar consulta: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Estatísticas do sistema"""
    if chat_rag is None:
        raise HTTPException(status_code=503, detail="Sistema RAG não inicializado")
    
    try:
        stats = chat_rag.indexer.get_collection_stats()
        return {
            "notes_count": stats.get('count', 0),
            "chunk_count": chat_rag.rag_chunk_count,
            "database_path": str(chat_rag.indexer.persist_directory)
        }
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

if __name__ == "__main__":
    # Configuração para desenvolvimento
    uvicorn.run(
        "web_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
