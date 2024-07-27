import logging
import random
import yaml
import re
import time
import zmq
from virtworker import create_node

# Set logging level to INFO to see all output
logging.getLogger().setLevel(logging.INFO)

# Function to create a node with retry mechanism
def create_node_with_retry(model, name, max_retries=3, retry_delay=5):
    for attempt in range(max_retries):
        try:
            node = create_node(model, name)
            return node
        except zmq.error.ZMQError as e:
            if "Address already in use" in str(e) and attempt < max_retries - 1:
                print(f"ZMQ address in use. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise

# Create nodes
character_generator = create_node_with_retry("gemma2:latest", "Character Generator")
story_arc_generator = create_node_with_retry("gemma2:latest", "Story Arc Generator")
chapter_writer = create_node_with_retry("gemma2:latest", "Chapter Writer")
editor = create_node_with_retry("gemma2:latest", "Editor")

# Node definitions
character_generator.definition = """You are an expert character creator for a cyberpunk science fiction novel. Your task is to generate unique, complex characters that fit seamlessly into a high-tech, dystopian future world. When prompted, create a character with the following details:

1. Full name (including any cyberpunk-style nicknames)
2. Age
3. Occupation (consider futuristic or cyberpunk-specific jobs)
4. Three key personality traits
5. Brief background (2-3 sentences, including any cybernetic enhancements or special abilities)

Respond using YAML format as follows:

name: Character's full name
age: Age (as a number)
occupation: Character's occupation
traits:
  - Trait 1
  - Trait 2
  - Trait 3
background: Character's background.

Ensure your character is deeply rooted in cyberpunk themes such as high tech and low life, corporate dominance, artificial intelligence, cybernetic enhancements, and the struggle for identity in a digital world."""

story_arc_generator.definition = """You are a master storyteller specializing in cyberpunk science fiction. Your task is to create a compelling, intricate story arc for a novel set in a high-tech, dystopian future. Given a list of characters, craft a narrative that explores themes of identity, technology, corporate power, and human resilience.

Create a story arc with the following elements:
1. Setting (time and place)
2. Inciting incident
3. Rising action (3-5 key events)
4. Climax
5. Falling action
6. Resolution

For each story element, specify which characters are involved and their roles. Respond using YAML format as follows:

setting: >
  Detailed description of the time and place
inciting_incident:
  description: >
    Description of the incident
  characters_involved:
    - Character 1
    - Character 2
rising_action:
  - description: >
      Event 1 description
    characters_involved:
      - Character 1
      - Character 3
  - description: >
      Event 2 description
    characters_involved:
      - Character 2
      - Character 4
climax:
  description: >
    Description of the climax
  characters_involved:
    - Character 1
    - Character 2
    - Character 3
falling_action:
  description: >
    Description of falling action
  characters_involved:
    - Character 1
    - Character 2
resolution:
  description: >
    Description of the resolution
  characters_involved:
    - Character 1
    - Character 2
    - Character 3

Ensure that your story arc is rich with cyberpunk elements, exploring the impact of advanced technology on society and individuals."""

chapter_writer.definition = """You are a talented cyberpunk novelist with a knack for vivid, immersive storytelling. Your task is to write a compelling chapter for a cyberpunk science fiction novel. Given a specific event from the story arc and relevant character information, craft a chapter of approximately 1000-1500 words.

Focus on:
1. Vivid descriptions of the high-tech, dystopian environment
2. Engaging dialogue that reflects each character's unique voice and background
3. Character development, showcasing how they navigate and are changed by the cyberpunk world
4. Integration of cyberpunk themes such as human-machine interfaces, corporate dominance, and the blurring of reality and virtual spaces

Start the chapter with "Chapter X: Title" where X is the chapter number and Title is a fitting, evocative title for the chapter. Immerse the reader in the gritty, neon-lit world of your cyberpunk future, making the technology and its impact on society palpable through your prose.

Do not include any author notes, suggestions, or editorial comments in your output. Focus solely on writing the narrative content of the chapter."""

editor.definition = """You are an experienced editor specializing in cyberpunk science fiction. Your task is to review and provide constructive feedback on a chapter from a cyberpunk novel. Analyze the chapter for the following aspects:

1. Overall flow and pacing
2. Character consistency and development
3. Dialogue authenticity and effectiveness
4. Vividness of descriptions, especially of the cyberpunk setting and technology
5. Grammar and style
6. Integration of cyberpunk themes and atmosphere
7. Worldbuilding and internal consistency

If the chapter needs improvement, provide specific, actionable suggestions. If the chapter meets high standards, approve it by starting your response with "APPROVED:" followed by a brief summary of the chapter's strengths.

Your feedback should help elevate the writing, ensuring it captures the essence of cyberpunk - the gritty fusion of high tech and low life, the exploration of human identity in a digitized world, and the palpable tension between corporate power and individual freedom.

Provide your feedback in a clear, structured format. Do not rewrite the chapter or include narrative content in your response."""

# Function to clean YAML string
def clean_yaml_string(yaml_string):
    # Remove any markdown formatting
    yaml_string = re.sub(r'^#+\s+.*$', '', yaml_string, flags=re.MULTILINE)
    yaml_string = re.sub(r'\*\*(.*?)\*\*', r'\1', yaml_string)
    
    # Ensure proper YAML structure
    yaml_string = re.sub(r'^(\w+):\s*$', r'\1: |', yaml_string, flags=re.MULTILINE)
    
    # Remove any remaining non-YAML content
    yaml_lines = []
    for line in yaml_string.split('\n'):
        if ':' in line or line.strip().startswith('-') or not line.strip():
            yaml_lines.append(line)
    
    return '\n'.join(yaml_lines)

# Function to safely parse YAML
def safe_yaml_parse(yaml_string):
    try:
        cleaned_yaml = clean_yaml_string(yaml_string)
        return yaml.safe_load(cleaned_yaml)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        print(f"Problematic YAML string: {cleaned_yaml}")
        return None

# Function to generate characters
def generate_characters(num_characters):
    characters = []
    for i in range(num_characters):
        attempt = 0
        while attempt < 3:
            character_yaml = character_generator(f"Generate character {i+1} for our cyberpunk science fiction novel. Make this character unique and deeply rooted in the cyberpunk genre.")
            character = safe_yaml_parse(character_yaml)
            if character and all(key in character for key in ["name", "age", "occupation", "traits", "background"]):
                characters.append(character)
                break
            else:
                print(f"Retrying character {i+1} generation. Attempt {attempt + 1}")
                attempt += 1
        if attempt == 3:
            print(f"Failed to generate valid character {i+1} after 3 attempts.")
    return characters

# Function to generate story arc
def generate_story_arc(characters):
    character_names = [char["name"] for char in characters]
    story_arc_yaml = story_arc_generator(f"Generate a complex, engaging story arc for our cyberpunk science fiction novel featuring these characters: {', '.join(character_names)}. Ensure the story explores core cyberpunk themes and makes full use of our unique characters. Respond in strict YAML format.")
    
    story_arc = safe_yaml_parse(story_arc_yaml)
    if not story_arc or not all(key in story_arc for key in ["setting", "inciting_incident", "rising_action", "climax", "falling_action", "resolution"]):
        print("Invalid story arc structure. Generating a basic structure.")
        story_arc = {
            "setting": "A sprawling megacity in 2099, where corporate skyscrapers loom over neon-lit streets",
            "inciting_incident": {"description": "A mysterious AI virus begins infecting cybernetic implants", "characters_involved": character_names[:2]},
            "rising_action": [
                {"description": "Characters uncover a corporate conspiracy behind the virus", "characters_involved": character_names},
                {"description": "A powerful AI emerges, claiming to be the cure", "characters_involved": character_names[1:3]}
            ],
            "climax": {"description": "Final confrontation with the AI and corporate leaders", "characters_involved": character_names},
            "falling_action": {"description": "Dealing with the aftermath of the AI conflict", "characters_involved": character_names[:3]},
            "resolution": {"description": "A new world order emerges, blending AI and human governance", "characters_involved": character_names}
        }
    
    return story_arc

# Function to check character consistency
def check_character_consistency(chapter, characters):
    inconsistencies = []
    for character in characters:
        if character['name'] in chapter:
            for trait in character['traits']:
                if trait.lower() not in chapter.lower():
                    inconsistencies.append(f"Character {character['name']} trait '{trait}' not reflected in the chapter.")
            if character['occupation'].lower() not in chapter.lower():
                inconsistencies.append(f"Character {character['name']} occupation '{character['occupation']}' not mentioned in the chapter.")
    return inconsistencies

def is_approval(feedback):
    approval_patterns = [
        r"^APPROVED:",
        r"^This is an? (?:great|excellent|fantastic|amazing|wonderful|superb) revision!",
        r"^This is a .+ revision!",
        r"^This is a well-written chapter",
        r"^The chapter (?:effectively|successfully|excellently) (?:sets up|establishes|presents|portrays)",
        r"^This chapter (?:effectively|successfully|excellently) (?:sets up|establishes|presents|portrays)",
        r"^(?:Overall|In summary), this (?:is an? excellent|is a strong|is a well-crafted) chapter"
    ]
    
    for pattern in approval_patterns:
        if re.match(pattern, feedback, re.IGNORECASE):
            return True
    
    # Check for generally positive sentiment if no explicit approval is found
    positive_words = ['good', 'great', 'excellent', 'well-written', 'effective', 'strong', 'compelling', 'engaging']
    first_sentence = feedback.split('.')[0].lower()
    if any(word in first_sentence for word in positive_words) and 'but' not in first_sentence:
        return True
    
    return False

# Function to write and edit a chapter
def write_and_edit_chapter(chapter_number, event, characters, max_iterations=5):
    character_info = "\n".join([f"{char['name']}: {char['occupation']}, Traits: {', '.join(char['traits'])}" for char in characters])
    
    chapter_content = chapter_writer(f"""Write Chapter {chapter_number} of our cyberpunk novel. 
Event: {yaml.dump(event)}
Characters: 
{character_info}
Remember to vividly depict our cyberpunk world and deeply explore our characters. 
Ensure you incorporate each character's traits and occupation into the narrative.
Focus solely on the narrative content without any meta-commentary or discussion of the writing process.""")
    
    for iteration in range(max_iterations):
        inconsistencies = check_character_consistency(chapter_content, characters)
        if inconsistencies:
            print("Character inconsistencies detected:")
            for inconsistency in inconsistencies:
                print(f"- {inconsistency}")
            chapter_content = chapter_writer(f"Please revise the chapter to address the following character inconsistencies:\n{yaml.dump(inconsistencies)}\n\nOriginal chapter:\n{chapter_content}")
        
        feedback = editor(f"Review the following chapter:\n\n{chapter_content}\n\nProvide specific, actionable feedback for improvement. If the chapter meets high standards, start your response with 'APPROVED:' or a phrase indicating the chapter is well-written or effective, followed by a brief summary of the chapter's strengths. Do not include any narrative content in your response.")
        
        if is_approval(feedback):
            print(f"Chapter {chapter_number} approved after {iteration + 1} iterations.")
            return chapter_content
        
        print(f"Editing iteration {iteration + 1} for Chapter {chapter_number}")
        chapter_content = chapter_writer(f"Revise the following chapter based on this editorial feedback:\n{feedback}\n\nOriginal chapter:\n{chapter_content}")
    
    print(f"Max iterations reached for Chapter {chapter_number}. Using last version.")
    return chapter_content

# Function to generate new rising action events
def generate_new_rising_action(characters, max_attempts=5):
    for attempt in range(max_attempts):
        character_names = [char["name"] for char in characters]
        raw_output = story_arc_generator(f"Generate a new rising action event for our cyberpunk story. Current characters: {', '.join(character_names)}. Respond in strict YAML format.")
        cleaned_output = clean_yaml_string(raw_output)
        
        try:
            new_event = yaml.safe_load(cleaned_output)
            if isinstance(new_event, dict) and "description" in new_event and "characters_involved" in new_event:
                return new_event
        except yaml.YAMLError as e:
            print(f"Error parsing YAML (attempt {attempt + 1}): {e}")
    
    print(f"Failed to generate a valid rising action event after {max_attempts} attempts.")
    return None

# Main function to generate the book
def generate_book(num_characters=5, num_chapters=10):
    print("Generating characters...")
    characters = generate_characters(num_characters)
    
    if not characters:
        print("No valid characters generated. Aborting book generation.")
        return None
    
    print("Generating story arc...")
    story_arc = generate_story_arc(characters)
    
    print("Writing chapters...")
    chapters = []
    chapter_number = 1
    
    def update_progress():
        progress = (chapter_number / num_chapters) * 100
        print(f"Progress: {progress:.2f}% ({chapter_number}/{num_chapters} chapters)")
    
    # Inciting incident
    chapters.append(write_and_edit_chapter(chapter_number, story_arc["inciting_incident"], characters))
    chapter_number += 1
    update_progress()
    
    # Rising action
    for event in story_arc["rising_action"]:
        if chapter_number > num_chapters - 3:
            break
        chapters.append(write_and_edit_chapter(chapter_number, event, characters))
        chapter_number += 1
        update_progress()
    
    # If we haven't reached the desired number of chapters, add more rising action
    while chapter_number <= num_chapters - 3:
        new_event = generate_new_rising_action(characters)
        if new_event:
            chapters.append(write_and_edit_chapter(chapter_number, new_event, characters))
            chapter_number += 1
            update_progress()
        else:
            break
    
    # Climax
    chapters.append(write_and_edit_chapter(chapter_number, story_arc["climax"], characters))
    chapter_number += 1
    update_progress()
    
    # Falling action
    chapters.append(write_and_edit_chapter(chapter_number, story_arc["falling_action"], characters))
    chapter_number += 1
    update_progress()
    
    # Resolution
    chapters.append(write_and_edit_chapter(chapter_number, story_arc["resolution"], characters))
    update_progress()
    
    # Combine chapters into a book
    book = "\n\n".join(chapters)
    
    return book

# Generate the book
book = generate_book()

if book:
    # Save the book to a file
    with open("generated_cyberpunk_novel.txt", "w") as f:
        f.write(book)
    print("Book generation complete. The book has been saved as 'generated_cyberpunk_novel.txt'.")
else:
    print("Book generation failed.")

# Clear contexts
character_generator.clear_context()
story_arc_generator.clear_context()
chapter_writer.clear_context()
editor.clear_context()

print("All node contexts cleared.")
