import os
from dotenv import load_dotenv
from sqlAgent import SQLAgent
from displayAgent import DisplayAgent

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
    display_agent = DisplayAgent(api_key=os.environ.get('GROQ_API_KEY'))
    
    print("\n🔄 Inicializando SQL Agent...")

    print("\n🤖 Assistente iniciado! (Digite 'sair' para encerrar)")
    
    while True:
        user_input = input("\n👤 Você: ")
        
        if user_input.lower() == 'sair':
            print("👋 Encerrando o assistente...")
            break
            
        try:
            # Obtém os resultados da query via SQL Agent
            query = sql_agent.decide_action(user_input)  # query agora é uma string
            print("\n📊 Query executada:")
            print(f"{query}")  # Exibe a query gerada
            
            # Se houver erro na query, mostra o erro e continua o loop
            if isinstance(query, str) and query.startswith("Erro ao gerar query:"):
                print(f"❌ {query}")
                continue
            
            # Executa a query e obtém os resultados
            sql_results = sql_agent.execute_query(query)
            
            # Se houver erro na execução da query, mostra o erro e continua o loop
            if isinstance(sql_results, dict) and 'error' in sql_results:
                print(f"❌ Erro: {sql_results['error']}")
                continue
            
            # Se tiver resultados válidos, passa para o Display Agent
            print("\n📋 Formatando resultados...")
            display = display_agent.display_results(
                query_results=sql_results,
                original_query=query,
                user_question=user_input
            )
            
            print("\n📈 Resultado:")
            print(display)
            
        except Exception as e:
            print(f"\n❌ Erro inesperado: {str(e)}")

if __name__ == "__main__":
    main() 