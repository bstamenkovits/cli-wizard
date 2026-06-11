from google import genai
from cli_wizard.core.config_settings import ConfigSettings


class NoClientError(Exception):
    """
    An error raised when a Gemini client is not configured.
    """
    pass


class GeminiInterface:
    """
    Represents an interface for interacting with the Gemini API, designed for use in generating
    terminal commands, explaining commands, and answering questions relevant to terminal usage.

    This class provides specific methods for interacting with the Gemini model using a provided
    API key, allowing users to achieve various text-based tasks related to terminal usage.

    The CLI wizard keeps track of the user settings through the ConfigSettings class. These settings
    include the API key, operating system, and shell environment, which are used to customize the
    user experience and ensure compatibility with different terminal environments.

    Attributes:
        config(ConfigSettings): The configuration settings object used to access and manage API keys.
    """

    def __init__(self, config_settings: ConfigSettings):
        self.config = config_settings
        self.client = None
        self.model = "gemini-3.1-flash-lite"
        self.update_client()

    def update_client(self):
        """
        Update the gemini client used by the CLI wizard by creating a new client using the current API key in the config
        """
        api_key = self.config.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None
        # click.secho("Gemini client updated!", fg="green")

    def _execute_prompt(self, prompt:str) -> dict:
        """
        Executes a prompt using the Gemini API client.

        Args:
            prompt(str): prompt to send to Gemini API

        Raises:
            NoClientError: If no Gemini client is configured.

        Returns:
            dict: The response from the Gemini API, including the generated text and token usage.
        """
        if not self.client:
            raise NoClientError("No Gemini client configured")

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        usage_metadata = getattr(response, "usage_metadata", None)
        token_count_in = getattr(usage_metadata, "candidates_token_count", 0) or 0
        token_count_out = getattr(usage_metadata, "prompt_token_count", 0) or 0

        return {'text': response.text, 'token_count_in': token_count_in, 'token_count_out': token_count_out}

    def generate_command(self, description:str) -> dict:
        """
        Generates a terminal command based on the provided task description.

        This method takes a user-provided task description and constructs a
        prompt by combining the description with default context instructions.
        It then generates the corresponding terminal command by invoking an
        internal method to process the prompt.

        Args:
            description (str): A textual description of the task for which a terminal command is needed.

        Returns:
            dict: A dictionary containing the generated command.
        """
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

        prompt = f"{default_instructions}\n\n{description}"
        return self._execute_prompt(prompt)

    def explain_command(self, command:str) -> dict:
        """
        Explains the functionality of a given terminal command and its components in a short
        and concise manner. The explanation for each part of the command, such as keywords,
        arguments, or flags, is returned as a JSON object with descriptions of their purpose.

        Args:
            command (str): The terminal command to be analyzed and explained.

        Returns:
            dict: A JSON-like dictionary where each key represents a segment of the command
            (e.g., keywords, flags, or arguments) and each value contains a brief explanation
            of the segment's function.
        """
        default_instructions = """
        You are an expert in using the terminal. The user will provide a command and you will explain what it does.
        
        For each part of the command (key word, argument, flag, etc.), explain what it does specifically in one or two sentences.
        
        Keep your answer short, concise, and to the point. Return your answer as JSON output (only JSON code, no markdown fluff around it). The keys should be the parts of the command, the values the explanation of said command.
        
        Example input: ls -a
        
        Example output: {"ls": "List files in the current directory", "-a": "Show hidden files"}
        Incorrect output: ```json {...}```
        
        This is the command:
        """.strip()

        prompt = f"{default_instructions}\n\n{command}"
        return self._execute_prompt(prompt)

    def ask_question(self, question:str) -> dict:
        """
        Processes a question by combining it with default instructions to create a
        prompt and returns the result of executing the prompt.

        The generated answer is concise and formatted for display in a terminal
        environment. It is designed assuming the user is seeking expert-level
        advice for terminal-related inquiries.

        Args:
            question: The user's question to be processed and answered.

        Returns:
            A dictionary containing the result of the executed prompt.
        """
        default_instructions = """
        You are an expert in using the terminal. The user will ask a question and you will answer it.
        
        Your answer should be short, concise, and to the point; its meant to be displayed in a terminal, 
        keep that in mind when writing your answer.
        
        This is the user's question:
        """
        prompt = f"{default_instructions}\n\n{question}"
        return self._execute_prompt(prompt)

