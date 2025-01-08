from groq import Groq
from baseAgent import BaseAgent
from prompts.displayAgentPrompt import display_agent_prompt

class DisplayAgent(BaseAgent):
    def __init__(self, api_key, model="llama3-70b-8192"):
        super().__init__(api_key=api_key, client=Groq, model=model)
        self.system_content = display_agent_prompt
        self.messages = [{"role": "system", "content": self.system_content}]
    
    def initialize_client(self):
        """
        Inicializa o agente com o prompt do sistema.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )

        system_response = response.choices[0].message.content.strip()

        if isinstance(system_response, str):
            print('Display Agent Initialized:', system_response)
            self.store_memory("assistant", system_response)
        else:
            print("Erro: resposta do sistema não é uma string válida.")
    
    def display_results(self, query_results, original_query, user_question):
        """
        Processa e exibe os resultados da análise de forma amigável.
        
        Args:
            query_results: Resultados da consulta SQL
            original_query: Query SQL original executada
            user_question: Pergunta original do usuário
        """
        # Prepara a mensagem para o LLM
        message = f"""
        Resultados da consulta: {query_results}
        Query original: {original_query}
        Pergunta do usuário: {user_question}
        """
        
        # Adiciona a mensagem do usuário ao histórico
        self.messages.append({"role": "user", "content": message})
        
        # Obtém a resposta do LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )
        
        # Extrai e retorna o conteúdo da resposta
        display_text = response.choices[0].message.content
        
        # Adiciona a resposta ao histórico
        self.messages.append({"role": "assistant", "content": display_text})
        
        return display_text