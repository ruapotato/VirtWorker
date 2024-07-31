import os
import re
from typing import List, Tuple
from virtworker import create_node

class AITerminalAssistant:
    def __init__(self, model_name: str = "llama3.1:8b", max_tokens: int = 16384):
        self.command_executor = create_node(model_name, "Command Executor", max_tokens=max_tokens)
        self.command_executor.definition = "Execute terminal commands and provide feedback."

        self.error_handler = create_node(model_name, "Error Handler", max_tokens=max_tokens)
        self.error_handler.definition = "Analyze errors and provide helpful feedback."

        self.auto_completer = create_node(model_name, "Auto Completer", max_tokens=max_tokens)
        self.auto_completer.definition = "Suggest command completions based on input."

        self.context = []

    def execute_command(self, command: str) -> str:
        try:
            # Add command to context
            self.context.append(command)
            
            # Use AI to interpret and execute the command
            result = self.command_executor(f"Context: {self.context}\nCommand: {command}")
            
            # Execute actual file operations
            if command.startswith("rename ") or command.startswith("mv "):
                old_name, new_name = command.split(" ")[1:]
                os.rename(old_name, new_name)
                return f"Renamed {old_name} to {new_name}"
            elif command.startswith("cp "):
                src, dest = command.split(" ")[1:]
                with open(src, 'r') as src_file, open(dest, 'w') as dest_file:
                    dest_file.write(src_file.read())
                return f"Copied {src} to {dest}"
            elif command.startswith("replace function "):
                file_name, old_func, new_func = re.match(r"replace function (\S+) with (\S+) in (\S+)", command).groups()
                with open(file_name, 'r') as file:
                    content = file.read()
                content = content.replace(old_func, new_func)
                with open(file_name, 'w') as file:
                    file.write(content)
                return f"Replaced function {old_func} with {new_func} in {file_name}"
            
            return result
        except Exception as e:
            return self.handle_error(str(e), command)

    def handle_error(self, error: str, command: str) -> str:
        return self.error_handler(f"Error: {error}\nCommand: {command}\nContext: {self.context}")

    def auto_complete(self, partial_command: str) -> str:
        return self.auto_completer(f"Partial command: {partial_command}\nContext: {self.context}")

def main():
    assistant = AITerminalAssistant()
    
    print("Welcome to the AI-Powered Terminal Assistant!")
    print("Type 'exit' to quit.")

    while True:
        try:
            command = input("$ ")
            if command.lower() == 'exit':
                break

            if command.endswith('\t'):
                # Auto-complete
                suggestion = assistant.auto_complete(command[:-1])
                print(f"Suggestion: {suggestion}")
            else:
                # Execute command
                result = assistant.execute_command(command)
                print(result)

        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")

    print("Goodbye!")

if __name__ == "__main__":
    main()
