import os
from groq import Groq
import mysql.connector
from dotenv import load_dotenv
from baseAgent import BaseAgent  # Assumindo que você já tem uma classe BaseAgent
from prompts.sqlAgentPrompt import sql_agent_prompt  # Prompt configurado para SQL

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
        self.messages = [{"role": "system", "content": self.system_content}]

    def generate_sql(self, user_input):
        """
        Converte a entrada do usuário em uma consulta SQL.
        :param user_input: Entrada do usuário em linguagem natural.
        :return: Consulta SQL gerada pelo modelo.
        """
        # Prepara o histórico de mensagens
        self.store_memory("user", user_input)
        self.messages.append({"role": "user", "content": user_input})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )

        # Extrai a consulta SQL gerada
        sql_query = response.choices[0].message.content.strip()
        return sql_query

    def execute_query(self, sql_query):
        """
        Executa a consulta SQL no banco de dados MySQL.
        :param sql_query: A consulta SQL gerada pelo modelo.
        :return: Resultados da consulta.
        """
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
        sql_query = self.generate_sql(user_input)
        print("Consulta gerada:", sql_query)

        # Executa a consulta no banco de dados
        query_results = self.execute_query(sql_query)
        
        # Armazena a resposta do assistente e retorna os resultados
        self.store_memory("assistant", query_results)
        
        return {
            "action": "query_result",
            "response": query_results
        }

# Exemplo de uso em um loop contínuo
if __name__ == "__main__":
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'sua_senha',
        'database': 'nome_do_banco'
    }
    
    agent = SQLAgent(api_key=os.environ.get('GROQ_API_KEY'), db_config=db_config)

    while True:
        user_input = input("Você: ")
        decision = agent.decide_action(user_input)
        print("Ação:", decision["action"])
        print("Resposta:", decision["response"])
