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
        Inicializa o agente com o cliente da API e o modelo LLM.
        :param api_key: Chave de API para acessar a LLM.
        :param model: Modelo LLM a ser usado.
        """
        super().__init__(api_key=api_key, client=Groq, model=model)
        self.system_content = decision_agent_prompt
        self.messages = [{"role": "system", "content": self.system_content}]

    def decide_action(self, user_input, previous_inputs=None, previous_responses=None):
        """
        Processa a entrada do usuário e decide qual ação executar.
        :param user_input: Entrada atual do usuário
        :param previous_inputs: Lista das últimas entradas do usuário
        :param previous_responses: Lista das últimas respostas dos agentes (analysis/display)
        :return: Um dicionário contendo a ação e o texto associado
        """
        # Reset das mensagens para manter apenas o system prompt
        self.messages = [{"role": "system", "content": self.system_content}]
        
        # Adiciona o histórico à memória se existir
        if previous_inputs and previous_responses:
            for i in range(len(previous_inputs)):
                self.store_memory("user", previous_inputs[i])
                if i < len(previous_responses):
                    self.store_memory("assistant", previous_responses[i])
        
        # Adiciona a nova pergunta
        self.store_memory("user", user_input)
        
        print("\n📝 Memória atual:", self.messages)  # Debug da memória

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )

        system_response = response.choices[0].message.content.strip()
        print('Response:', system_response)

        try:
            decision = json.loads(system_response)
            
            if decision.get('action') == 'generic':
                cleaned_response = decision.get('response', system_response).replace("\n", "")
                # Guarda a própria resposta do DecisionAgent na memória
                self.store_memory("assistant", cleaned_response)
                return {
                    "action": "generic",
                    "response": cleaned_response
                }

            # Caso contrário, retorna a decisão como está
            self.store_memory("assistant", decision.get('response', system_response))
            print('Memória:', self.messages)
            return decision
            
        except json.JSONDecodeError:
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

