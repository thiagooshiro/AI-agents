class BaseAgent:
    base_prompt = "Você é um assistente de IA. Aguarde configurações específicas para sua função."

    def __init__(self, api_key, client, model="llama3-70b-8192", system_content=None):
        """
        Inicializa a estrutura base de um agente, com memória, cliente de API e prompt inicial.
        :param api_key: Chave da API para acessar o modelo LLM.
        :param client: Cliente de API a ser utilizado (exemplo: Groq, OpenAI).
        :param model: Modelo LLM a ser usado.
        :param system_content: Conteúdo inicial do prompt do sistema.
        """
        self.memory = {}  # Memória do agente
        self.client = client(api_key=api_key)  # Cliente da API (passando o cliente como parâmetro)
        self.model = model  # Modelo do LLM
        self.system_content = system_content or self.base_prompt

    def store_memory(self, key, value):
        """
        Armazena um valor na memória do agente.
        :param key: Chave para identificação da memória.
        :param value: Valor a ser armazenado.
        """
        self.memory[key] = value

    def get_memory(self, key):
        """
        Recupera um valor da memória do agente.
        :param key: Chave da memória a ser recuperada.
        """
        return self.memory.get(key)

    def clear_memory(self):
        """
        Limpa toda a memória armazenada.
        """
        self.memory.clear()
