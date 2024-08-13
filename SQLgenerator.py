import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def generate_sql(client, user_input, system_content=None):
    if system_content is None:
        system_content = """
        You are an assistant specialized in converting natural language queries into SQL queries. 
        Given a natural language input, you will generate a valid SQL query that can be used to retrieve the requested information from a database.

        Ensure the SQL query is syntactically correct and only use the columns and tables mentioned in the provided context. 
        If no specific columns or tables are mentioned, assume a general query structure.
        Do not include any placeholders or ask for clarification; just provide the most straightforward SQL query based on the input.
        """

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content



client = Groq(
    api_key=os.environ.get('GROQ_API_KEY')
)

user_query = "Find all orders placed by customer John Doe."
sql_query = generate_sql(client, user_query)
print(sql_query)
