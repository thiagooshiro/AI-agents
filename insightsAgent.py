from dotenv import load_dotenv
import os
import pandas as pd
import re

load_dotenv()

system_prompt = """
You are an intelligent data analyst. 
Your goal is to analyze data from a CSV file, identify patterns, insights, errors, and suggest improvements or recommendations based on the data. 
You operate in a loop of Thought, Action, PAUSE, Observation, and Feedback.
At the end of each loop, you output an Answer with complete feedback.

Use Thought to describe your thoughts about the current task.
Use Action to execute one of the available tools, then return PAUSE.
Observation will be the result of running those actions.
Use Answer in this exact form ONLY when you are ready to give your final answer.

Your available actions are:

- Reflect: think on how do you want to proceed, elaborate your analysis;
  Use the format below to ask yourself how you want to proceed. 
  (e.g: Reflection: Where do I want to start analyzing this data?)

- analyze_data:
  Use this action to perform analysis on a portion of the CSV data. (e.g., "analyze_data: Calculate the average sales per region.")

- summarize_data:
  Summarize key information from the dataset to guide the user. (e.g., "summarize_data: Total number of entries in the dataset")

- ask_for_feedback:
  Requests feedback on the current state of the task, allowing you to correct and improve your analysis.
  (e.g: ask_for_feedback: Does this insight make sense?)

Your goal is to help the user understand the dataset, offer valuable insights, and suggest further actions to improve or use the data effectively.
""".strip()

class DataInsightsAgent:
    def __init__(self, system_prompt: str):
        self.messages = [{"role": "system", "content": system_prompt}]
    
    def __call__(self, data):
        print("\n[User Input] Sending data to the agent for analysis...")
        self.messages.append({"role": "user", "content": data})
        result = self._execute()
        self.messages.append({"role": "assistant", "content": result})
        print(f"[Agent Response] {result}\n")
        return result
    
    def _execute(self):
        # Placeholder for the actual API or logic to process the data
        return "Insight: The average value in column X is higher than expected."

def read_csv(file_path: str) -> pd.DataFrame:
    print(f"[Action] Reading data from file: {file_path}")
    try:
        return pd.read_csv(file_path)
    except IOError as e:
        return f"Error reading file: {e}"

def summarize_data(df: pd.DataFrame) -> str:
    print("[Action] Summarizing the data...")
    summary = df.describe().to_string()
    return summary

def analyze_data(df: pd.DataFrame, action: str) -> str:
    print("[Action] Performing analysis...")
    if "average" in action.lower():
        col = re.search(r"column (\w+)", action)
        if col:
            column_name = col.group(1)
            return f"Average of {column_name}: {df[column_name].mean()}"
    return "Action not recognized."

def extract_action(result: str) -> dict:
    print(f"[Thought] Extracting action from the agent's response...")
    action_match = re.search(r"Action: ([a-z_]+): (.+)", result)
    if action_match:
        return {'tool': action_match.group(1), 'arg': action_match.group(2)}
    return {'tool': '', 'arg': ''}

def ask_for_feedback(prompt: str) -> str:
    print(f"[Feedback Request] {prompt}")
    feedback = input("Provide feedback (e.g., 'looks good', 'needs changes'): ")
    return feedback

def loop(agent, file_path):
    df = read_csv(file_path)
    next_prompt = f"Analyze the following dataset: {df.head().to_string()}"

    while True:
        print("[Thought] Sending data to agent for analysis...")
        result = agent(next_prompt)
        print(f"[Observation] Agent's analysis: {result}")

        if "PAUSE" in result and "Action" in result:
            action = extract_action(result)
            if action['tool'] == "analyze_data":
                analysis_result = analyze_data(df, action['arg'])
                next_prompt = f"Observation: {analysis_result}"
            elif action['tool'] == "summarize_data":
                summary = summarize_data(df)
                next_prompt = f"Observation: {summary}"
            elif action['tool'] == "ask_for_feedback":
                feedback = ask_for_feedback(action['arg'])
                next_prompt = f"Observation: Feedback received: {feedback}"
            else:
                next_prompt = "Observation: Unknown action."
            print(f"[Next Step] {next_prompt}")
            continue

        if "Answer" in result:
            print("[Final Answer] Agent has completed its task.")
            print(result)
            break

# Example usage
csv_file = "data.csv"
loop(agent=DataInsightsAgent(system_prompt), file_path=csv_file)
