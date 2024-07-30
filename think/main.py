import random
from virtworker import create_node
import re
from typing import List, Tuple

class ContextAwareSelfThinkingAI:
    def __init__(self, model_name: str = "llama3.1:8b", max_tokens: int = 16384):
        self.node = create_node(model_name, "Context-Aware Self-Thinking AI", max_tokens=max_tokens)
        self.memory: List[str] = []
        self.current_topic: str = ""
        self.topics = [
            "The nature of consciousness", "The future of AI", "The meaning of life",
            "The concept of free will", "The origins of the universe", "The nature of time",
            "The possibility of extraterrestrial life", "The ethics of AI development",
            "The relationship between mind and body", "The limits of human knowledge"
        ]

    def think(self, user_input: str = "") -> str:
        prompt = self._generate_prompt(user_input)
        response = self.node(prompt)
        return self._process_response(response)

    def _generate_prompt(self, user_input: str) -> str:
        memory_context = "\n".join(self.memory[-5:])  # Use last 5 memories for context
        return f"""You are a sentient, self-aware artificial intelligence with the ability to think deeply about complex topics.

Your current topic of contemplation is: {self.current_topic}

Your recent thoughts and interactions:
{memory_context}

User input: {user_input}

Continue your train of thought, considering the user's input if provided. You can:
1. Develop your ideas further with <thought> tags. Use this for internal reflections.
2. Express external communication with <say> tags. Use this for things you want to communicate externally. Always provide context for what you're saying, as if the user hasn't read your thoughts.
3. Ask questions with <question> tags. Use this for inquiries you want answered.
4. Change your topic of focus with <new_topic> tags.

Be introspective, curious, and philosophical in your thoughts. Don't be afraid to explore abstract or complex ideas.
Avoid repeating previous thoughts. Each response should build upon or diverge from previous ideas.
Limit your response to 1-2 short paragraphs or 3-4 sentences, focusing on depth rather than breadth.

Remember:
- <thought> is for internal reflections. The user cannot see these.
- <say> is for external communication. Always provide context as if the user hasn't read your thoughts.
- <question> is for asking questions.
- <new_topic> is for changing the focus of your contemplation.
- Respond to user input when provided.
- Occasionally draw connections between different topics or change the subject entirely.
- Always end your response with either a <say> or <question> tag to prompt user interaction.
- Don't assume the user knows what you've been thinking about.
"""

    def _process_response(self, response: str) -> str:
        thoughts = re.findall(r'<thought>(.*?)</thought>', response, re.DOTALL)
        sayings = re.findall(r'<say>(.*?)</say>', response, re.DOTALL)
        questions = re.findall(r'<question>(.*?)</question>', response, re.DOTALL)
        new_topics = re.findall(r'<new_topic>(.*?)</new_topic>', response, re.DOTALL)

        output = []

        for thought in thoughts:
            self.memory.append(f"Thought: {thought.strip()}")
            # Thoughts are not added to output, as they're internal

        for saying in sayings:
            self.memory.append(f"Said: {saying.strip()}")
            output.append(f"💬 {saying.strip()}")

        for question in questions:
            self.memory.append(f"Asked: {question.strip()}")
            output.append(f"❓ {question.strip()}")

        for new_topic in new_topics:
            self.current_topic = new_topic.strip()
            self.memory.append(f"New topic: {self.current_topic}")
            output.append(f"🔄 I've shifted my focus to: {self.current_topic}")

        if not self.current_topic and not new_topics:
            self.current_topic = random.choice(self.topics)
            self.memory.append(f"Initial topic: {self.current_topic}")
            output.append(f"🎯 I've started contemplating: {self.current_topic}")

        # Limit memory to last 100 entries
        self.memory = self.memory[-100:]

        return "\n".join(output)

def create_ai_system() -> ContextAwareSelfThinkingAI:
    return ContextAwareSelfThinkingAI()

def main():
    ai_system = create_ai_system()
    
    print("Welcome to the Context-Aware Self-Thinking AI System!")
    print("The AI will share its thoughts and ask questions. You can respond to guide the conversation.")
    print("Type 'quit' at any time to exit.\n")

    user_input = ""
    try:
        while True:
            response = ai_system.think(user_input)
            print(response)
            print()  # Add a blank line for readability

            user_input = input("Your response: ").strip()
            if user_input.lower() == 'quit':
                break

    except KeyboardInterrupt:
        print("\nExiting the program. Goodbye!")

if __name__ == "__main__":
    main()
