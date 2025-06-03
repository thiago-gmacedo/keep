#!/usr/bin/env python3
"""
Chat RAG - Interface de chat com Retrieval-Augmented Generation

Este script implementa um chatbot que utiliza as notas indexadas no ChromaDB
como contexto para gerar respostas através de modelos LLM (GPT-4).

Combina busca semântica + geração de texto para criar um assistente pessoal
baseado nas suas próprias anotações manuscritas.

Autor: Thiago Macedo
Data: 02/06/2025
Versão: 1.0.0
"""

import sys
import os
import json
import readline
from pathlib import Path
from typing import List, Dict, Any, Optional

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

# Importar módulos necessários
try:
    import openai
    from src.chroma_indexer import ChromaIndexer
    from src.rag_formatter import format_for_rag, format_for_rag_detailed, estimate_tokens
    from src.ocr_extractor import load_keep_credentials
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("\nDependências necessárias:")
    print("  - pip install openai")
    print("  - Certifique-se de que todos os módulos estão no local correto")
    sys.exit(1)


class ChatRAG:
    """Interface de chat com Retrieval-Augmented Generation"""
    
    def __init__(self):
        """Inicializa o sistema RAG"""
        self.setup_openai()
        self.setup_indexer() 
        self.setup_history()
        self.conversation_history = []
        
    def setup_openai(self):
        """Configura cliente OpenAI"""
        try:
            # Carregar configurações
            config = load_keep_credentials()
            api_key = config.get('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                raise ValueError("OPENAI_API_KEY não encontrada")
            
            openai.api_key = api_key
            self.openai_client = openai
            
            # Testar conexão
            try:
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1
                )
                print("✅ Conexão OpenAI estabelecida com sucesso")
            except Exception as e:
                print(f"⚠️ Aviso: Não foi possível testar a conexão OpenAI: {e}")
                
        except Exception as e:
            print(f"❌ Erro ao configurar OpenAI: {e}")
            print("Certifique-se de que OPENAI_API_KEY está configurada no .env/config")
            sys.exit(1)
    
    def setup_indexer(self):
        """Configura o indexador ChromaDB"""
        try:
            # Carregar configuração de caminhos
            config = load_keep_credentials()
            chroma_path = config.get('CHROMA_DB_PATH', str(ROOT_DIR / 'chroma_db'))
            
            # Inicializar indexador
            self.indexer = ChromaIndexer(persist_directory=chroma_path)
            
            # Verificar se há dados indexados
            stats = self.indexer.get_collection_stats()
            total_notes = stats.get('total_notes', 0)
            
            if total_notes == 0:
                print("⚠️ Aviso: Nenhuma nota indexada encontrada no ChromaDB")
                print("Execute o pipeline principal primeiro para indexar suas notas")
                print("Comando: python -m src.main")
                
                choice = input("\nDeseja continuar mesmo assim? [s/N]: ")
                if choice.lower() != 's':
                    sys.exit("Operação cancelada pelo usuário.")
            else:
                print(f"✅ ChromaDB carregado: {total_notes} notas indexadas")
                
        except Exception as e:
            print(f"❌ Erro ao configurar ChromaDB: {e}")
            sys.exit(1)
    
    def setup_history(self):
        """Configura histórico de comandos"""
        self.history_file = ROOT_DIR / '.chat_rag_history'
        
        # Carregar histórico se existir
        if self.history_file.exists():
            try:
                readline.read_history_file(str(self.history_file))
            except Exception:
                pass  # Ignorar erros de histórico
    
    def save_history(self):
        """Salva histórico de comandos"""
        try:
            readline.write_history_file(str(self.history_file))
        except Exception:
            pass  # Ignorar erros de histórico
    
    def search_context(self, query: str, n_results: int = 5) -> str:
        """
        Busca contexto relevante no ChromaDB
        
        Args:
            query (str): Consulta do usuário
            n_results (int): Número de resultados a buscar
            
        Returns:
            str: Contexto formatado para RAG
        """
        try:
            print(f"🔍 Buscando contexto relevante...")
            
            # Buscar notas similares
            results = self.indexer.search_similar_notes(query, n_results=n_results)
            
            if not results:
                return "Nenhuma nota relevante encontrada na sua base de conhecimento."
            
            # Formatar para RAG
            context = format_for_rag(results, max_tokens=1200)
            
            print(f"✅ Contexto encontrado: {len(results)} nota(s) relevante(s)")
            return context
            
        except Exception as e:
            print(f"❌ Erro na busca de contexto: {e}")
            return "Erro ao acessar base de conhecimento."
    
    def generate_response(self, query: str, context: str) -> str:
        """
        Gera resposta usando LLM com contexto RAG
        
        Args:
            query (str): Pergunta do usuário
            context (str): Contexto das notas relevantes
            
        Returns:
            str: Resposta gerada pelo LLM
        """
        try:
            # Construir prompt RAG
            prompt = self._build_rag_prompt(query, context)
            
            print("🤖 Gerando resposta com IA...")
            
            # Chamar OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente pessoal inteligente que responde perguntas baseado exclusivamente nas anotações pessoais do usuário. Seja preciso, útil e cite as informações relevantes das notas quando possível."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Salvar na conversa
            self.conversation_history.append({
                "query": query,
                "context_notes": len(context.split("--- NOTA")) - 1,
                "response": answer[:200] + "..." if len(answer) > 200 else answer
            })
            
            return answer
            
        except Exception as e:
            print(f"❌ Erro ao gerar resposta: {e}")
            return f"Desculpe, ocorreu um erro ao processar sua pergunta: {e}"
    
    def _build_rag_prompt(self, query: str, context: str) -> str:
        """
        Constrói prompt otimizado para RAG
        
        Args:
            query (str): Pergunta do usuário
            context (str): Contexto das notas
            
        Returns:
            str: Prompt formatado
        """
        prompt = f"""Você é um assistente que responde perguntas baseado exclusivamente nas anotações pessoais fornecidas abaixo.

INSTRUÇÕES:
- Use APENAS as informações do contexto fornecido
- Se a informação não estiver nas notas, diga claramente que não encontrou
- Cite as notas relevantes quando apropriado
- Seja conciso mas completo
- Use um tom amigável e pessoal

{context}

PERGUNTA DO USUÁRIO: {query}

RESPOSTA BASEADA NAS SUAS ANOTAÇÕES:"""

        return prompt
    
    def print_help(self):
        """Exibe ajuda do sistema"""
        print("\n📚 COMANDOS DISPONÍVEIS:")
        print("  /help, /h          - Exibir esta ajuda")
        print("  /stats, /s         - Estatísticas do sistema")
        print("  /history, /hist    - Mostrar histórico da conversa")
        print("  /clear, /c         - Limpar tela")
        print("  /reset             - Reiniciar conversa")
        print("  /quit, /q, exit    - Sair")
        print("\n💬 COMO USAR:")
        print("  Digite qualquer pergunta sobre suas anotações")
        print("  O sistema buscará automaticamente o contexto relevante")
        print("  Exemplos:")
        print("    - 'O que preciso fazer esta semana?'")
        print("    - 'Quais foram os pontos da reunião de ontem?'")
        print("    - 'Onde anotei sobre o projeto X?'")
        print("    - 'Resumo das minhas tarefas pendentes'")
        print()
    
    def print_stats(self):
        """Exibe estatísticas do sistema"""
        try:
            db_stats = self.indexer.get_collection_stats()
            
            print("\n📊 ESTATÍSTICAS DO SISTEMA RAG:")
            print(f"   📄 Notas indexadas: {db_stats.get('total_notes', 0)}")
            print(f"   💬 Perguntas nesta sessão: {len(self.conversation_history)}")
            print(f"   💾 Banco de dados: {self.indexer.persist_directory}")
            print(f"   🤖 Modelo LLM: GPT-4")
            print()
            
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
    
    def print_history(self):
        """Exibe histórico da conversa atual"""
        if not self.conversation_history:
            print("📭 Nenhuma conversa registrada nesta sessão")
            return
        
        print(f"\n📝 HISTÓRICO DA CONVERSA ({len(self.conversation_history)} perguntas):")
        for i, item in enumerate(self.conversation_history, 1):
            print(f"\n{i}. Pergunta: {item['query']}")
            print(f"   Notas consultadas: {item['context_notes']}")
            print(f"   Resposta: {item['response']}")
        print()
    
    def run_interactive(self):
        """Executa interface interativa"""
        print("🤖 CHAT RAG - Assistente Pessoal Baseado em suas Anotações")
        print("=" * 70)
        print("Faça perguntas sobre suas notas manuscritas indexadas!")
        print("Digite /help para ver comandos disponíveis")
        print("=" * 70)
        
        while True:
            try:
                # Prompt interativo
                user_input = input("\n💬 Você: ").strip()
                
                if not user_input:
                    continue
                
                # Comandos especiais
                if user_input.lower() in ['/quit', '/q', 'exit', 'quit']:
                    break
                elif user_input.lower() in ['/help', '/h']:
                    self.print_help()
                elif user_input.lower() in ['/stats', '/s']:
                    self.print_stats()
                elif user_input.lower() in ['/history', '/hist']:
                    self.print_history()
                elif user_input.lower() in ['/clear', '/c']:
                    print("\033[2J\033[H")  # Limpar tela
                elif user_input.lower() == '/reset':
                    self.conversation_history = []
                    print("🔄 Conversa reiniciada")
                else:
                    # Processar pergunta RAG
                    self.process_rag_query(user_input)
                
            except KeyboardInterrupt:
                print("\n👋 Saindo...")
                break
            except EOFError:
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        # Salvar histórico
        self.save_history()
        print("👋 Chat RAG encerrado")
    
    def process_rag_query(self, query: str):
        """
        Processa uma consulta RAG completa
        
        Args:
            query (str): Pergunta do usuário
        """
        try:
            # Buscar contexto
            context = self.search_context(query, n_results=5)
            
            # Gerar resposta
            response = self.generate_response(query, context)
            
            # Exibir resposta
            print(f"\n🤖 Assistente: {response}")
            
        except Exception as e:
            print(f"❌ Erro ao processar pergunta: {e}")
    
    def run_single_query(self, query: str):
        """
        Executa uma única consulta RAG (modo não-interativo)
        
        Args:
            query (str): Pergunta do usuário
        """
        print(f"💬 Pergunta: {query}")
        self.process_rag_query(query)


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Chat RAG - Assistente baseado em suas anotações",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python scripts/chat_rag.py                                    # Modo interativo
  python scripts/chat_rag.py "O que preciso fazer hoje?"        # Pergunta única
  python scripts/chat_rag.py --stats                            # Apenas estatísticas

O sistema busca automaticamente nas suas notas indexadas e gera respostas
contextualizadas usando GPT-4.
        """
    )
    
    parser.add_argument('query', nargs='?', help='Pergunta para o assistente')
    parser.add_argument('--stats', action='store_true', 
                       help='Exibir apenas estatísticas do sistema')
    
    args = parser.parse_args()
    
    # Inicializar sistema RAG
    try:
        chat_rag = ChatRAG()
    except Exception as e:
        print(f"❌ Falha na inicialização: {e}")
        sys.exit(1)
    
    # Executar baseado nos argumentos
    if args.stats:
        chat_rag.print_stats()
    elif args.query:
        chat_rag.run_single_query(args.query)
    else:
        chat_rag.run_interactive()


if __name__ == "__main__":
    main()
