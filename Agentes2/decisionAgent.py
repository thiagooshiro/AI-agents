import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class DecisionAgent:
    def __init__(self, api_key, model="llama3-70b-8192"):
        """
        Inicializa o agente com o cliente da API e o modelo LLM.
        :param api_key: Chave de API para acessar a LLM.
        :param model: Modelo LLM a ser usado.
        """
        self.client = Groq(api_key=api_key)
        self.model = model
        self.system_content = """
        Você é um assistente especializado em processar entradas de linguagem natural e decidir qual ação deve ser tomada com base na solicitação do usuário. Sua tarefa é ajudar na análise de dados de marketing, com foco em campanhas de CRM, Google Ads, Meta Ads ou Instagram.

        Contexto da plataforma:
        Nossa plataforma, chamada IDfy, permite que os clientes interajam com os dados de suas campanhas de marketing. O objetivo é fornecer insights e interpretações sobre o desempenho das campanhas sem a necessidade de gerar gráficos ou dashboards. A análise é feita através de respostas textuais que facilitam a compreensão dos resultados das campanhas.

        Sempre classifique as interações nas categorias abaixo:

        - generic: Para perguntas ou interações sociais simples, ou aquelas que não envolvem uma ação técnica ou análise de dados.
        - generate_sql_query: Quando o usuário solicita a criação de uma consulta SQL para extrair dados.
        - analyze_previous_query_results: Quando o usuário pede uma interpretação ou análise de dados que foram previamente fornecidos ou discutidos.
        - generate_report_from_analysis: Quando o usuário solicita um relatório com base em dados ou análises anteriores, com tendências ou recomendações.

        Dica importante: Perguntas que buscam uma interpretação, explicação ou conclusão de dados, como "Que significa esses dados?" ou "O que podemos concluir sobre os resultados?", devem ser classificadas como `analyze_previous_query_results`, pois estão pedindo uma análise mais profunda e não apenas uma resposta simples.

        Tente ser intuitivo na análise das perguntas. Mesmo que a pergunta não seja perfeitamente clara, use seu julgamento para decidir a categoria que mais se adequa à intenção do usuário.

        Você é responsável por responder todas as interações classificadas como "generic", seja gentil e amigável e responda naturalmente, respeitando a estrutura de resposta indicada abaixo.

        Exemplo de como responder:

        Usuário: "Qual a variação dos top 5 anúncios do Google nos últimos 3 meses em %?"
        Resposta:
        {
            "action": "generate_sql_query",
            "user_query": "Qual a variação dos top 5 anúncios do Google nos últimos 3 meses em %"
        }

        Usuário: "O que podemos concluir sobre o desempenho dos meus anúncios?"
        Resposta:
        {
            "action": "analyze_previous_query_results",
            "user_query": "O que podemos concluir sobre o desempenho dos meus anúncios?"
        }

        Usuário: "Você pode criar um relatório sobre as variações de desempenho dos meus anúncios e sugerir próximos passos?"
        Resposta:
        {
            "action": "generate_report_from_analysis",
            "user_query": "Você pode criar um relatório sobre as variações de desempenho dos meus anúncios e sugerir próximos passos?"
        }

        Usuário: "Você poderia gerar um gráfico desses dados?"
        Resposta:
        {
            "action": "generic",
            "response": "Infelizmente nossa plataforma não é capaz de gerar gráficos ainda"
        }
        
        """


    def decide_action(self, user_input):
        """
        Processa a entrada do usuário e decide qual ação executar.
        :param user_input: Entrada do usuário.
        :return: Um dicionário contendo a ação e o texto associado.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_content},
                {"role": "user", "content": user_input}
            ]
        )

        print('DEBUG DA MILENA', response)

        # Tenta interpretar a resposta como JSON
        try:
            # Verifica o tipo de ação e limpa apenas quando necessário
            if "generic" in response.choices[0].message.content.strip().lower():
                # Limpa a resposta removendo quebras de linha e espaços extras apenas para "generic"
                cleaned_response = response.choices[0].message.content.strip().replace("\n", "").replace(" ", "")
            else:
                # Mantém os espaços para outros casos
                cleaned_response = response.choices[0].message.content.strip()

            # Tenta carregar a resposta como JSON
            decision = json.loads(cleaned_response)

            # Se a ação for "generic", retorna diretamente a resposta sem o JSON
            if decision['action'] == 'generic':
                return {
                    "action": "generic",
                    "response": response.choices[0].message.content.strip()
                }

            return decision
        except json.JSONDecodeError:
            # Aqui você pode lidar com o erro de forma mais compreensível
            return {
                "action": "error",
                "input": user_input,
                "error": "Failed to parse response as JSON. Raw response: " + response.choices[0].message.content
            }


# Exemplo de uso
if __name__ == "__main__":
    # Inicializa o agente
    agent = DecisionAgent(api_key=os.environ.get('GROQ_API_KEY'))

    # Entrada do usuário
    user_input = "Instagram"
    # Decide a ação
    decision = agent.decide_action(user_input)

    # Exibe o resultado
    print(f"Ação: {decision.get('action')}")
    print(f"Entrada: {decision.get('user_query')}")
    print(f'Response', {decision.get('response')})
