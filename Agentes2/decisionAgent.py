import os
import json
from groq import Groq
from dotenv import load_dotenv
from baseAgent import BaseAgent
from prompts.decisionAgentPrompt import decision_agent_prompt

load_dotenv()


class DecisionAgent(BaseAgent):
    def __init__(self, api_key, model="llama3-70b-8192"):
        """
        Inicializa o agente com o cliente da API e o modelo LLM, herdando funcionalidades da classe base.
        :param api_key: Chave de API para acessar a LLM.
        :param model: Modelo LLM a ser usado.
        """
        # Inicializa a classe base
        super().__init__(api_key=api_key, client=Groq, model=model)

        self.system_content = decision_agent_prompt
        self.messages = [{"role": "system", "content": self.system_content}]

    def decide_action(self, user_input):
        """
        Processa a entrada do usuário e decide qual ação executar, considerando as interações anteriores.
        :param user_input: Entrada do usuário.
        :return: Um dicionário contendo a ação e o texto associado.
        """

        # Prepara o histórico de mensagens, incluindo a entrada do usuário
        self.store_memory("user", user_input)

        # Envia a solicitação para o modelo
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )

        # Obtém o conteúdo gerado pelo sistema
        system_response = response.choices[0].message.content.strip()
        print('Response:', system_response)

        try:
            # Tenta carregar a resposta como JSON
            decision = json.loads(system_response)
            print('Memory', self.messages)
            # Se for "generic", limpa e guarda a interação simplificada
            if decision.get('action') == 'generic':
                cleaned_response = system_response.replace("\n", "")
                self.store_memory("assistant", decision.get('response'))  # Memoriza apenas a resposta textual
                return {
                    "action": "generic",
                    "response": system_response
                }

            return decision

        except json.JSONDecodeError:
            # Erro ao tentar parsear a resposta como JSON
            return {
                "action": "error",
                "input": user_input,
                "error": f"Failed to parse response as JSON. Raw response: {system_response}"
            }

# Exemplo de uso em um loop contínuo
if __name__ == "__main__":
    # Inicializa o agente
    agent = DecisionAgent(api_key=os.environ.get('GROQ_API_KEY'))

    # Loop contínuo para testar a memória
    while True:
        # Entrada do usuário
        user_input = input("Você: ")

        # Decide a ação
        decision = agent.decide_action(user_input)
        print('Decision', decision)

        # Exibe o resultado
        print(f"Ação: {decision.get('action')}")
        print(f"Entrada: {decision.get('user_query')}")
        print(f"Resposta: {decision.get('response')}")
