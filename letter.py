from crewai import Agent, Crew, Task, Process
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

secret_key = os.environ['OPENAI_API_KEY']


llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=secret_key)

agent_role = 'Você é um jovem viajante do século XVIII'
agent_goal = 'Escrever uma carta para sua amada contando sobre suas incríveis descobertas'
agent_backstory = 'Sempre apaixonado e dedicado, você encontrou seu verdadeiro proposito nas ciências e nas artes, se tornou viajante por algum desejo quase inescapável de viajar (wanderlust), mas sente falta da moça pela qual se apaixonou'

task_description = 'Faz muito tempo que você não escreve uma carta para sua querida Gabrielle'
task_outputformat ='Um texto em formato md, com os campos adequados de uma carta escrita à mão: data, local, uma introdução apropriada, o desenvolvimento do assunto e uma finalização também seguindo os mesmos padrões de uma carta'
# Define Agents
generic_agent = Agent(
    role=agent_role,
    goal=agent_goal,
    backstory=(
        agent_backstory
    ),
    verbose=True,
    llm=llm,
    
)

transform_query_task = Task(
    description=task_description,
    expected_output=task_outputformat,
    agent=generic_agent,
)

# Form the Crew
crew = Crew(
    agents=[generic_agent],
    tasks=[transform_query_task],
    process=Process.sequential,
    verbose=True
)


# Example input
inputs = {
    'user_question': 'Escrever uma carta para os familiares'
}

# Kickoff the crew process
result = crew.kickoff(inputs=inputs)

# Print the results
print(result)