import os
from dotenv import load_dotenv
from sqlAgent import SQLAgent
from analysisAgent import AnalysisAgent

load_dotenv()

def main():
    # Configurações do banco de dados
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD'),  
        'database': os.getenv('DB_NAME', 'teste_idfy'),
        'port': os.getenv('DB_PORT', 3306)
    }
    
    # Inicializa os agentes
    sql_agent = SQLAgent(api_key=os.environ.get('GROQ_API_KEY'), db_config=db_config)
    analysis_agent = AnalysisAgent(api_key=os.environ.get('GROQ_API_KEY'))
    
    # Inicializa ambos os agentes com seus prompts de configuração
    print("\n🔄 Inicializando SQL Agent...")
    sql_agent.initialize_client()
    
    print("\n🔄 Inicializando Analysis Agent...")
    analysis_agent.initialize_client()

    print("\n🤖 Assistentes iniciados! (Digite 'sair' para encerrar)")
    
    while True:
        user_input = input("\n👤 Você: ")
        
        if user_input.lower() == 'sair':
            print("👋 Encerrando o assistente...")
            break
            
        try:
            # Primeiro, obtém os resultados da query via SQL Agent
            sql_results = sql_agent.decide_action(user_input)
            
            print("\n📊 Resultados SQL obtidos:")
            print(f"Query executada: {sql_results['original_query']}")
            
            # Se houver erro na query, mostra o erro e continua o loop
            if isinstance(sql_results['response'], dict) and 'error' in sql_results['response']:
                print(f"❌ Erro: {sql_results['response']['error']}")
                continue
            
            # Se tiver resultados válidos, passa para análise
            print("\n🔍 Analisando resultados...")
            analysis = analysis_agent.analyze_results(
                query_results=sql_results['response'],
                original_query=sql_results['original_query'],
                user_question=user_input
            )
            
            print("\n💡 Análise:")
            print(analysis['response'])
            
        except Exception as e:
            print(f"\n❌ Erro inesperado: {str(e)}")

if __name__ == "__main__":
    main() 