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
    
    print("\n🤖 Assistentes iniciados! (Digite 'sair' para encerrar)")
    
    while True:
        user_input = input("\n👤 Você: ")
        
        if user_input.lower() == 'sair':
            print("👋 Encerrando o assistente...")
            break
        
        # Processa a requisição SQL completa
        sql_result = sql_agent.process_request(user_input)
        print("\n📊 Query executada:", sql_result['original_query'])
        
        if sql_result['action'] == 'error':
            print("\n❌ Erro:", sql_result['response'])
            continue
            
        # Gera a análise dos resultados
        analysis = analysis_agent.generate_analysis(
            user_input,
            sql_result['response'],
            sql_result['original_query']
        )
        
        print("\n💡 Análise:", analysis['response'])

if __name__ == "__main__":
    main() 