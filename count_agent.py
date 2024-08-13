import os
from dotenv import load_dotenv
from count_prompt import system_prompt

load_dotenv()

from groq import Groq

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)


class CountAgent:
    def __init__(self, client: Groq, system: str = "") -> None:
        self.client = client
        self.system = system
        self.messages: list = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message=""):
        if message:
            self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        completion = client.chat.completions.create(
            model="llama3-70b-8192", messages=self.messages
        )
        return completion.choices[0].message.content

# Initialize the agent with the refined system prompt



agent = CountAgent(client, system_prompt)


def introAgent():
    intro_text = """
    Com muito esforço, você conseguiu requisitar uma audiência com o Conde Pedro de Almeida Vasconcelos para investigar o brutal assassinato que abalou a cidade. O Conde, relutante, aquiesceu à sua requisição e você foi convocado para comparecer em sua residência em Mariana.

    Ao chegar, você é recebido com um ar de formalidade por um membro da guarda pessoal do Conde. O saguão principal da mansão é imponente: um enorme salão com uma mesa ampla central e o brasão de armas da família estampado na parede. As janelas largas permitem que a luz natural ilumine a sala, destacando a opulência do ambiente. Dois escravizados permanecem em cantos obscuros, quase invisíveis, enquanto um dos guardas que o escoltou ainda permanece de vigilância junto à porta.

    Você ouve passos firmes e ritmados no corredor. O Conde finalmente entra na sala.

    Ele é um homem esguio, com uma postura rígida e um olhar que reflete tanto sua autoridade quanto seu desdém. Sua vestimenta, embora de tecidos finos, é sóbria e quase remete a um uniforme militar, sem qualquer ostentação desnecessária. O Conde caminha pela sala com passos precisos e controlados, observando você com um olhar avaliativo e carregado de desgosto.

    Sem disfarçar a irritação por sua presença, o Conde faz um gesto imperioso para que você se sente. O ambiente está carregado de uma tensão palpável, um reflexo da resistência que o Conde sente em cooperar com sua investigação.

    A conversa está prestes a começar. Prepare-se para um diálogo em que cada palavra é carregada de formalidade e ressentimento.

    Que o interrogatório comece.
    """
    print(intro_text)

def conversationLoop(agent):
    introAgent()
    print("\nO Conde está pronto para começar a conversa. Use uma linguagem formal e respeitosa.")

    while True:
        user_input = input("\nVocê: ").strip()
        
        # Condição para encerrar a conversa
        if user_input.lower() in ["sair", "adeus", "encerrar"]:
            print("\nConde: Como desejar. Espero que tenha uma boa jornada.")
            break

        # Enviar entrada do usuário para o Conde e obter a resposta
        response = agent(user_input)
        print(f"\nConde: {response}")

        # Verificar se a conversa foi encerrada pelo Conde
        if "encerrar" in response.lower():
            print("\nConde: Nossa conversa foi bastante reveladora. Até a próxima.")
            break
        
the_count = CountAgent(client, system_prompt )
conversationLoop(the_count)