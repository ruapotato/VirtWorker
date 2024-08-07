import os
import subprocess
import shlex
import getpass
from typing import List, Tuple
from virtworker import create_node
import readline
import glob

class AITerminalAssistant:
    def __init__(self, model_name: str = "llama3.1:8b", max_tokens: int = 16384):
        self.username = getpass.getuser()
        self.home_folder = os.path.expanduser("~")
        self.current_directory = os.getcwd()

        self.command_executor = create_node(model_name, "Command Executor", max_tokens=max_tokens)
        self.command_executor.definition = f"""
        Interpret and convert user input into a SINGLE shell command. Return ONLY the command, nothing else.
        Use these details for context:
        - Username: {self.username}
        - Home folder: {self.home_folder}
        - Current working directory: {self.current_directory}
        IMPORTANT:
        - If the input is already a valid shell command, return it as is.
        - For natural language queries, translate to the most appropriate single command.
        - Do NOT use 'cd' or try to navigate directories unless explicitly asked by the user.
        - For file operations, assume the current directory unless specified otherwise.
        - For queries about directory contents, use 'ls' without any path arguments.
        - For file type queries, use 'file' command.
        - For file size queries, use 'du -h' with the filename.
        - For creating multiple files, use a for loop: for i in $(seq 1 10); do touch $i.txt; done
        - DO NOT use brace expansion {{1..10}} as it may not work in all environments.
        - DO NOT combine multiple commands using ';', '&&', or '|'.
        - DO NOT provide any explanations or comments. Return ONLY the command.
        """

        self.error_handler = create_node(model_name, "Error Handler", max_tokens=max_tokens)
        self.error_handler.definition = "Analyze errors and provide a single, simple corrected command. Do not provide explanations."

        self.context = []

    def execute_command(self, user_input: str) -> str:
        try:
            # Update current directory
            self.current_directory = os.getcwd()
            
            # Add user input to context
            self.context.append(user_input)
            
            # Use AI to interpret the user input and convert to a command if necessary
            interpretation = self.command_executor(f"""
            Context: {self.context}
            User Input: {user_input}
            Current Directory: {self.current_directory}
            Translate the user input into a SINGLE shell command. Return ONLY the command, nothing else.
            If the input is already a valid shell command, return it as is.
            Do not provide any explanations or comments.
            """)
            
            # Extract the command from the interpretation
            command = interpretation.strip()
            
            # Execute the actual command
            if command.startswith("cd "):
                # Handle 'cd' command separately
                path = command.split(" ", 1)[1]
                os.chdir(os.path.expanduser(path))
                result = f"Changed directory to {os.getcwd()}"
            else:
                # Execute other commands using subprocess
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
                stdout, stderr = process.communicate()
                result = stdout if stdout else stderr

            return f"User Input: {user_input}\n\nInterpreted Command: {command}\n\nResult:\n{result}"
        except Exception as e:
            return self.handle_error(str(e), user_input, command)

    def handle_error(self, error: str, user_input: str, command: str) -> str:
        error_analysis = self.error_handler(f"""
        Error: {error}
        User Input: {user_input}
        Interpreted Command: {command}
        Context: {self.context}
        Current Directory: {self.current_directory}
        Provide ONLY a single, simple corrected command. No explanations.
        """)
        
        print(f"Error occurred: {error}")
        print(f"Suggested command: {error_analysis}")
        
        confirmation = input(f"Would you like to execute the suggested command: {error_analysis}? (y/n) ")
        if confirmation.lower() == 'y':
            return self.execute_command(error_analysis)
        
        return "Command execution aborted."

def setup_readline():
    # Enable tab completion
    readline.parse_and_bind('tab: complete')
    
    # Set up auto-completion function
    def complete(text, state):
        return (glob.glob(os.path.expanduser(text) + '*') + [None])[state]
    
    readline.set_completer(complete)
    readline.set_completer_delims(' \t\n;')

def main():
    assistant = AITerminalAssistant()
    setup_readline()
    
    print("Welcome to the AI-Powered Terminal Assistant!")
    print("This assistant interacts with your real file system. Use with caution.")
    print("You can use natural language queries or standard shell commands.")
    print("Type 'exit' to quit.")

    while True:
        try:
            user_input = input(f"{os.getcwd()}$ ")
            if user_input.lower() == 'exit':
                break

            # Execute command or process natural language query
            result = assistant.execute_command(user_input)
            print(result)

        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")

    print("Goodbye!")

if __name__ == "__main__":
    main()
