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
        Armazena uma interação na memória do agente e no histórico de mensagens.
        :param role: O papel da interação, pode ser 'user' ou 'assistant'.
        :param content: O conteúdo da interação.
        """
        # Adiciona a nova interação no histórico de mensagens
        self.messages.append({"role": role, "content": content})

        # Limita a memória para as últimas 5 interações
        if len(self.messages) > 7:  # Contando com o system prompt, o limite será 7 (5 interações + prompt)
            self.messages.pop(1)  # Remove a interação mais antiga, preservando o system prompt

   
