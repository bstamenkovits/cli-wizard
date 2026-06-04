from google import genai
import json
import click
from cli_wizard.config import load_config


class GeminiInterface:

    def __init__(self, config):
        self.config = config
        self.client = None
        self.model = "gemini-3.1-flash-lite"
        self.update_client()

    def update_client(self):
        api_key = self.config.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None
        # click.secho("Gemini client updated!", fg="green")

    def generate_command(self, question:str) -> dict:
        default_instructions = f"""
        You are an agent that helps users come up with terminal commands.
        
        You are specifically meant to help new users navigate the terminal.  
        
        The user will provide you with a task they want to complete. Your job is
        to generate the correct CLI command to run.
        
        The command should be a single line, only return the command, nothing else.
        
        The user is using this Operating System: {self.config.get('OS', 'Unknown')}
        The user is using this Shell/Terminal: {self.config.get('SHELL', 'Unknown')}
        
        The user's input is: 
        """.strip()

        if not self.client:
            return 0
        response = self.client.models.generate_content(
            model=self.model,
            contents=f"{default_instructions}\n\n{question}"
        )

        usage_metadata = getattr(response, "usage_metadata", None)
        token_count_in = getattr(usage_metadata, "candidates_token_count", 0) or 0
        token_count_out = getattr(usage_metadata, "prompt_token_count", 0) or 0

        return {"command": response.text, "token_count_in": token_count_in, "token_count_out": token_count_out}

    def explain_command(self, command:str) -> dict:
        default_instructions = """
        You are an expert in using the terminal. The user will provide a command and you will explain what it does.
        
        For each part of the command (key word, argument, flag, etc.), explain what it does specifically in one or two sentences.
        
        Keep your answer short, concise, and to the point. Return your answer as JSON output (only JSON code, no markdown fluff around it). The keys should be the parts of the command, the values the explanation of said command.
        
        Example input: ls -a
        
        Example output: {"ls": "List files in the current directory", "-a": "Show hidden files"}
        Incorrect output: ```json {...}```
        
        This is the command:
        """.strip()

        if not self.client:
            return 0
        response = self.client.models.generate_content(
            model=self.model,
            contents=f"{default_instructions}\n\n{command}"
        )

        usage_metadata = getattr(response, "usage_metadata", None)
        token_count_in = getattr(usage_metadata, "candidates_token_count", 0) or 0
        token_count_out = getattr(usage_metadata, "prompt_token_count", 0) or 0

        return {"explanation": response.text, "token_count_in": token_count_in, "token_count_out": token_count_out}


if __name__ == "__main__":
    config = {'GEMINI_API_KEY': "***REMOVED***"}
    gem = GeminiInterface(config)
    output = gem.generate_command("ls -a")

