#!/usr/bin/env python3
"""
Query Interface - Interface CLI para busca semântica no ChromaDB

Este script fornece uma interface de linha de comando para realizar consultas 
semânticas no banco de dados ChromaDB onde estão indexadas as notas manuscritas.

Permite buscar notas por significado usando linguagem natural.

Autor: Thiago Macedo
Data: 29/05/2025
Versão: 1.0.0
"""

import sys
import json
import readline
from pathlib import Path
from typing import List, Dict, Any, Optional

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

# Importar módulos necessários
try:
    from src.chroma_indexer import ChromaIndexer
    from src.ocr_extractor import load_keep_credentials
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("Certifique-se de que está executando do diretório raiz do projeto")
    sys.exit(1)


class QueryInterface:
    """Interface para consultas semânticas no ChromaDB"""
    
    def __init__(self):
        """Inicializa a interface de consulta"""
        self.setup_indexer()
        self.setup_history()
    
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
            if stats.get('count', 0) == 0:
                print("⚠️ Aviso: Nenhuma nota indexada encontrada no ChromaDB")
                print("Execute o pipeline principal primeiro para indexar suas notas")
            else:
                print(f"✅ ChromaDB carregado: {stats.get('count', 0)} notas indexadas")
                
        except Exception as e:
            print(f"❌ Erro ao configurar ChromaDB: {e}")
            sys.exit(1)
    
    def setup_history(self):
        """Configura histórico de comandos"""
        self.history_file = ROOT_DIR / '.query_history'
        
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
    
    def print_help(self):
        """Exibe ajuda do sistema"""
        print("\n📚 COMANDOS DISPONÍVEIS:")
        print("  /help, /h          - Exibir esta ajuda")
        print("  /stats, /s         - Estatísticas do banco")
        print("  /recent, /r        - Mostrar notas recentes")
        print("  /list, /l          - Listar todas as notas")
        print("  /clear, /c         - Limpar tela")
        print("  /quit, /q, exit    - Sair")
        print("\n🔍 BUSCA SEMÂNTICA:")
        print("  Digite qualquer pergunta ou termo em linguagem natural")
        print("  Exemplos:")
        print("    - 'tarefas pendentes'")
        print("    - 'problemas de trabalho'")
        print("    - 'lembretes importantes'")
        print("    - 'reuniões da semana'")
        print()
    
    def format_result(self, result: Dict[str, Any], index: int) -> str:
        """Formata um resultado de busca para exibição"""
        metadata = result.get('metadata', {})
        similarity = result.get('similarity', 0.0)
        
        title = metadata.get('title', 'Sem título')
        summary = metadata.get('summary', 'Sem resumo')
        date = metadata.get('data', 'Sem data')
        keywords = metadata.get('keywords', [])
        
        # Formatar keywords
        keywords_str = ', '.join(keywords) if keywords else 'Nenhuma'
        
        # Criar resultado formatado
        result_text = f"""
📝 {index}. {title}
   📅 Data: {date}
   📊 Similaridade: {similarity:.3f}
   📝 Resumo: {summary}
   🏷️ Tags: {keywords_str}
"""
        return result_text
    
    def search_notes(self, query: str, n_results: int = 5) -> List[Dict]:
        """Executa busca semântica"""
        try:
            print(f"🔍 Buscando: '{query}'...")
            results = self.indexer.search_similar_notes(query, n_results=n_results)
            return results or []
        except Exception as e:
            print(f"❌ Erro na busca: {e}")
            return []
    
    def show_stats(self):
        """Exibe estatísticas do banco"""
        try:
            stats = self.indexer.get_collection_stats()
            print("\n📊 ESTATÍSTICAS DO CHROMADB:")
            print(f"   📄 Total de notas: {stats.get('count', 0)}")
            print(f"   🧠 Embeddings: {stats.get('count', 0)} vetores")
            print(f"   💾 Banco: {self.indexer.persist_directory}")
            print()
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
    
    def show_recent_notes(self, limit: int = 10):
        """Mostra notas recentes (baseado nos metadados disponíveis)"""
        try:
            # Buscar por termo genérico para obter algumas notas
            results = self.indexer.search_similar_notes("nota", n_results=limit)
            
            if not results:
                print("📭 Nenhuma nota encontrada")
                return
            
            print(f"\n📋 NOTAS RECENTES (últimas {len(results)}):")
            for i, result in enumerate(results, 1):
                metadata = result.get('metadata', {})
                title = metadata.get('title', 'Sem título')
                date = metadata.get('data', 'Sem data')
                print(f"   {i}. {title} ({date})")
            print()
            
        except Exception as e:
            print(f"❌ Erro ao buscar notas recentes: {e}")
    
    def list_all_notes(self):
        """Lista todas as notas disponíveis"""
        try:
            # Buscar com termo muito genérico para pegar todas
            results = self.indexer.search_similar_notes("", n_results=100)
            
            if not results:
                print("📭 Nenhuma nota encontrada")
                return
            
            print(f"\n📋 TODAS AS NOTAS ({len(results)} encontradas):")
            for i, result in enumerate(results, 1):
                metadata = result.get('metadata', {})
                title = metadata.get('title', 'Sem título')
                date = metadata.get('data', 'Sem data')
                summary = metadata.get('summary', '')
                
                # Limitar tamanho do resumo
                if len(summary) > 50:
                    summary = summary[:47] + "..."
                
                print(f"   {i:2d}. {title:<25} | {date:<12} | {summary}")
            print()
            
        except Exception as e:
            print(f"❌ Erro ao listar notas: {e}")
    
    def run_interactive(self):
        """Executa interface interativa"""
        print("🔍 QUERY INTERFACE - Busca Semântica no ChromaDB")
        print("=" * 60)
        print("Digite sua consulta em linguagem natural ou /help para ajuda")
        print("=" * 60)
        
        while True:
            try:
                # Prompt interativo
                user_input = input("\n🔎 Consulta: ").strip()
                
                if not user_input:
                    continue
                
                # Comandos especiais
                if user_input.lower() in ['/quit', '/q', 'exit', 'quit']:
                    break
                elif user_input.lower() in ['/help', '/h']:
                    self.print_help()
                elif user_input.lower() in ['/stats', '/s']:
                    self.show_stats()
                elif user_input.lower() in ['/recent', '/r']:
                    self.show_recent_notes()
                elif user_input.lower() in ['/list', '/l']:
                    self.list_all_notes()
                elif user_input.lower() in ['/clear', '/c']:
                    print("\033[2J\033[H")  # Limpar tela
                else:
                    # Busca semântica
                    results = self.search_notes(user_input)
                    
                    if results:
                        print(f"\n✅ {len(results)} resultado(s) encontrado(s):")
                        for i, result in enumerate(results, 1):
                            print(self.format_result(result, i))
                    else:
                        print("❌ Nenhum resultado encontrado")
                        print("💡 Tente termos diferentes ou consulte /help")
                
            except KeyboardInterrupt:
                print("\n👋 Saindo...")
                break
            except EOFError:
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        # Salvar histórico
        self.save_history()
        print("👋 Interface de consulta encerrada")
    
    def run_single_query(self, query: str, n_results: int = 5):
        """Executa uma única consulta (modo não-interativo)"""
        results = self.search_notes(query, n_results)
        
        if results:
            print(f"✅ {len(results)} resultado(s) encontrado(s) para '{query}':")
            for i, result in enumerate(results, 1):
                print(self.format_result(result, i))
        else:
            print(f"❌ Nenhum resultado encontrado para '{query}'")
        
        return results


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Interface de consulta semântica para ChromaDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python scripts/query_interface.py                           # Modo interativo
  python scripts/query_interface.py "tarefas pendentes"       # Consulta única
  python scripts/query_interface.py --stats                   # Apenas estatísticas
  python scripts/query_interface.py --list                    # Listar todas as notas
        """
    )
    
    parser.add_argument('query', nargs='?', help='Consulta para busca semântica')
    parser.add_argument('-n', '--results', type=int, default=5, 
                       help='Número máximo de resultados (padrão: 5)')
    parser.add_argument('--stats', action='store_true', 
                       help='Exibir apenas estatísticas do banco')
    parser.add_argument('--list', action='store_true', 
                       help='Listar todas as notas disponíveis')
    parser.add_argument('--recent', action='store_true', 
                       help='Mostrar notas recentes')
    
    args = parser.parse_args()
    
    # Inicializar interface
    try:
        interface = QueryInterface()
    except Exception as e:
        print(f"❌ Falha na inicialização: {e}")
        sys.exit(1)
    
    # Executar baseado nos argumentos
    if args.stats:
        interface.show_stats()
    elif args.list:
        interface.list_all_notes()
    elif args.recent:
        interface.show_recent_notes()
    elif args.query:
        interface.run_single_query(args.query, args.results)
    else:
        interface.run_interactive()


if __name__ == "__main__":
    main()
