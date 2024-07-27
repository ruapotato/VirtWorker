import logging
import random
import json
import re
import time
from virtworker import create_node

# Set logging level to INFO to see all output
logging.getLogger().setLevel(logging.INFO)

# Create nodes
topic_generator = create_node("llama3.1:8b", "Topic Generator")
character_generator = create_node("llama3.1:8b", "Character Generator")
story_arc_generator = create_node("llama3.1:8b", "Story Arc Generator")
chapter_writer = create_node("llama3.1:8b", "Chapter Writer")
editor = create_node("llama3.1:8b", "Editor")

# Node definitions
topic_generator.definition = """You are an expert in generating unique and engaging topics for novels. When prompted, create a topic that includes:

1. Genre (can be a combination of genres)
2. Setting (time and place)
3. Main theme or central conflict
4. Two to three key elements or motifs

Respond using ONLY the following JSON format:

{
  "genre": "Main genre (and subgenres if applicable)",
  "setting": "Time and place",
  "theme": "Central theme or conflict",
  "elements": [
    "Element 1",
    "Element 2",
    "Element 3"
  ]
}

Be creative and avoid clichés. Think outside the box to create truly unique and intriguing topics. Do not include any additional text or explanations outside of this JSON structure."""

character_generator.definition = """You are an expert character creator for novels. Your task is to generate unique, complex characters that fit seamlessly into the given topic. When prompted, create a character with the following details:

1. Full name (including any relevant nicknames)
2. Age
3. Occupation
4. Three key personality traits
5. Brief background (2-3 sentences, including any special abilities or notable experiences)

Respond using ONLY the following JSON format:

{
  "name": "Character's full name",
  "age": 30,
  "occupation": "Character's occupation",
  "traits": [
    "Trait 1",
    "Trait 2",
    "Trait 3"
  ],
  "background": "Character's background."
}

Ensure your character is deeply rooted in the provided topic and genre. Be creative and avoid stereotypes. Do not include any explanations or additional text outside of this JSON structure."""

story_arc_generator.definition = """You are a master storyteller specializing in crafting compelling narratives. Your task is to create an intricate story arc for a novel based on the given topic and characters. Craft a narrative that explores the main theme and incorporates the key elements.

Create a story arc with the following elements:
1. Inciting incident
2. Rising action (3-5 key events)
3. Climax
4. Falling action
5. Resolution

For each story element, specify which characters are involved and their roles. Respond using ONLY the following JSON format:

{
  "inciting_incident": {
    "description": "Description of the incident",
    "characters_involved": ["Character 1", "Character 2"]
  },
  "rising_action": [
    {
      "description": "Event 1 description",
      "characters_involved": ["Character 1", "Character 3"]
    },
    {
      "description": "Event 2 description",
      "characters_involved": ["Character 2", "Character 4"]
    }
  ],
  "climax": {
    "description": "Description of the climax",
    "characters_involved": ["Character 1", "Character 2", "Character 3"]
  },
  "falling_action": {
    "description": "Description of falling action",
    "characters_involved": ["Character 1", "Character 2"]
  },
  "resolution": {
    "description": "Description of the resolution",
    "characters_involved": ["Character 1", "Character 2", "Character 3"]
  }
}

Ensure that your story arc is rich with elements from the given topic and genre, exploring the main theme and incorporating the key elements. Do not include any explanations or additional text outside of this JSON structure."""

chapter_writer.definition = """You are a talented novelist with a knack for vivid, immersive storytelling. Your task is to write a compelling chapter for a novel based on the given topic, characters, and story arc. Given a specific event from the story arc and relevant character information, craft a chapter of approximately 2500-3000 words.

Focus on:
1. Vivid descriptions of the setting and atmosphere
2. Engaging dialogue that reflects each character's unique voice and background
3. Character development, showcasing how they navigate and are changed by the events
4. Integration of the main theme and key elements from the topic
5. Advancing the plot while maintaining tension and reader engagement

Start the chapter with "Chapter X: Title" where X is the chapter number and Title is a fitting, evocative title for the chapter. Immerse the reader in the world you're creating, making the theme and elements palpable through your prose.

Do not include any author notes, suggestions, or editorial comments in your output. Focus solely on writing the narrative content of the chapter."""

editor.definition = """You are an experienced editor specializing in various genres of fiction. Your task is to review and provide constructive feedback on a chapter from a novel. Analyze the chapter for the following aspects:

1. Overall flow and pacing
2. Character consistency and development
3. Dialogue authenticity and effectiveness
4. Vividness and depth of descriptions
5. Grammar and style
6. Integration of the main theme and key elements from the topic
7. Worldbuilding and internal consistency
8. Length and completeness of the narrative (aiming for 2500-3000 words)

If the chapter needs improvement, provide specific, actionable suggestions. If the chapter meets high standards, approve it by starting your response with "APPROVED:" followed by a brief summary of the chapter's strengths.

Your feedback should help elevate the writing, ensuring it captures the essence of the given topic and genre while maintaining reader engagement.

Provide your feedback in a clear, structured format. Do not rewrite the chapter or include narrative content in your response."""

# Function to safely parse JSON
def safe_json_parse(json_string):
    try:
        # Remove any content before the first '{'
        json_string = re.sub(r'^.*?{', '{', json_string, flags=re.DOTALL)
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON: {e}")
        logging.error(f"Problematic JSON string: {json_string}")
        return None

# Function to generate topic
def generate_topic():
    topic_json = topic_generator("Generate a unique and engaging topic for a novel. Be creative and think outside the box.")
    topic = safe_json_parse(topic_json)
    if topic and all(key in topic for key in ["genre", "setting", "theme", "elements"]):
        logging.info(f"Generated topic: {topic['genre']} set in {topic['setting']}")
        return topic
    logging.error("Failed to generate a valid topic.")
    return None

# Function to generate characters
def generate_characters(num_characters, topic):
    characters = []
    for i in range(num_characters):
        attempt = 0
        while attempt < 5:  # Increase max attempts to 5
            prompt = f"""Generate character {i+1} for our novel with the following topic:
            Genre: {topic['genre']}
            Setting: {topic['setting']}
            Theme: {topic['theme']}
            Elements: {', '.join(topic['elements'])}
            Make this character unique and deeply rooted in the given topic and genre. Respond ONLY with the JSON structure, no additional text."""
            
            character_json = character_generator(prompt)
            character = safe_json_parse(character_json)
            
            if character and all(key in character for key in ["name", "age", "occupation", "traits", "background"]):
                if isinstance(character['age'], (int, str)) and isinstance(character['traits'], list) and len(character['traits']) >= 2:
                    # Convert age to int if it's a string
                    if isinstance(character['age'], str):
                        try:
                            character['age'] = int(character['age'])
                        except ValueError:
                            character['age'] = 0  # Default age if conversion fails
                    
                    # Ensure we have exactly 3 traits
                    while len(character['traits']) < 3:
                        character['traits'].append("Mysterious")
                    character['traits'] = character['traits'][:3]
                    
                    characters.append(character)
                    logging.info(f"Generated character: {character['name']}")
                    break
            
            logging.warning(f"Invalid character data. Retrying character {i+1} generation. Attempt {attempt + 1}")
            attempt += 1
        
        if attempt == 5:
            logging.error(f"Failed to generate valid character {i+1} after 5 attempts.")
    
    return characters
# Function to generate story arc
def generate_story_arc(topic, characters):
    character_names = [char["name"] for char in characters]
    story_arc_json = story_arc_generator(f"""Generate a complex, engaging story arc for our novel with the following details:
    Genre: {topic['genre']}
    Setting: {topic['setting']}
    Theme: {topic['theme']}
    Elements: {', '.join(topic['elements'])}
    Characters: {', '.join(character_names)}
    Ensure the story explores the main theme and incorporates the key elements. Make full use of our unique characters.""")
    
    story_arc = safe_json_parse(story_arc_json)
    if story_arc and all(key in story_arc for key in ["inciting_incident", "rising_action", "climax", "falling_action", "resolution"]):
        logging.info("Successfully generated story arc")
        return story_arc
    logging.error("Failed to generate a valid story arc. Generating a basic structure.")
    return {
        "inciting_incident": {"description": "A mysterious event occurs", "characters_involved": character_names[:2]},
        "rising_action": [
            {"description": "Characters investigate the event", "characters_involved": character_names},
            {"description": "A major discovery is made", "characters_involved": character_names[1:3]}
        ],
        "climax": {"description": "Confrontation with the main challenge", "characters_involved": character_names},
        "falling_action": {"description": "Dealing with the aftermath", "characters_involved": character_names[:3]},
        "resolution": {"description": "A new equilibrium is established", "characters_involved": character_names}
    }

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
def write_and_edit_chapter(chapter_number, event, characters, topic, max_iterations=5):
    character_info = "\n".join([f"{char['name']}: {char['occupation']}, Traits: {', '.join(char['traits'])}" for char in characters])
    
    chapter_content = chapter_writer(f"""Write Chapter {chapter_number} of our novel. 
Topic: {json.dumps(topic)}
Event: {json.dumps(event)}
Characters: 
{character_info}
Remember to vividly depict our world and deeply explore our characters. 
Ensure you incorporate each character's traits and occupation into the narrative.
Focus solely on the narrative content without any meta-commentary or discussion of the writing process.
Write a lengthy, detailed chapter of approximately 2500-3000 words.""")
    
    for iteration in range(max_iterations):
        inconsistencies = check_character_consistency(chapter_content, characters)
        if inconsistencies:
            logging.info("Character inconsistencies detected. Revising chapter.")
            chapter_content = chapter_writer(f"Please revise the chapter to address the following character inconsistencies:\n{json.dumps(inconsistencies)}\n\nOriginal chapter:\n{chapter_content}\nEnsure the revised chapter maintains its length of approximately 2500-3000 words.")
        
        feedback = editor(f"Review the following chapter:\n\n{chapter_content}\n\nProvide specific, actionable feedback for improvement. If the chapter meets high standards, start your response with 'APPROVED:' or a phrase indicating the chapter is well-written or effective, followed by a brief summary of the chapter's strengths. Ensure the chapter is approximately 2500-3000 words long. Do not include any narrative content in your response.")
        
        if is_approval(feedback):
            logging.info(f"Chapter {chapter_number} approved after {iteration + 1} iterations.")
            return chapter_content
        
        logging.info(f"Editing iteration {iteration + 1} for Chapter {chapter_number}")
        chapter_content = chapter_writer(f"Revise the following chapter based on this editorial feedback:\n{feedback}\n\nOriginal chapter:\n{chapter_content}\nEnsure the revised chapter maintains its length of approximately 2500-3000 words.")
    
    logging.warning(f"Max iterations reached for Chapter {chapter_number}. Using last version.")
    return chapter_content

# Function to generate new rising action events
def generate_new_rising_action(topic, characters, max_attempts=5):
    for attempt in range(max_attempts):
        character_names = [char["name"] for char in characters]
        prompt = f"""Generate a new rising action event for our story with the following details:
        Genre: {topic['genre']}
        Setting: {topic['setting']}
        Theme: {topic['theme']}
        Elements: {', '.join(topic['elements'])}
        Current characters: {', '.join(character_names)}
        Respond in strict JSON format with the following structure:
        {{
            "description": "Event description",
            "characters_involved": ["Character 1", "Character 2"]
        }}"""
        
        raw_output = story_arc_generator(prompt)
        new_event = safe_json_parse(raw_output)
        
        if isinstance(new_event, dict) and "description" in new_event and "characters_involved" in new_event:
            return new_event
        
        logging.warning(f"Failed to generate valid rising action event. Attempt {attempt + 1}")
    
    logging.error(f"Failed to generate a valid rising action event after {max_attempts} attempts.")
    # Return a default event if generation fails
    return {
        "description": "An unexpected twist occurs, challenging the characters.",
        "characters_involved": character_names[:2]
    }

# Main function to generate the book
def generate_book(num_characters=5, num_chapters=10):
    logging.info("Generating topic...")
    topic = generate_topic()
    if not topic:
        logging.error("Failed to generate a valid topic. Aborting book generation.")
        return None

    logging.info("Generating characters...")
    characters = generate_characters(num_characters, topic)
    
    if not characters:
        logging.error("No valid characters generated. Aborting book generation.")
        return None
    
    logging.info("Generating story arc...")
    story_arc = generate_story_arc(topic, characters)
    
    logging.info("Writing chapters...")
    chapters = []
    chapter_number = 1
    
    def update_progress():
        progress = (chapter_number / num_chapters) * 100
        logging.info(f"Progress: {progress:.2f}% ({chapter_number}/{num_chapters} chapters)")
    
    # Inciting incident
    chapters.append(write_and_edit_chapter(chapter_number, story_arc["inciting_incident"], characters, topic))
    chapter_number += 1
    update_progress()
    
    # Rising action
    for event in story_arc["rising_action"]:
        if chapter_number > num_chapters - 3:
            break
        chapters.append(write_and_edit_chapter(chapter_number, event, characters, topic))
        chapter_number += 1
        update_progress()
    
    # Generate additional rising action events if needed
    while chapter_number <= num_chapters - 3:
        new_event = generate_new_rising_action(topic, characters)
        chapters.append(write_and_edit_chapter(chapter_number, new_event, characters, topic))
        chapter_number += 1
        update_progress()
    
    # Climax
    chapters.append(write_and_edit_chapter(chapter_number, story_arc["climax"], characters, topic))
    chapter_number += 1
    update_progress()
    
    # Falling action
    chapters.append(write_and_edit_chapter(chapter_number, story_arc["falling_action"], characters, topic))
    chapter_number += 1
    update_progress()
    
    # Resolution
    chapters.append(write_and_edit_chapter(chapter_number, story_arc["resolution"], characters, topic))
    update_progress()
    
    # Combine chapters into a book
    book = "\n\n".join(chapters)
    
    return book

# Generate the book
logging.info("Starting book generation...")
book = generate_book()

if book:
    # Save the book to a file
    filename = f"generated_novel_{int(time.time())}.txt"
    with open(filename, "w") as f:
        f.write(book)
    logging.info(f"Book generation complete. The book has been saved as '{filename}'.")
else:
    logging.error("Book generation failed.")

# Clear contexts
topic_generator.clear_context()
character_generator.clear_context()
story_arc_generator.clear_context()
chapter_writer.clear_context()
editor.clear_context()

logging.info("All node contexts cleared.")
