def generate_sql(self, user_input, system_content=None):
    if system_content is None:
        system_content = """
        You are an assistant specialized in converting natural language queries into SQL queries. 
        Given a natural language input, you will generate a valid SQL query that can be used to retrieve the requested information from a database.

        Ensure the SQL query is syntactically correct and only use the columns and tables mentioned in the provided context. 
        If no specific columns or tables are mentioned, assume a general query structure.
        Do not include any placeholders or ask for clarification; just provide the most straightforward SQL query based on the input.
        """

    response = self.client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content


