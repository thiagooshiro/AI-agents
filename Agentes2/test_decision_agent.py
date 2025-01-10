import os
from dotenv import load_dotenv
from decisionAgent import DecisionAgent
from sqlAgent import SQLAgent
from analysisAgent import AnalysisAgent
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
    
    # Inicializa todos os agentes
    decision_agent = DecisionAgent(api_key=os.environ.get('GROQ_API_KEY'))
    sql_agent = SQLAgent(api_key=os.environ.get('GROQ_API_KEY'), db_config=db_config)
    analysis_agent = AnalysisAgent(api_key=os.environ.get('GROQ_API_KEY'))
    display_agent = DisplayAgent(api_key=os.environ.get('GROQ_API_KEY'))
    
    # Histórico de interações
    previous_inputs = []      # Guarda perguntas do usuário
    previous_responses = []   # Guarda respostas dos agentes
    
    print("\n🤖 Testando DecisionAgent... (Digite 'sair' para encerrar)")
    
    while True:
        user_input = input("\n👤 Você: ")
        
        if user_input.lower() == 'sair':
            print("👋 Encerrando...")
            break
        
        # Pega as últimas 2 interações do histórico
        last_inputs = previous_inputs[-2:] if previous_inputs else None
        last_responses = previous_responses[-2:] if previous_responses else None
        
        # Decide ação com base no histórico
        decision = decision_agent.decide_action(
            user_input,
            last_inputs,
            last_responses
        )
        print(f"\n🤔 Ação decidida: {decision['action']}")
        
        # Executa a ação decidida
        if decision['action'] == 'analysis':
            # Primeiro executa a query
            sql_result = sql_agent.process_request(user_input)
            if sql_result['action'] == 'error':
                print("\n❌ Erro SQL:", sql_result['response'])
                continue
            
            # Depois faz a análise
            analysis = analysis_agent.generate_analysis(
                user_input,
                sql_result['response'],
                sql_result['original_query']
            )
            print("\n📊 Análise:", analysis['response'])
            
            # Guarda a resposta no histórico
            previous_responses.append(analysis['response'])
            
        elif decision['action'] == 'display':
            # Executa a query
            sql_result = sql_agent.process_request(user_input)
            if sql_result['action'] == 'error':
                print("\n❌ Erro SQL:", sql_result['response'])
                continue
            
            # Formata a exibição
            display = display_agent.display_results(
                sql_result['response'],
                sql_result['original_query'],
                user_input
            )
            print("\n📈 Resultados:", display)
            
            # Guarda a resposta no histórico
            previous_responses.append(display)
            
        elif decision['action'] == 'generic':
            print("\n💬 Resposta:", decision['response'])
            # Guarda a resposta do DecisionAgent no histórico
            previous_responses.append(decision['response'])
        
        # Guarda a pergunta no histórico
        previous_inputs.append(user_input)

if __name__ == "__main__":
    main() 