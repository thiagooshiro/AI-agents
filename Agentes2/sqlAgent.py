import os
from groq import Groq
import mysql.connector
from dotenv import load_dotenv
from baseAgent import BaseAgent 
from prompts.sqlAgentPrompt import sql_agent_prompt  

load_dotenv()

class SQLAgent(BaseAgent):
    def __init__(self, api_key, db_config, model="llama3-70b-8192"):
        """
        Inicializa o agente com o cliente da API e o modelo LLM, herdando funcionalidades da classe base.
        :param api_key: Chave de API para acessar a LLM.
        :param db_config: Dicionário contendo as configurações de conexão com o MySQL.
        :param model: Modelo LLM a ser usado.
        """
        # Inicializa a classe base
        super().__init__(api_key=api_key, client=Groq, model=model)

        self.system_content = sql_agent_prompt
        self.db_config = db_config

        # Inicializa as mensagens com uma mensagem do tipo 'system'
        self.messages = [{"role": "system", "content": self.system_content}]

    def initialize_client(self):
        """
        Envia o prompt de configuração como primeira mensagem para garantir que o modelo comece configurado.
        """
        # Envia a primeira solicitação com o prompt de configuração
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )

        # Obtém a resposta do sistema e armazena como memória inicial
        system_response = response.choices[0].message.content.strip()

        # Verifica se a resposta do sistema é uma string válida
        if isinstance(system_response, str):
            print('Initial Response:', system_response)
            self.store_memory("assistant", system_response)  # Memorizando a resposta inicial do assistente
        else:
            print("Erro: resposta do sistema não é uma string válida.")

    def generate_sql(self, user_input):
        """
        Converte a entrada do usuário em uma consulta SQL.
        :param user_input: Entrada do usuário em linguagem natural.
        :return: Consulta SQL gerada pelo modelo.
        """
        # Armazena a entrada do usuário no histórico
        self.store_memory("user", user_input)

        # Cria a mensagem do usuário
        self.messages.append({"role": "user", "content": str(user_input)})

        # Envia a solicitação para gerar a consulta SQL
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )

        # Obtém a resposta do assistente (deve ser uma string)
        assistant_response = response.choices[0].message.content.strip()

        # Verifica se a resposta do assistente é uma string válida
        if isinstance(assistant_response, str):
            print("Consulta gerada:", assistant_response)
        else:
            assistant_response = "Erro: resposta do assistente não é uma string válida."
            print(assistant_response)

        # Armazena a resposta do assistente na memória
        self.store_memory("assistant", assistant_response)

        return assistant_response

    def execute_query(self, sql_query):
        """
        Executa a consulta SQL no banco de dados MySQL.
        :param sql_query: A consulta SQL gerada pelo modelo.
        :return: Resultados da consulta.
        """
        # Se for mensagem de erro, retorna sem executar query
        if sql_query == "ERROR: invalid input":
            return {sql_query}
        
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql_query)
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            return results
        except mysql.connector.Error as err:
            return {"error": f"Erro ao executar a consulta: {err}"}

    def decide_action(self, user_input):
        """
        Processa a entrada do usuário e decide qual ação executar, considerando as interações anteriores.
        :param user_input: Entrada do usuário.
        :return: Dicionário com a ação e a resposta.
        """
        # Gera a consulta SQL com base na entrada do usuário
        sql_query = self.generate_sql(user_input)
        print("Consulta gerada:", sql_query)

        # Executa a consulta no banco de dados
        query_results = self.execute_query(sql_query)
        
        # Verifica se há erro na resposta
        if isinstance(query_results, dict) and 'error' in query_results:
            response = query_results['error']  # Se for erro, não salva na memória
        else:
            response = query_results  # Caso contrário, usa os resultados da consulta
            self.store_memory("assistant", str(response))  # Garante que será salvo como string, se não for erro

        return {
            "action": "query_result",
            "response": query_results
        }

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
    
    # Inicializa o agente com o prompt de configuração
    agent.initialize_client()

    while True:
        user_input = input("Você: ")
        decision = agent.decide_action(user_input)
        print("Ação:", decision["action"])
        print("Resposta:", decision["response"])
