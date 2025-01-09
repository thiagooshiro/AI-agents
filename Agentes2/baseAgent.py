class BaseAgent:
    base_prompt = "Você é um assistente de IA. Aguarde configurações específicas para sua função."

    def __init__(self, api_key, client, model="llama3-70b-8192", system_content=None):
        """
        Inicializa a estrutura base de um agente, com memória, cliente de API e prompt inicial.
        :param api_key: Chave da API para acessar o modelo LLM.
        :param client: Cliente de API a ser utilizado (exemplo: Groq, OpenAI).
        :param model: Modelo do LLM a ser usado.
        :param system_content: Conteúdo inicial do prompt do sistema.
        """
        self.messages = [{"role": "system", "content": system_content or self.base_prompt}]  # Histórico de mensagens
        self.client = client(api_key=api_key)  # Cliente da API
        self.model = model  # Modelo do LLM

    def store_memory(self, role, content):
        """
        Armazena uma interação na memória do agente.
        Mantém apenas o system prompt + 4 mensagens (2 pares de pergunta/resposta)
        """
        self.messages.append({"role": role, "content": content})
        
        # Se passar de 5 mensagens (system + 2 pares), remove o par mais antigo
        while len(self.messages) > 5:  # Troca if por while para garantir
            self.messages.pop(1)  # Sempre remove a partir do índice 1

   
