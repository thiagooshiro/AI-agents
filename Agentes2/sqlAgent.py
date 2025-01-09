import os
from groq import Groq
import mysql.connector
from dotenv import load_dotenv
from prompts.sqlAgentPrompt import sql_agent_prompt  

load_dotenv()

class SQLAgent:
    def __init__(self, api_key, db_config, model="llama3-70b-8192"):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.system_content = sql_agent_prompt
        self.db_config = db_config
    
    def decide_action(self, user_input):
        """Processa a entrada do usuário e obtém a query SQL"""
        messages = [
            {"role": "system", "content": self.system_content},
            {"role": "user", "content": user_input}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Erro ao gerar query: {str(e)}"
    
    def execute_query(self, query):
        """Executa a query SQL e retorna os resultados"""
        print('Query: ', query)
        try:
            with mysql.connector.connect(**self.db_config) as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query)
                return cursor.fetchall()
                
        except Exception as e:
            return {"error": str(e)}
    
    def format_response(self, query, results):
        """Formata a resposta final com query e resultados"""
        return {
            "action": "sql_query" if not isinstance(results, dict) or "error" not in results else "error",
            "original_query": query,
            "response": results
        }
    
    def process_request(self, user_input):
        """Método principal que coordena o fluxo completo"""
        query = self.decide_action(user_input)
        results = self.execute_query(query)
        return self.format_response(query, results)

# Exemplo de uso em um loop contínuo
if __name__ == "__main__":
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD'),  
        'database': os.getenv('DB_NAME', 'teste_idfy'),
        'port': os.getenv('DB_PORT', 3306)
    }
    
    agent = SQLAgent(api_key=os.environ.get('GROQ_API_KEY'), db_config=db_config)
    
    while True:
        user_input = input("Você: ")
        decision = agent.process_request(user_input)
        print("Ação:", decision["action"])
        print("Resposta:", decision["response"])
