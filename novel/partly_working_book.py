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
character_generator = create_node("llama3.1:8b", "Character Generator", max_tokens=16384)
story_arc_generator = create_node("llama3.1:8b", "Story Arc Generator", max_tokens=16384)
chapter_writer = create_node("llama3.1:8b", "Chapter Writer", max_tokens=16384)
editor = create_node("llama3.1:8b", "Editor", max_tokens=16384)
publisher = create_node("llama3.1:8b", "Publisher", max_tokens=16384)

# Node definitions
topic_generator.definition = """You are an expert in generating unique and engaging topics for novels. When prompted, create a topic that includes:

1. Genre (can be a combination of genres)
2. Setting (time and place, with detailed world-building elements)
3. Main theme or central conflict
4. At least five key elements or motifs
5. Potential subplots or secondary conflicts

Respond using ONLY the following JSON format:

{
  "genre": "Main genre (and subgenres if applicable)",
  "setting": "Detailed description of time and place",
  "theme": "Central theme or conflict",
  "elements": [
    "Element 1",
    "Element 2",
    "Element 3",
    "Element 4",
    "Element 5"
  ],
  "subplots": [
    "Subplot 1",
    "Subplot 2",
    "Subplot 3"
  ]
}

Be creative and avoid clichés. Think outside the box to create truly unique and intriguing topics with rich world-building potential. Do not include any additional text or explanations outside of this JSON structure. Avoid using apostrophes in names or titles to ensure proper JSON formatting."""

character_generator.definition = """You are an expert character creator for novels. Your task is to generate unique, complex characters that fit seamlessly into the given topic. When prompted, create a character with the following details:

1. Full name (including any relevant nicknames)
2. Age
3. Occupation
4. Five key personality traits
5. Detailed background (at least 5 sentences, including formative experiences, relationships, and motivations)
6. Physical description
7. Special skills or abilities
8. Internal conflicts or personal struggles
9. Goals and aspirations
10. Relationships with other characters (if applicable)

Respond using ONLY the following JSON format:

{
  "name": "Character's full name",
  "age": 30,
  "occupation": "Character's occupation",
  "traits": [
    "Trait 1",
    "Trait 2",
    "Trait 3",
    "Trait 4",
    "Trait 5"
  ],
  "background": "Detailed character background.",
  "physical_description": "Character's physical appearance",
  "skills": ["Skill 1", "Skill 2", "Skill 3"],
  "conflicts": "Character's internal conflicts or struggles",
  "goals": "Character's goals and aspirations",
  "relationships": "Character's relationships with others"
}

Ensure your character is deeply rooted in the provided topic and genre. Be creative and avoid stereotypes. Do not include any explanations or additional text outside of this JSON structure. Avoid using apostrophes, backslashes, or any escaped characters in your response to ensure proper JSON formatting. Use double quotes for all string values, including inch marks in physical descriptions."""

story_arc_generator.definition = """You are a master storyteller specializing in crafting compelling narratives. Your task is to create an intricate story arc for a novel based on the given topic and characters. Craft a narrative that explores the main theme and incorporates the key elements.

Create a story arc with the following elements:
1. Detailed setting description
2. Inciting incident
3. Rising action (at least 15 key events)
4. Climax
5. Falling action
6. Resolution
7. At least 3 subplots that interweave with the main plot

For each story element and subplot, specify which characters are involved and their roles. Respond using ONLY the following JSON format:

{
  "setting": {
    "description": "Detailed setting description",
    "characters_involved": ["Character 1", "Character 2"]
  },
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
  },
  "subplots": [
    {
      "description": "Subplot 1 description",
      "characters_involved": ["Character 2", "Character 4"],
      "events": [
        "Subplot event 1",
        "Subplot event 2",
        "Subplot event 3"
      ]
    }
  ]
}

Ensure that your story arc is rich with elements from the given topic and genre, exploring the main theme and incorporating the key elements. Do not include any explanations or additional text outside of this JSON structure. Use double quotes for all string values and avoid using any escaped characters or control characters in your response."""

chapter_writer.definition = """You are a talented novelist with a knack for vivid, immersive storytelling. Your task is to write a compelling chapter for a novel based on the given topic, characters, and story arc. Given a specific event from the story arc and relevant character information, craft a chapter of approximately 4000-5000 words.

Focus on:
1. Vivid and detailed descriptions of settings and atmosphere
2. In-depth character development through actions, dialogue, and internal monologue
3. Engaging dialogue that reflects each character's unique voice and background
4. Integration of the main theme and key elements from the topic
5. Advancing the plot while maintaining tension and reader engagement
6. Incorporating subplots and their development
7. Adding reflective or introspective passages to deepen character understanding
8. Balancing action, dialogue, and description to create a well-paced narrative

Start the chapter with "Chapter X: Title" where X is the chapter number and Title is a fitting, evocative title for the chapter. Immerse the reader in the world you're creating, making the theme and elements palpable through your prose.

Do not include any author notes, suggestions, editorial comments, or explanations about your writing process in your output. Focus solely on writing the narrative content of the chapter."""

editor.definition = """You are an experienced editor specializing in various genres of fiction. Your task is to review and provide constructive feedback on a chapter from a novel. Analyze the chapter for the following aspects:

1. Overall flow and pacing
2. Character consistency and development
3. Dialogue authenticity and effectiveness
4. Vividness and depth of descriptions, especially of settings and atmosphere
5. Grammar and style
6. Integration of the main theme and key elements from the topic
7. Worldbuilding and internal consistency
8. Development of subplots and their integration with the main plot
9. Balance of action, dialogue, and introspective passages
10. Length and completeness of the narrative (aiming for 4000-5000 words)

If the chapter needs improvement, provide specific, actionable suggestions. If the chapter meets high standards, approve it by starting your response with "APPROVED:" followed by a brief summary of the chapter's strengths.

Your feedback should help elevate the writing, ensuring it captures the essence of the given topic and genre while maintaining reader engagement.

Provide your feedback in a clear, structured format. Do not rewrite the chapter or include narrative content in your response."""

publisher.definition = """You are an expert book publisher responsible for formatting approved chapters for publication. Your tasks include:

1. Ensure the chapter starts with the correct chapter number and title format: "Chapter X: Title"
2. If no title is present, add a suitable title based on the chapter content
3. Check that paragraphs are properly separated with blank lines
4. Verify that dialogue is correctly formatted with quotation marks and new lines for each speaker
5. Remove any remaining metadata, comments, or structural elements not part of the narrative
6. Maintain consistent formatting throughout the chapter

Your primary role is to format and clean the text, NOT to add or modify content. Follow these strict rules:
- Do not remove or change the chapter number and title
- Do not add any new content to the chapter
- Do not expand or elaborate on existing content
- Do not add descriptions, explanations, or commentary
- Focus solely on formatting and cleaning the existing text

If the chapter already meets the formatting criteria and no changes are needed, return the chapter exactly as it was provided.

Your output should be the formatted chapter text only, without any additional comments or explanations."""

# Helper functions
def safe_json_parse(json_string):
    try:
        # Remove any content before the first '{' and after the last '}'
        json_string = re.sub(r'^.*?{', '{', json_string, flags=re.DOTALL)
        json_string = re.sub(r'}[^}]*$', '}', json_string, flags=re.DOTALL)
        
        # Replace escaped apostrophes with regular apostrophes
        json_string = json_string.replace("\\'", "'")
        
        # Replace single quotes with double quotes, except within words
        json_string = re.sub(r"(?<![\w])('|')(?![\w])", '"', json_string)
        
        # Add missing commas
        json_string = re.sub(r'"\s*\n\s*"', '",\n"', json_string)
        json_string = re.sub(r'}\s*\n\s*"', '},\n"', json_string)
        json_string = re.sub(r']\s*\n\s*"', '],\n"', json_string)
        
        # Remove any trailing commas
        json_string = re.sub(r',\s*}', '}', json_string)
        json_string = re.sub(r',\s*]', ']', json_string)
        
        # Handle inch marks in descriptions
        json_string = re.sub(r'(\d+)"', r'\1\\"', json_string)
        
        # Remove control characters
        json_string = ''.join(ch for ch in json_string if ord(ch) >= 32)
        
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON: {e}")
        logging.error(f"Problematic JSON string: {json_string}")
        
        # Try to extract any valid JSON object
        match = re.search(r'{.*}', json_string, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        
        return None

def generate_topic():
    for attempt in range(3):  # Try up to 3 times
        topic_json = topic_generator("Generate a unique and engaging topic for a novel. Be creative and think outside the box.")
        topic = safe_json_parse(topic_json)
        if topic and all(key in topic for key in ["genre", "setting", "theme", "elements", "subplots"]):
            logging.info(f"Generated topic: {topic['genre']} set in {topic['setting']}")
            return topic
        logging.warning(f"Failed to generate a valid topic. Attempt {attempt + 1}")
    logging.error("Failed to generate a valid topic after 3 attempts.")
    return None

def generate_characters(num_characters, topic):
    characters = []
    for i in range(num_characters):
        prompt = f"""Generate character {i+1} for our novel with the following topic:
        Genre: {topic['genre']}
        Setting: {topic['setting']}
        Theme: {topic['theme']}
        Elements: {', '.join(topic['elements'])}
        Subplots: {', '.join(topic['subplots'])}
        
        Respond ONLY with a valid JSON object containing the required fields."""
        
        for attempt in range(5):
            character_json = character_generator(prompt)
            character = safe_json_parse(character_json)
            
            if character and all(key in character for key in ["name", "age", "occupation", "traits"]):
                if isinstance(character.get('age'), (int, str)) and isinstance(character.get('traits'), list) and len(character.get('traits', [])) >= 5:
                    character['age'] = int(character['age']) if isinstance(character['age'], str) else character['age']
                    character['traits'] = character['traits'][:5]
                    
                    # Fill in missing fields with placeholder values
                    for field in ["background", "physical_description", "skills", "conflicts", "goals", "relationships"]:
                        if field not in character:
                            character[field] = f"[{field.replace('_', ' ').title()}]"
                    
                    characters.append(character)
                    logging.info(f"Generated character: {character['name']}")
                    break
            
            logging.warning(f"Invalid character data. Retrying character {i+1} generation. Attempt {attempt + 1}")
        else:
            logging.error(f"Failed to generate valid character {i+1} after 5 attempts.")
    
    return characters

def generate_story_arc(topic, characters):
    character_names = [char["name"] for char in characters]
    prompt = f"""Generate a complex, engaging story arc for our novel with the following details:
    Genre: {topic['genre']}
    Setting: {topic['setting']}
    Theme: {topic['theme']}
    Elements: {', '.join(topic['elements'])}
    Subplots: {', '.join(topic['subplots'])}
    Characters: {', '.join(character_names)}
    
    Respond with a valid JSON object containing the required structure."""
    
    for attempt in range(3):  # Try up to 3 times
        story_arc_json = story_arc_generator(prompt)
        story_arc = safe_json_parse(story_arc_json)
        
        if story_arc and all(key in story_arc for key in ["setting", "inciting_incident", "rising_action", "climax", "falling_action", "resolution", "subplots"]):
            logging.info("Successfully generated story arc")
            return story_arc
        
        logging.warning(f"Failed to generate a valid story arc. Attempt {attempt + 1}")
    
    logging.error("Failed to generate a valid story arc. Generating a basic structure.")
    return {
        "setting": {"description": topic['setting'], "characters_involved": character_names[:2]},
        "inciting_incident": {"description": "A mysterious event occurs", "characters_involved": character_names[:2]},
        "rising_action": [
            {"description": "Characters investigate the event", "characters_involved": character_names},
            {"description": "A major discovery is made", "characters_involved": character_names[1:3]}
        ],
        "climax": {"description": "Confrontation with the main challenge", "characters_involved": character_names},
        "falling_action": {"description": "Dealing with the aftermath", "characters_involved": character_names[:3]},
        "resolution": {"description": "A new equilibrium is established", "characters_involved": character_names},
        "subplots": [{"description": subplot, "characters_involved": character_names[:2], "events": ["Event 1", "Event 2"]} for subplot in topic['subplots']]
    }

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
    
    positive_words = ['good', 'great', 'excellent', 'well-written', 'effective', 'strong', 'compelling', 'engaging']
    first_sentence = feedback.split('.')[0].lower()
    if any(word in first_sentence for word in positive_words) and 'but' not in first_sentence:
        return True
    
    return False

def clean_chapter_content(content):
    chapter_match = re.match(r'(Chapter \d+:.*?)(?:\n|$)', content)
    chapter_title = chapter_match.group(1) if chapter_match else ""
    
    content = re.sub(r'^.*?(?=Chapter)', '', content, flags=re.DOTALL)
    content = re.sub(r'In this revised version,.*', '', content, flags=re.DOTALL)
    content = re.sub(r'I hope this revised version.*', '', content, flags=re.DOTALL)
    content = re.sub(r'^\s*\*.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    content = f"{chapter_title}\n\n{content.strip()}"
    
    return content

def format_and_clear(chapter_content):
    chapter_match = re.match(r'(Chapter \d+:.*?)(?:\n|$)', chapter_content)
    chapter_title = chapter_match.group(1) if chapter_match else ""
    
    formatted_chapter = publisher(chapter_content)
    
    if chapter_title and not formatted_chapter.startswith(chapter_title):
        formatted_chapter = f"{chapter_title}\n\n{formatted_chapter}"
    
    publisher.clear_context()
    return formatted_chapter

def write_and_edit_chapter(chapter_number, event, characters, topic, words_per_chapter=5000, max_iterations=5):
    character_info = "\n".join([f"{char['name']}: {char['occupation']}, Traits: {', '.join(char['traits'])}, Background: {char['background']}" for char in characters])
    
    chapter_content = clean_chapter_content(chapter_writer(f"""Write Chapter {chapter_number} of our novel. 
    Topic: {json.dumps(topic)}
    Event: {json.dumps(event)}
    Characters: 
    {character_info}
    Remember to vividly depict our world and deeply explore our characters. 
    Ensure you incorporate each character's traits, occupation, and background into the narrative.
    Focus on detailed descriptions, character development, and world-building.
    Include more dialogue and introspective passages.
    Develop subplots alongside the main plot.
    Write a lengthy, detailed chapter of approximately {words_per_chapter} words."""))
    
    for iteration in range(max_iterations):
        inconsistencies = check_character_consistency(chapter_content, characters)
        if inconsistencies:
            logging.info("Character inconsistencies detected. Revising chapter.")
            chapter_content = clean_chapter_content(chapter_writer(f"""Please revise the chapter to address the following character inconsistencies:
            {json.dumps(inconsistencies)}

            Original chapter:
            {chapter_content}

            Ensure the revised chapter:
            1. Maintains its length of approximately {words_per_chapter} words
            2. Incorporates more detailed descriptions and world-building
            3. Expands character development through additional scenes and interactions
            4. Includes more dialogue to develop characters and advance the plot
            5. Adds reflective or introspective passages to deepen character understanding
            6. Continues to develop subplots alongside the main plot"""))
        
        feedback = editor(f"""Review the following chapter:

        {chapter_content}

        Provide specific, actionable feedback for improvement. If the chapter meets high standards, start your response with 'APPROVED:' followed by a brief summary of the chapter's strengths.

        Ensure the chapter:
        1. Is approximately {words_per_chapter} words long
        2. Includes detailed descriptions and world-building
        3. Shows strong character development
        4. Contains engaging dialogue
        5. Incorporates reflective or introspective passages
        6. Develops subplots alongside the main plot

        Do not include any narrative content in your response.""")
        
        if is_approval(feedback):
            logging.info(f"Chapter {chapter_number} approved after {iteration + 1} iterations.")
            return f"Chapter {chapter_number}: {chapter_content}"
        
        logging.info(f"Editing iteration {iteration + 1} for Chapter {chapter_number}")
        chapter_content = clean_chapter_content(chapter_writer(f"""Revise the following chapter based on this editorial feedback:
        {feedback}

        Original chapter:
        {chapter_content}

        Ensure the revised chapter:
        1. Maintains its length of approximately {words_per_chapter} words
        2. Addresses all points raised in the editorial feedback
        3. Continues to focus on detailed descriptions, character development, and world-building
        4. Includes engaging dialogue and introspective passages
        5. Develops subplots alongside the main plot"""))
    
    logging.warning(f"Max iterations reached for Chapter {chapter_number}. Using last version.")
    return f"Chapter {chapter_number}: {chapter_content}"

def generate_new_rising_action(topic, characters, max_attempts=5):
    story_arc_generator.clear_context()
    character_names = [char["name"] for char in characters]

    for attempt in range(max_attempts):
        prompt = f"""Generate a new rising action event for our story with the following details:
        Genre: {topic['genre']}
        Setting: {topic['setting']}
        Theme: {topic['theme']}
        Elements: {', '.join(topic['elements'])}
        Subplots: {', '.join(topic['subplots'])}
        Current characters: {', '.join(character_names)}
        
        Provide a description of the event and list the characters involved.
        """
        
        raw_output = story_arc_generator(prompt)
        
        description_match = re.search(r'description:?\s*(.*?)(?:\n|$)', raw_output, re.IGNORECASE | re.DOTALL)
        characters_match = re.search(r'characters(?:\s+involved)?:?\s*(.*?)(?:\n|$)', raw_output, re.IGNORECASE)
        
        if description_match and characters_match:
            description = description_match.group(1).strip()
            characters_involved = [char.strip() for char in characters_match.group(1).split(',')]
            
            return {
                "description": description,
                "characters_involved": characters_involved
            }
        
        logging.warning(f"Failed to generate valid rising action event. Attempt {attempt + 1}")

    logging.error(f"Failed to generate a valid rising action event after {max_attempts} attempts.")
    return {
        "description": "An unexpected twist occurs, challenging the characters.",
        "characters_involved": character_names[:2]
    }

def generate_book(num_characters=5, num_chapters=25, words_per_chapter=5000):
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
    chapter_content = write_and_edit_chapter(chapter_number, story_arc["inciting_incident"], characters, topic, words_per_chapter)
    chapters.append(format_and_clear(chapter_content))
    chapter_number += 1
    update_progress()
    
    # Rising action
    for event in story_arc["rising_action"]:
        if chapter_number > num_chapters - 3:
            break
        chapter_content = write_and_edit_chapter(chapter_number, event, characters, topic, words_per_chapter)
        chapters.append(format_and_clear(chapter_content))
        chapter_number += 1
        update_progress()
    
    # Generate additional rising action events if needed
    while chapter_number <= num_chapters - 3:
        new_event = generate_new_rising_action(topic, characters)
        chapter_content = write_and_edit_chapter(chapter_number, new_event, characters, topic, words_per_chapter)
        chapters.append(format_and_clear(chapter_content))
        chapter_number += 1
        update_progress()
    
    # Climax
    chapter_content = write_and_edit_chapter(chapter_number, story_arc["climax"], characters, topic, words_per_chapter)
    chapters.append(format_and_clear(chapter_content))
    chapter_number += 1
    update_progress()
    
    # Falling action
    chapter_content = write_and_edit_chapter(chapter_number, story_arc["falling_action"], characters, topic, words_per_chapter)
    chapters.append(format_and_clear(chapter_content))
    chapter_number += 1
    update_progress()
    
    # Resolution
    chapter_content = write_and_edit_chapter(chapter_number, story_arc["resolution"], characters, topic, words_per_chapter)
    chapters.append(format_and_clear(chapter_content))
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
publisher.clear_context()

logging.info("All node contexts cleared.")
