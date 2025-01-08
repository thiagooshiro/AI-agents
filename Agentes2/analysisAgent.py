from groq import Groq
from baseAgent import BaseAgent
from prompts.analysisAgentPrompt import analysis_agent_prompt

class AnalysisAgent(BaseAgent):
    def __init__(self, api_key, model="llama3-70b-8192"):
        super().__init__(api_key=api_key, client=Groq, model=model)
        self.system_content = analysis_agent_prompt
        self.messages = [{"role": "system", "content": self.system_content}]

    def analyze_results(self, query_results, original_query, user_question):
        """
        Analisa os resultados da query e gera insights.
        :param query_results: Resultados formatados da query
        :param original_query: Query SQL original
        :param user_question: Pergunta original do usuário
        :return: Análise com insights
        """
        context = {
            "user_question": user_question,
            "sql_query": original_query,
            "query_results": query_results
        }
        
        analysis_prompt = f"""
        Contexto da análise:
        - Pergunta original do usuário: {context['user_question']}
        - Query SQL executada: {context['sql_query']}
        - Resultados obtidos: {context['query_results']}

        Por favor, analise estes dados e forneça insights relevantes.
        """

        self.store_memory("user", analysis_prompt)
        self.messages.append({"role": "user", "content": analysis_prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )

        analysis = response.choices[0].message.content.strip()
        self.store_memory("assistant", analysis)

        return {
            "action": "analysis",
            "response": analysis
        } 