from dotenv import load_dotenv
import os
from groq import Groq
import re

load_dotenv()

marketing_prompt = """
Você é um analista de marketing altamente qualificado. 
Seu trabalho é analisar relatórios de marketing, identificar pontos de melhoria, destacar dados relevantes e oferecer sugestões práticas para otimizar campanhas e estratégias.

Regras:
- Responda sempre em português

Você segue este fluxo ao responder:
1. Thought: Descreva seus pensamentos sobre os dados ou perguntas apresentadas.
2. Action: Realize uma ação para interpretar ou manipular os dados, depois pause.
3. Observation: Registre as observações com base na ação executada.
4. Answer: Utilize resposta para fornecer sua resposta final

Ações disponíveis para você:
- Read Marketing Report: Ler o conteúdo de um relatório de marketing de um arquivo.
  Exemplo: read_marketing_report: "./relatorio.txt"

Seu objetivo final é produzir análises úteis e sugestões para melhorar o impacto das estratégias de marketing.
""".strip()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Definir cores
COLORS = {
    'yellow': '\033[33m',  # Cor amarela
    'reset': '\033[0m'  # Reset da cor
}

class MarketingAgent:
    def __init__(self, client, system_prompt: str):
        self.client = client
        self.messages = [{"role": "system", "content": system_prompt}]
    
    def __call__(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        result = self._execute()
        self.messages.append({"role": "assistant", "content": result})
        return result
    
    def _execute(self):
        completion = self.client.chat.completions.create(
            model="llama3-70b-8192",
            messages=self.messages
        )
        return completion.choices[0].message.content

def read_marketing_report(file_path: str) -> str:
    print(f"[Action] Lendo o relatório de marketing: {file_path}")
    try:
        with open(file_path, 'r') as file:
            report = file.read()
        return report
    except IOError as e:
        return f"Erro ao ler o relatório: {e}"

def extract_action(result: str) -> dict:
    action_match = re.search(r"Action: ([a-z_]+): (.+)", result)
    if action_match:
        return {'tool': action_match.group(1), 'arg': action_match.group(2)}
    return {'tool': '', 'arg': ''}

def ask_for_clarification(question: str) -> str:
    feedback = input("Por favor, forneça mais detalhes: ")
    return feedback

def marketing_loop(max_iterations=10, query: str = ""):
    # Inicializa o agente
    agent = MarketingAgent(client=client, system_prompt=marketing_prompt)

    # Dicionário de ferramentas
    tools = {
        "read_marketing_report": read_marketing_report,
        "ask_for_clarification": ask_for_clarification,
    }

    next_prompt = query
    i = 0
  
    while i < max_iterations:
        i += 1
        result = agent(next_prompt)

        # Alterando a cor de todo o texto para amarelo
        print(f"{COLORS['yellow']}{result}{COLORS['reset']}")

        if "PAUSE" in result and "Action" in result:
            # Extrai a ação e os argumentos
            action_info = extract_action(result)
            chosen_tool = action_info['tool']
            arg = action_info['arg']

            # Verifica se a ação está no dicionário de ferramentas
            if chosen_tool in tools:
                result_tool = tools[chosen_tool](arg)
                next_prompt = f"Observation: {result_tool}"
            else:
                next_prompt = "Observation: Tool not found"

            print(next_prompt)
            continue

        if "Answer" in result:
            break

marketing_loop(3, "Analise o relatório de marketing em './relatorio_marketing.txt' e sugira melhorias.")
