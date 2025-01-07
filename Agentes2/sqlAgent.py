import os
import sqlite3
from groq import Groq
from dotenv import load_dotenv
from baseAgent import BaseAgent  # Assumindo que você já tem uma classe BaseAgent
from prompts.sqlAgentPrompt import sql_agent_prompt  # Prompt configurado para SQL

load_dotenv()

class SQLAgent(BaseAgent):
    def __init__(self, api_key, db_path=":memory:", model="llama3-70b-8192"):
        """
        Inicializa o agente com o cliente da API e o modelo LLM, herdando funcionalidades da classe base.
        :param api_key: Chave de API para acessar a LLM.
        :param db_path: Caminho para o banco de dados. Usamos o SQLite em memória por padrão.
        :param model: Modelo LLM a ser usado.
        """
        super().__init__(api_key=api_key, client=Groq, model=model)

        self.system_content = sql_agent_prompt  # Prompt específico para SQL
        self.messages = []  # Inicialmente, sem mensagens
        self.db_path = db_path  # Caminho para o banco de dados
        self.initialize_client()  # Inicializa o agente com o prompt de configuração

    def initialize_client(self):
        """
        Envia o prompt de configuração como primeira mensagem para garantir que o modelo comece configurado.
        """
        self.messages = [{"role": "system", "content": self.system_content}]  # Só o prompt de configuração
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )

        system_response = response.choices[0].message.content.strip()
        print('Initial Response:', system_response)
        self.store_memory("assistant", system_response)  # Memoriza a resposta inicial

    def generate_sql(self, user_input):
        """
        Gera uma consulta SQL a partir da entrada do usuário.
        :param user_input: A consulta em linguagem natural do usuário.
        :return: A consulta SQL gerada pelo modelo.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": self.system_content},
                     {"role": "user", "content": user_input}]
        )
        sql_query = response.choices[0].message.content.strip()
        return sql_query

    def execute_sql_query(self, sql_query):
        """
        Executa a consulta SQL no banco de dados fornecido e retorna os resultados.
        :param sql_query: A consulta SQL gerada.
        :return: O resultado da consulta ou uma mensagem de erro.
        """
        try:
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()
            cursor.execute(sql_query)
            result = cursor.fetchall()
            connection.close()
            return result
        except sqlite3.Error as e:
            return f"Erro ao executar a consulta: {str(e)}"

    def decide_action(self, user_input):
        """
        Processa a entrada do usuário, gera a consulta SQL e executa a consulta no banco de dados.
        :param user_input: Entrada do usuário.
        :return: Dicionário com a ação e os resultados.
        """
        self.store_memory("user", user_input)  # Armazena a interação do usuário

        # Gera a consulta SQL a partir do input do usuário
        sql_query = self.generate_sql(user_input)

        # Executa a consulta SQL
        results = self.execute_sql_query(sql_query)

        # Armazena a resposta na memória
        self.store_memory("assistant", results)

        # Retorna os resultados ou uma mensagem de erro
        return {
            "action": "sql_query",
            "sql_query": sql_query,
            "results": results
        }

# Exemplo de uso
if __name__ == "__main__":
    # Inicializa o agente
    agent = SQLAgent(api_key=os.environ.get('GROQ_API_KEY'))

    # Loop contínuo para testar a memória e geração de SQL
    while True:
        # Entrada do usuário
        user_input = input("Você: ")

        # Decide a ação
        decision = agent.decide_action(user_input)
        print('Decisão:', decision)

        # Exibe a consulta SQL e os resultados
        print(f"Consulta SQL: {decision.get('sql_query')}")
        print(f"Resultados: {decision.get('results')}")
