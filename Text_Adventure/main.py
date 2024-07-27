import curses
import textwrap
import re
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
def generate_story(story_node, last_action, player_state):
    prompt = f"""The player's last action was: "{last_action}"

Current player state:
{player_state}

Based on this information, generate the next part of the story. Describe the result of the player's action and the new situation they find themselves in. Be concise but descriptive.

If the action is impossible, explain why and ask the player to try something else.

If the player takes damage, include a <damage>X</damage> tag, where X is the amount of damage taken.
If the player heals, include a <heal>X</heal> tag, where X is the amount healed.
If the player's location changes, include a <location>new_location</location> tag.
If the player picks up an item, include an <item>item_name</item> tag.
If the player loses an item, include a <lost>item_name</lost> tag.

Do not repeat the player's action or their current state in your response. Focus on describing what happens next and any changes to the environment or player's situation."""

    return story_node(prompt)

@print_ai_call
def summarize_story(summarizer_node, story):
    prompt = f"""Summarize this story concisely, keeping only the most important details:

{story}"""
    return summarizer_node(prompt)

def update_player_health(player_state, result):
    damage_matches = re.findall(r'<damage>(\d+)</damage>', result)
    heal_matches = re.findall(r'<heal>(\d+)</heal>', result)
    
    for damage in damage_matches:
        player_state['health'] -= int(damage)
    
    for heal in heal_matches:
        player_state['health'] = min(100, player_state['health'] + int(heal))
    
    player_state['health'] = max(0, player_state['health'])  # Ensure health doesn't go below 0
    
    return player_state['health'] > 0

def init_curses():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.curs_set(1)  # Show cursor
    return stdscr

def end_curses(stdscr):
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

def draw_ui(stdscr, player_state, story, input_buffer):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    
    # Draw header
    header = "Text Adventure Game"
    stdscr.addstr(0, (width - len(header)) // 2, header, curses.color_pair(1) | curses.A_BOLD)
    
    # Draw player stats
    stats = f"Health: {player_state['health']} | Location: {player_state['location']} | Items: {', '.join(player_state['items'])}"
    stdscr.addstr(2, 0, stats, curses.color_pair(3))
    
    # Draw story
    story_lines = textwrap.wrap(story, width - 2)
    for i, line in enumerate(story_lines[-height+7:]):
        stdscr.addstr(4 + i, 1, line)
    
    # Draw input prompt
    prompt = "> "
    stdscr.addstr(height - 2, 0, prompt)
    stdscr.addstr(height - 2, len(prompt), input_buffer)
    
    stdscr.refresh()

def parse_ai_response(response):
    # Remove any mentions of the player's current state
    cleaned_response = re.sub(r'Current player state:.*?}', '', response, flags=re.DOTALL).strip()
    # Remove any "What would you like to do?" prompts
    cleaned_response = re.sub(r'What would you like to do\?.*', '', cleaned_response).strip()
    # Remove any mentions of the player's situation remaining unchanged
    cleaned_response = re.sub(r'Your current situation remains.*?\.', '', cleaned_response).strip()
    return cleaned_response

def game_loop(stdscr, story_node, summarizer_node):
    initial_context = "You're at the edge of a forest, with the cliffs on your back. Two paths are up ahead, one dark and well-trodden, one bright and overgrown."
    story = initial_context
    player_state = {
        "location": "forest edge",
        "items": [],
        "abilities": ["walk", "run", "talk"],
        "health": 100
    }
    
    input_buffer = ""
    
    while True:
        draw_ui(stdscr, player_state, story, input_buffer)
        
        key = stdscr.getch()
        if key == ord('\n'):  # Enter key
            action = input_buffer.strip()
            input_buffer = ""
            
            if action.lower() == 'quit':
                break
            
            result = generate_story(story_node, action, player_state)
            if result:
                parsed_result = parse_ai_response(result)
                
                # Only add the new content to the story
                story = f"{parsed_result}"
                
                if not update_player_health(player_state, parsed_result):
                    story += "\nYour health has dropped to 0 or below. Game over!"
                    draw_ui(stdscr, player_state, story, input_buffer)
                    stdscr.getch()
                    break
                
                # Update player_state based on the parsed result
                new_location = re.search(r"<location>'?(.*?)'?</location>", parsed_result)
                if new_location:
                    player_state["location"] = new_location.group(1)
                
                new_items = re.findall(r"<item>(.*?)</item>", parsed_result)
                for item in new_items:
                    if item not in player_state["items"]:
                        player_state["items"].append(item)
                
                lost_items = re.findall(r"<lost>(.*?)</lost>", parsed_result)
                for item in lost_items:
                    if item in player_state["items"]:
                        player_state["items"].remove(item)
        
        elif key == curses.KEY_BACKSPACE or key == 127:
            input_buffer = input_buffer[:-1]
        elif key == curses.KEY_RESIZE:
            stdscr.clear()
        else:
            input_buffer += chr(key)
        
        stdscr.move(stdscr.getmaxyx()[0] - 2, len("> ") + len(input_buffer))

def main():
    try:
        nodes = create_nodes()
        stdscr = init_curses()
        game_loop(stdscr, nodes['story'], nodes['summarizer'])
    except Exception as e:
        end_curses(stdscr)
        print(f"An error occurred: {str(e)}")
        print("Game initialization failed. Please try running the game again.")
    finally:
        end_curses(stdscr)

if __name__ == "__main__":
    main()
