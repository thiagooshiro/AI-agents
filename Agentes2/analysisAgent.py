import os
from groq import Groq
from dotenv import load_dotenv
from prompts.analysisAgentPrompt import analysis_agent_prompt

load_dotenv()

class AnalysisAgent:
    def __init__(self, api_key, model="llama3-70b-8192"):
        """
        Inicializa o agente com o cliente da API e o modelo LLM.
        :param api_key: Chave de API para acessar a LLM.
        :param model: Modelo LLM a ser usado.
        """
        self.client = Groq(api_key=api_key)
        self.model = model
        self.system_content = analysis_agent_prompt
        self.messages = [{"role": "system", "content": self.system_content}]

    def generate_analysis(self, user_input, query_results, original_query):
        """
        Gera a análise com base na entrada do usuário e resultados da query.
        :param user_input: Entrada do usuário em linguagem natural
        :param query_results: Resultados da query SQL
        :param original_query: Query SQL original
        :return: Análise gerada pelo modelo
        """
        # Reset das mensagens para manter apenas o system prompt
        self.messages = [{"role": "system", "content": self.system_content}]
        
        # Cria o contexto
        context = {
            "user_question": user_input,
            "sql_query": original_query,
            "query_results": query_results
        }
        
        # Cria a mensagem do usuário
        message_content = f"""
        Contexto da análise:
        - Pergunta original do usuário: {context['user_question']}
        - Query SQL executada: {context['sql_query']}
        - Resultados obtidos: {context['query_results']}
        """
        self.messages.append({"role": "user", "content": message_content})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )

        return {
            "action": "analysis",
            "response": response.choices[0].message.content.strip()
        }
