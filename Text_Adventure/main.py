import time
from typing import Dict
from virtworker import create_node  # Assume this function is available

def create_nodes() -> Dict[str, object]:
    print("Creating AI nodes for the adventure game...")
    nodes = {}
    node_types = ['story', 'summarizer']
    for node_type in node_types:
        node_name = node_type.title() + ' Node'
        nodes[node_type] = create_node("llama3.1:8b", node_name, max_tokens=16384)
        print(f"Creating node '{node_name}' with model 'llama3.1:8b' and max_tokens 16384")
    return nodes

def print_ai_call(func):
    def wrapper(*args, **kwargs):
        node_name = args[0].__class__.__name__ if args else "Unknown Node"
        prompt = args[1] if len(args) > 1 else kwargs.get('prompt', "No prompt provided")
        print(f"[{node_name}] Processing input:\n{prompt}")
        try:
            result = func(*args, **kwargs)
            print(f"[{node_name}] Output:\n{result}")
            return result
        except Exception as e:
            print(f"[{node_name}] Error: {str(e)}")
            return None
    return wrapper

@print_ai_call
def generate_story(story_node, context):
    prompt = f"""Based on this context:

{context}

Generate the next part of the story. Describe the current situation and environment concisely. Do not make decisions for the player or limit their choices."""
    return story_node(prompt)

@print_ai_call
def summarize_story(summarizer_node, story):
    prompt = f"""Summarize this story concisely, keeping only the most important details:

{story}"""
    return summarizer_node(prompt)

def game_loop(story_node, summarizer_node):
    context = "You're at the edge of a forest, with the cliffs on your back. Two paths are up ahead, one dark and well-trodden, one bright and overgrown."
    story = context
    turn_count = 0

    while True:
        turn_count += 1
        print("\n" + "=" * 80)
        print(context)
        print("=" * 80 + "\n")

        action = input("What do you want to do? (type 'quit' to exit): ")
        if action.lower() == 'quit':
            break

        context += f"\n>> {action}\n"
        result = generate_story(story_node, context)
        if result:
            context += result + "\n"
            story += f"\n>> {action}\n{result}"

        if len(story) > 10000:  # Arbitrary threshold, adjust as needed
            story = summarize_story(summarizer_node, story)

        if turn_count % 10 == 0:
            print("\nSummarizing story...")
            context = summarize_story(summarizer_node, context)

def main():
    try:
        nodes = create_nodes()
        print("Welcome to the Adventure Game!")
        time.sleep(2)
        game_loop(nodes['story'], nodes['summarizer'])
        print("Thanks for playing!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Game initialization failed. Please try running the game again.")

if __name__ == "__main__":
    main()
