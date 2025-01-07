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

        self.system_content = decision_agent_prompt  # Prompt de configuração
        self.messages = []  # Inicialmente, sem mensagens
        self.initialize_client()  # Chama a inicialização para enviar o prompt de configuração

    def initialize_client(self):
        """
        Envia o prompt de configuração como primeira mensagem para garantir que o modelo comece configurado.
        """
        self.messages = [{"role": "system", "content": self.system_content}]  # Só o prompt de configuração

        # Envia a primeira solicitação com o prompt de configuração
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )

        # Obtém a resposta do sistema e a armazena como memória inicial
        system_response = response.choices[0].message.content.strip()
        print('Initial Response:', system_response)  # Verifica a resposta inicial

        self.store_memory("assistant", system_response)  # Memoriza a resposta inicial do assistente

    def decide_action(self, user_input):
        """
        Processa a entrada do usuário e decide qual ação executar, considerando as interações anteriores.
        :param user_input: Entrada do usuário.
        :return: Um dicionário contendo a ação e o texto associado.
        """
        # Adiciona a interação do usuário ao histórico
        self.store_memory("user", user_input)

        # Envia a solicitação para o modelo com o histórico de mensagens
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )

        # Obtém a resposta do sistema
        system_response = response.choices[0].message.content.strip()
        print('Response:', system_response)

        # Armazena a resposta do sistema na memória
        self.store_memory("assistant", system_response)

        # Tenta interpretar a resposta como JSON
        try:
            decision = json.loads(system_response)

            # Se a ação for "generic", limpa e guarda a interação simplificada
            if decision.get('action') == 'generic':
                cleaned_response = system_response.replace("\n", "")
                self.store_memory("assistant", cleaned_response)  # Memoriza apenas a resposta textual
                return {
                    "action": "generic",
                    "response": system_response
                }

            # Caso contrário, retorna a decisão como está
            self.store_memory("assistant", decision.get('response', system_response))
            return decision

        except json.JSONDecodeError:
            # Falha ao tentar transformar a resposta da string em JSON
            return {
                "action": "error",
                "input": user_input,
                "error": f"Failed to parse response as JSON. Raw response: {system_response}"
            }


if __name__ == "__main__":
    # Inicializa o agente
    agent = DecisionAgent(api_key=os.environ.get('GROQ_API_KEY'))

    # Agora que a inicialização foi feita, o agente já está configurado com o prompt
    # Exemplo de loop contínuo para interações subsequentes
    while True:
        # Entrada do usuário
        user_input = input("Você: ")

        # Verifica se é a primeira interação, ou se já foi configurado
        if not agent.messages:  # Se o histórico está vazio, significa que a configuração ainda não foi feita
            print("Inicializando o agente com a configuração...")
            agent.initialize_client()  # Chama a função de inicialização para enviar o prompt de configuração

        # Decide a ação com base na entrada do usuário
        decision = agent.decide_action(user_input)

        # Exibe o resultado
        print(f"Ação: {decision.get('action')}")
        print(f"Resposta: {decision.get('response')}")

